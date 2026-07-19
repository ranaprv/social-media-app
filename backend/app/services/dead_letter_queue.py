"""Dead-letter queue — manages failed publishes with full retry history.

Tracks every failed publish attempt with error details, timestamps,
and retry metadata. Supports manual retry, bulk retry, and analysis.
"""
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post_platform import PostPlatform

logger = logging.getLogger(__name__)


async def get_dead_letter_queue(
    db: AsyncSession,
    workspace_id: str,
    platform: str | None = None,
    error_category: str | None = None,
    offset: int = 0,
    limit: int = 50,
) -> dict[str, Any]:
    """Get failed publishes with full error context.

    Returns detailed failure information including error patterns,
    retry history, and suggested actions.
    """
    query = select(PostPlatform).where(
        PostPlatform.workspace_id == workspace_id,
        PostPlatform.status == "failed",
    )

    if platform:
        query = query.where(PostPlatform.platform == platform)

    # Count total
    count_query = select(func.count(PostPlatform.id)).where(
        PostPlatform.workspace_id == workspace_id,
        PostPlatform.status == "failed",
    )
    if platform:
        count_query = count_query.where(PostPlatform.platform == platform)

    total = (await db.execute(count_query)).scalar() or 0

    # Fetch items
    query = query.order_by(PostPlatform.updated_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()

    # Enrich with error analysis
    queue_items = []
    for item in items:
        error_msg = item.error_message or "Unknown error"
        category = _categorize_error(error_msg)
        suggestion = _get_retry_suggestion(category, item.retry_count or 0, item.max_retries or 3)

        queue_items.append({
            "id": item.id,
            "post_id": item.post_id,
            "platform": item.platform,
            "error": error_msg,
            "error_category": category,
            "retry_suggestion": suggestion,
            "retry_count": item.retry_count or 0,
            "max_retries": item.max_retries or 3,
            "last_attempt": item.updated_at.isoformat() if item.updated_at else None,
            "scheduled_at": item.scheduled_at.isoformat() if item.scheduled_at else None,
            "created_at": item.created_at.isoformat() if item.created_at else None,
        })

    return {
        "items": queue_items,
        "total": total,
        "offset": offset,
        "limit": limit,
        "by_category": await _count_by_category(db, workspace_id),
    }


async def retry_from_dead_letter(
    db: AsyncSession,
    workspace_id: str,
    item_id: str,
    reset_retries: bool = False,
) -> dict[str, Any]:
    """Move a failed item back to the scheduled queue for retry."""
    result = await db.execute(
        select(PostPlatform).where(
            PostPlatform.id == item_id,
            PostPlatform.workspace_id == workspace_id,
            PostPlatform.status == "failed",
        )
    )
    item = result.scalar_one_none()
    if not item:
        return {"error": "Item not found or not in failed state"}

    item.status = "scheduled"
    item.error_message = None
    item.scheduled_at = datetime.utcnow()  # Schedule for immediate retry
    if reset_retries:
        item.retry_count = 0

    await db.flush()

    return {
        "id": item_id,
        "platform": item.platform,
        "message": "Moved to scheduled queue",
        "scheduled_at": item.scheduled_at.isoformat(),
    }


async def bulk_retry_dead_letter(
    db: AsyncSession,
    workspace_id: str,
    platform: str | None = None,
    error_category: str | None = None,
    max_age_days: int = 7,
) -> dict[str, Any]:
    """Bulk retry multiple failed items at once."""
    cutoff = datetime.utcnow() - timedelta(days=max_age_days)

    query = select(PostPlatform).where(
        PostPlatform.workspace_id == workspace_id,
        PostPlatform.status == "failed",
        PostPlatform.updated_at >= cutoff,
    )
    if platform:
        query = query.where(PostPlatform.platform == platform)

    result = await db.execute(query)
    items = result.scalars().all()

    retried = 0
    skipped = 0
    for item in items:
        if error_category:
            item_category = _categorize_error(item.error_message or "")
            if item_category != error_category:
                skipped += 1
                continue

        item.status = "scheduled"
        item.error_message = None
        item.scheduled_at = datetime.utcnow()
        retried += 1

    await db.flush()

    return {
        "retried": retried,
        "skipped": skipped,
        "total_found": len(items),
    }


async def get_error_analytics(
    db: AsyncSession,
    workspace_id: str,
    days: int = 30,
) -> dict[str, Any]:
    """Detailed error analytics for the dead-letter queue."""
    cutoff = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(PostPlatform).where(
            PostPlatform.workspace_id == workspace_id,
            PostPlatform.status == "failed",
            PostPlatform.updated_at >= cutoff,
        )
    )
    items = result.scalars().all()

    # Error frequency
    error_freq: dict[str, int] = {}
    category_freq: dict[str, int] = {}
    platform_errors: dict[str, int] = {}
    hourly_distribution: dict[int, int] = {}

    for item in items:
        error_msg = (item.error_message or "Unknown")[:100]
        error_freq[error_msg] = error_freq.get(error_msg, 0) + 1
        category = _categorize_error(item.error_message or "")
        category_freq[category] = category_freq.get(category, 0) + 1
        platform_errors[item.platform] = platform_errors.get(item.platform, 0) + 1
        if item.updated_at:
            hourly_distribution[item.updated_at.hour] = hourly_distribution.get(item.updated_at.hour, 0) + 1

    # Top errors
    top_errors = sorted(error_freq.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "period_days": days,
        "total_failures": len(items),
        "by_category": category_freq,
        "by_platform": platform_errors,
        "top_errors": [{"error": e, "count": c} for e, c in top_errors],
        "hourly_distribution": hourly_distribution,
        "retry_success_rate": await _calc_retry_success_rate(db, workspace_id),
    }


