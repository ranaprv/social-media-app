"""Audit log — track who did what when for scheduling operations.

Logs all scheduling actions for compliance and debugging.
"""
import logging
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Activity

logger = logging.getLogger(__name__)

# Action types for scheduling
ACTION_TYPES = {
    "post_scheduled": "Post scheduled for publishing",
    "post_published": "Post published successfully",
    "post_failed": "Post publishing failed",
    "post_cancelled": "Post scheduling cancelled",
    "post_rescheduled": "Post rescheduled",
    "post_approved": "Post approved for publishing",
    "post_rejected": "Post rejected",
    "queue_reordered": "Publishing queue reordered",
    "bulk_action": "Bulk operation performed",
    "settings_changed": "Workspace settings updated",
    "template_saved": "Content template saved",
    "template_used": "Content template used",
    "rss_ingested": "RSS feed ingested",
    "ab_test_created": "A/B test created",
    "recycle_scheduled": "Content recycle scheduled",
    "version_created": "Content version snapshot created",
    "version_rolled_back": "Content rolled back to previous version",
}


async def log_scheduling_action(
    db: AsyncSession,
    user_id: str,
    action_type: str,
    description: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Log a scheduling action to the audit trail."""
    activity = Activity(
        id=str(uuid.uuid4()),
        user_id=user_id,
        type=action_type,
        description=description,
        meta=metadata or {},
        created_at=datetime.utcnow(),
    )
    db.add(activity)
    await db.flush()

    return {
        "id": activity.id,
        "action": action_type,
        "description": description,
        "timestamp": activity.created_at.isoformat(),
    }


async def get_audit_log(
    db: AsyncSession,
    workspace_id: str | None = None,
    user_id: str | None = None,
    action_type: str | None = None,
    days: int = 30,
    offset: int = 0,
    limit: int = 50,
) -> dict[str, Any]:
    """Get audit log entries with filtering."""
    from datetime import timedelta
    cutoff = datetime.utcnow() - timedelta(days=days)

    query = select(Activity).where(Activity.created_at >= cutoff)

    if user_id:
        query = query.where(Activity.user_id == user_id)
    if action_type:
        query = query.where(Activity.type == action_type)

    # Count
    from sqlalchemy import func
    count_query = select(func.count(Activity.id)).where(Activity.created_at >= cutoff)
    if user_id:
        count_query = count_query.where(Activity.user_id == user_id)
    if action_type:
        count_query = count_query.where(Activity.type == action_type)

    total = (await db.execute(count_query)).scalar() or 0

    # Fetch
    query = query.order_by(Activity.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    activities = result.scalars().all()

    entries = []
    for activity in activities:
        entries.append({
            "id": activity.id,
            "user_id": activity.user_id,
            "action": activity.type,
            "action_label": ACTION_TYPES.get(activity.type, activity.type),
            "description": activity.description,
            "metadata": activity.meta or {},
            "timestamp": activity.created_at.isoformat() if activity.created_at else None,
        })

    return {
        "entries": entries,
        "total": total,
        "offset": offset,
        "limit": limit,
    }


async def get_audit_stats(
    db: AsyncSession,
    days: int = 30,
) -> dict[str, Any]:
    """Get audit statistics."""
    from datetime import timedelta
    from sqlalchemy import func

    cutoff = datetime.utcnow() - timedelta(days=days)

    # Count by action type
    result = await db.execute(
        select(Activity.type, func.count(Activity.id))
        .where(Activity.created_at >= cutoff)
        .group_by(Activity.type)
    )
    by_action = {row[0]: row[1] for row in result.all()}

    # Count by day
    day_result = await db.execute(
        select(
            func.date(Activity.created_at),
            func.count(Activity.id),
        )
        .where(Activity.created_at >= cutoff)
        .group_by(func.date(Activity.created_at))
        .order_by(func.date(Activity.created_at))
    )
    by_day = {str(row[0]): row[1] for row in day_result.all()}

    # Total actions
    total_result = await db.execute(
        select(func.count(Activity.id)).where(Activity.created_at >= cutoff)
    )
    total = total_result.scalar() or 0

    # Unique users
    users_result = await db.execute(
        select(func.count(func.distinct(Activity.user_id)))
        .where(Activity.created_at >= cutoff)
    )
    unique_users = users_result.scalar() or 0

    return {
        "period_days": days,
        "total_actions": total,
        "unique_users": unique_users,
        "by_action": by_action,
        "by_day": by_day,
    }
