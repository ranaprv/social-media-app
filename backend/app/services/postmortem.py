"""Postmortem service — auto-analyze failed publishes.

Analyzes failed publish attempts, identifies root causes,
and suggests fixes.
"""
import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post_platform import PostPlatform

logger = logging.getLogger(__name__)


async def analyze_failure(
    db: AsyncSession,
    workspace_id: str,
    post_id: str,
) -> dict[str, Any]:
    """Analyze a specific failed publish attempt."""
    result = await db.execute(
        select(PostPlatform).where(
            PostPlatform.id == post_id,
            PostPlatform.workspace_id == workspace_id,
        )
    )
    item = result.scalar_one_none()
    if not item:
        return {"error": f"PostPlatform {post_id} not found"}

    if item.status != "failed":
        return {"error": "Item is not in failed state"}

    error_msg = item.error_message or "Unknown error"
    category = _categorize(error_msg)
    root_cause = _determine_root_cause(category, error_msg, item)
    fix_suggestion = _suggest_fix(category, error_msg, item)

    return {
        "post_id": post_id,
        "platform": item.platform,
        "error": error_msg,
        "category": category,
        "root_cause": root_cause,
        "fix_suggestion": fix_suggestion,
        "retry_count": item.retry_count or 0,
        "max_retries": item.max_retries or 3,
        "first_attempt": item.created_at.isoformat() if item.created_at else None,
        "last_attempt": item.updated_at.isoformat() if item.updated_at else None,
    }


async def generate_failure_report(
    db: AsyncSession,
    workspace_id: str,
    days: int = 7,
) -> dict[str, Any]:
    """Generate a failure analysis report."""
    cutoff = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(PostPlatform).where(
            PostPlatform.workspace_id == workspace_id,
            PostPlatform.status == "failed",
            PostPlatform.updated_at >= cutoff,
        )
    )
    failures = result.scalars().all()

    # Categorize failures
    categories: dict[str, list[dict]] = {}
    for item in failures:
        error_msg = item.error_message or "Unknown"
        cat = _categorize(error_msg)
        if cat not in categories:
            categories[cat] = []
        categories[cat].append({
            "post_id": item.id,
            "platform": item.platform,
            "error": error_msg[:100],
            "retry_count": item.retry_count or 0,
            "timestamp": item.updated_at.isoformat() if item.updated_at else None,
        })

    # Root causes
    root_causes: list[dict[str, Any]] = []
    for cat, items in categories.items():
        root_causes.append({
            "category": cat,
            "count": len(items),
            "percentage": round(len(items) / max(len(failures), 1) * 100, 1),
            "common_error": items[0]["error"] if items else "",
            "fix": _suggest_fix(cat, items[0]["error"], None) if items else "",
        })

    root_causes.sort(key=lambda x: x["count"], reverse=True)

    return {
        "period_days": days,
        "total_failures": len(failures),
        "by_category": {k: len(v) for k, v in categories.items()},
        "root_causes": root_causes,
        "top_fix": root_causes[0]["fix"] if root_causes else "No failures",
    }


def _categorize(error_msg: str) -> str:
    msg = error_msg.lower()
    if "token" in msg and ("expire" in msg or "invalid" in msg or "401" in msg):
        return "authentication"
    elif "rate limit" in msg or "429" in msg:
        return "rate_limit"
    elif "timeout" in msg:
        return "timeout"
    elif "permission" in msg or "403" in msg:
        return "permission"
    elif "not found" in msg or "404" in msg:
        return "not_found"
    elif "caption" in msg or "content" in msg or "validation" in msg:
        return "content"
    elif "media" in msg or "upload" in msg or "file" in msg:
        return "media"
    elif "network" in msg or "connection" in msg:
        return "network"
    else:
        return "unknown"


def _determine_root_cause(category: str, error_msg: str, item: Any) -> str:
    causes = {
        "authentication": "OAuth token expired or revoked. Platform credentials need refresh.",
        "rate_limit": "Platform API rate limit exceeded. Reduce posting frequency or wait.",
        "timeout": "Platform API responded too slowly. Likely transient — safe to retry.",
        "permission": "App lacks required permissions. Check platform developer settings.",
        "not_found": "Target resource (page, account) may have been deleted or renamed.",
        "content": "Content violates platform rules or exceeds limits. Review and fix.",
        "media": "Media file issue — wrong format, too large, or URL inaccessible.",
        "network": "Network connectivity issue. Likely transient — safe to retry.",
    }
    return causes.get(category, "Unknown cause — review error details.")


def _suggest_fix(category: str, error_msg: str, item: Any) -> str:
    fixes = {
        "authentication": "Go to Connections → Reconnect the platform account. Ensure the token is refreshed.",
        "rate_limit": "Wait 15-30 minutes before retrying. Consider spacing posts further apart.",
        "timeout": "Simply retry — timeouts are usually transient.",
        "permission": "Check your app's permissions in the platform developer portal.",
        "not_found": "Verify the target page/account still exists. Update connection if needed.",
        "content": "Edit the post to comply with platform rules. Check character limits and content policies.",
        "media": "Re-upload the media file. Ensure correct format and size.",
        "network": "Check your server's network connectivity. Retry in a few minutes.",
    }
    return fixes.get(category, "Review the error details and consult platform documentation.")