def _categorize_error(error_msg: str) -> str:
    """Categorize an error message into a known category."""
    msg = error_msg.lower()
    if "token" in msg and ("expire" in msg or "invalid" in msg or "401" in msg):
        return "auth_error"
    elif "rate limit" in msg or "429" in msg or "too many" in msg:
        return "rate_limit"
    elif "timeout" in msg:
        return "timeout"
    elif "permission" in msg or "403" in msg or "forbidden" in msg:
        return "permission_error"
    elif "not found" in msg or "404" in msg:
        return "not_found"
    elif "caption" in msg or "content" in msg or "validation" in msg:
        return "content_error"
    elif "media" in msg or "upload" in msg or "file" in msg:
        return "media_error"
    elif "network" in msg or "connection" in msg or "dns" in msg:
        return "network_error"
    elif "quota" in msg or "limit reached" in msg:
        return "quota_exceeded"
    else:
        return "unknown"


def _get_retry_suggestion(category: str, retry_count: int, max_retries: int) -> str:
    """Get a human-readable retry suggestion based on error category."""
    if retry_count >= max_retries:
        return "Max retries reached. Manual intervention required."

    suggestions = {
        "auth_error": "Token needs refresh. Check platform connection settings.",
        "rate_limit": "Wait before retrying. Rate limits typically reset in 1-15 minutes.",
        "timeout": "Safe to retry. The platform API may have been temporarily slow.",
        "permission_error": "Check app permissions on the platform. Some permissions require app review.",
        "not_found": "Verify the target resource (page, account) still exists.",
        "content_error": "Fix the content issue (caption too long, invalid characters) before retrying.",
        "media_error": "Check media file format, size, and URL accessibility.",
        "network_error": "Safe to retry. Network issues are typically transient.",
        "quota_exceeded": "Wait for quota reset or reduce posting frequency.",
        "unknown": "Review the error details. May be safe to retry.",
    }
    return suggestions.get(category, "Review error details before retrying.")


async def _count_by_category(db: AsyncSession, workspace_id: str) -> dict[str, int]:
    """Count failed items by error category."""
    result = await db.execute(
        select(PostPlatform.error_message).where(
            PostPlatform.workspace_id == workspace_id,
            PostPlatform.status == "failed",
        )
    )
    errors = [row[0] for row in result.all()]
    categories: dict[str, int] = {}
    for error in errors:
        cat = _categorize_error(error or "")
        categories[cat] = categories.get(cat, 0) + 1
    return dict(sorted(categories.items(), key=lambda x: x[1], reverse=True))


async def _calc_retry_success_rate(db: AsyncSession, workspace_id: str) -> float:
    """Calculate what percentage of retried items eventually succeeded."""
    # Items that were retried (retry_count > 0)
    retried = await db.execute(
        select(func.count(PostPlatform.id)).where(
            PostPlatform.workspace_id == workspace_id,
            PostPlatform.retry_count > 0,
        )
    )
    total_retried = retried.scalar() or 0

    if total_retried == 0:
        return 0.0

    # Of those, how many succeeded?
    succeeded = await db.execute(
        select(func.count(PostPlatform.id)).where(
            PostPlatform.workspace_id == workspace_id,
            PostPlatform.retry_count > 0,
            PostPlatform.status == "published",
        )
    )
    total_succeeded = succeeded.scalar() or 0

    return round(total_succeeded / total_retried * 100, 1)
