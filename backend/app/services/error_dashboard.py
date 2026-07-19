"""Error dashboard — provides error analytics and retry controls.

Aggregates publish failures, identifies patterns, and surfaces
actionable insights for debugging publish issues.
"""
import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Post
from app.models.post_platform import PostPlatform

logger = logging.getLogger(__name__)


async def get_error_summary(
    db: AsyncSession,
    workspace_id: str,
    days: int = 30,
) -> dict[str, Any]:
    """Get a summary of publish errors over the given period.

    Returns:
    {
        "total_attempts": int,
        "total_failures": int,
        "failure_rate": float,
        "by_platform": {
            "linkedin": {"attempts": 10, "failures": 1, "rate": 0.1},
            ...
        },
        "by_error_type": [
            {"error": "Token expired", "count": 5, "platforms": ["linkedin"]},
            ...
        ],
        "recent_failures": [...],
        "retry_stats": {"retried": 8, "recovered": 5, "permanently_failed": 3},
    }
    """
    cutoff = datetime.utcnow() - timedelta(days=days)

    # Get all PostPlatform entries in the period
    result = await db.execute(
        select(PostPlatform).where(
            PostPlatform.workspace_id == workspace_id,
            PostPlatform.created_at >= cutoff,
        )
    )
    all_entries = result.scalars().all()

    total_attempts = len(all_entries)
    failures = [e for e in all_entries if e.status == "failed"]
    total_failures = len(failures)
    failure_rate = (total_failures / total_attempts * 100) if total_attempts > 0 else 0

    # By platform
    by_platform: dict[str, dict[str, Any]] = {}
    for entry in all_entries:
        p = entry.platform
        if p not in by_platform:
            by_platform[p] = {"attempts": 0, "failures": 0, "rate": 0}
        by_platform[p]["attempts"] += 1
        if entry.status == "failed":
            by_platform[p]["failures"] += 1
    for p in by_platform:
        a = by_platform[p]["attempts"]
        f = by_platform[p]["failures"]
        by_platform[p]["rate"] = round(f / a * 100, 1) if a > 0 else 0

    # By error type (group similar errors)
    error_groups: dict[str, dict[str, Any]] = {}
    for entry in failures:
        error_msg = entry.error_message or "Unknown error"
        # Simplify error message for grouping
        simplified = _simplify_error(error_msg)
        if simplified not in error_groups:
            error_groups[simplified] = {"error": simplified, "count": 0, "platforms": set()}
        error_groups[simplified]["count"] += 1
        error_groups[simplified]["platforms"].add(entry.platform)

    by_error_type = sorted(
        [
            {"error": v["error"], "count": v["count"], "platforms": list(v["platforms"])}
            for v in error_groups.values()
        ],
        key=lambda x: x["count"],
        reverse=True,
    )

    # Recent failures (last 10)
    recent_failures = []
    for entry in sorted(failures, key=lambda e: e.created_at or datetime.min, reverse=True)[:10]:
        recent_failures.append({
            "id": entry.id,
            "post_id": entry.post_id,
            "platform": entry.platform,
            "error": entry.error_message,
            "retry_count": entry.retry_count or 0,
            "max_retries": entry.max_retries or 3,
            "created_at": entry.created_at.isoformat() if entry.created_at else None,
            "scheduled_at": entry.scheduled_at.isoformat() if entry.scheduled_at else None,
        })

    # Retry stats
    retried = [e for e in all_entries if (e.retry_count or 0) > 0]
    recovered = [e for e in retried if e.status == "published"]
    permanently_failed = [e for e in failures if (e.retry_count or 0) >= (e.max_retries or 3)]

    return {
        "period_days": days,
        "total_attempts": total_attempts,
        "total_failures": total_failures,
        "failure_rate": round(failure_rate, 1),
        "by_platform": by_platform,
        "by_error_type": by_error_type,
        "recent_failures": recent_failures,
        "retry_stats": {
            "retried": len(retried),
            "recovered": len(recovered),
            "permanently_failed": len(permanently_failed),
        },
    }


async def get_publish_stats(
    db: AsyncSession,
    workspace_id: str,
    days: int = 30,
) -> dict[str, Any]:
    """Get overall publish statistics for the dashboard."""
    cutoff = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(
            PostPlatform.status,
            func.count(PostPlatform.id),
        ).where(
            PostPlatform.workspace_id == workspace_id,
            PostPlatform.created_at >= cutoff,
        ).group_by(PostPlatform.status)
    )
    status_counts = {row[0]: row[1] for row in result.all()}

    total = sum(status_counts.values())
    published = status_counts.get("published", 0)
    failed = status_counts.get("failed", 0)
    scheduled = status_counts.get("scheduled", 0)
    publishing = status_counts.get("publishing", 0)

    return {
        "period_days": days,
        "total": total,
        "by_status": status_counts,
        "success_rate": round((published / total * 100) if total > 0 else 0, 1),
        "published": published,
        "failed": failed,
        "scheduled": scheduled,
        "publishing": publishing,
    }


async def bulk_retry_failed(
    db: AsyncSession,
    workspace_id: str,
    platform: str | None = None,
) -> dict[str, Any]:
    """Reset all failed items to 'scheduled' for retry."""
    query = select(PostPlatform).where(
        PostPlatform.workspace_id == workspace_id,
        PostPlatform.status == "failed",
    )
    if platform:
        query = query.where(PostPlatform.platform == platform)

    result = await db.execute(query)
    failed_items = result.scalars().all()

    reset_count = 0
    for item in failed_items:
        item.status = "scheduled"
        item.error_message = None
        item.retry_count = 0
        item.scheduled_at = datetime.utcnow()
        reset_count += 1

    await db.flush()

    return {
        "reset_count": reset_count,
        "platform": platform,
    }


def _simplify_error(error_msg: str) -> str:
    """Simplify error messages for grouping."""
    msg_lower = error_msg.lower()
    if "token" in msg_lower and ("expire" in msg_lower or "invalid" in msg_lower):
        return "Token expired/invalid"
    elif "rate limit" in msg_lower or "429" in msg_lower:
        return "Rate limited"
    elif "timeout" in msg_lower:
        return "API timeout"
    elif "permission" in msg_lower or "403" in msg_lower:
        return "Permission denied"
    elif "not found" in msg_lower or "404" in msg_lower:
        return "Resource not found"
    elif "caption" in msg_lower or "content" in msg_lower:
        return "Content validation error"
    elif "media" in msg_lower or "upload" in msg_lower:
        return "Media upload error"
    else:
        # Return first 80 chars
        return error_msg[:80] if error_msg else "Unknown error"
