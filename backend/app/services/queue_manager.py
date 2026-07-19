"""Advanced queue manager — priority ordering, bulk operations, queue analytics.

Provides queue reordering, bulk status changes, and queue health metrics.
"""
import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post_platform import PostPlatform

logger = logging.getLogger(__name__)


async def reorder_queue(
    db: AsyncSession,
    workspace_id: str,
    item_ids: list[str],
) -> dict[str, Any]:
    """Reorder the queue by updating scheduled_at times.

    Items are rescheduled with 15-minute intervals in the given order
    starting from the earliest scheduled time in the current queue.
    """
    if not item_ids:
        return {"error": "No items provided"}

    # Get the earliest scheduled time
    earliest_result = await db.execute(
        select(func.min(PostPlatform.scheduled_at)).where(
            PostPlatform.workspace_id == workspace_id,
            PostPlatform.status == "scheduled",
            PostPlatform.scheduled_at.isnot(None),
        )
    )
    earliest = earliest_result.scalar() or datetime.utcnow()

    # Fetch all items
    result = await db.execute(
        select(PostPlatform).where(
            PostPlatform.id.in_(item_ids),
            PostPlatform.workspace_id == workspace_id,
        )
    )
    items = {pp.id: pp for pp in result.scalars().all()}

    reordered = []
    current_time = earliest
    for i, item_id in enumerate(item_ids):
        pp = items.get(item_id)
        if pp and pp.status == "scheduled":
            pp.scheduled_at = current_time
            reordered.append({"id": item_id, "new_time": current_time.isoformat()})
            current_time += timedelta(minutes=15)

    await db.flush()

    return {
        "reordered": len(reordered),
        "items": reordered,
        "new_schedule_start": earliest.isoformat(),
    }


async def bulk_update_status(
    db: AsyncSession,
    workspace_id: str,
    item_ids: list[str],
    new_status: str,
) -> dict[str, Any]:
    """Bulk update status for multiple queue items."""
    valid_statuses = {"draft", "scheduled", "cancelled"}
    if new_status not in valid_statuses:
        return {"error": f"Invalid status: {new_status}. Must be one of {valid_statuses}"}

    result = await db.execute(
        select(PostPlatform).where(
            PostPlatform.id.in_(item_ids),
            PostPlatform.workspace_id == workspace_id,
        )
    )
    items = result.scalars().all()

    updated = 0
    for pp in items:
        if pp.status != "publishing":  # Don't interrupt in-flight publishes
            pp.status = new_status
            if new_status == "cancelled":
                pp.error_message = "Cancelled by user"
            updated += 1

    await db.flush()

    return {"updated": updated, "new_status": new_status}


async def get_queue_analytics(
    db: AsyncSession,
    workspace_id: str,
) -> dict[str, Any]:
    """Get analytics about the publishing queue health."""
    now = datetime.utcnow()

    # Count by status
    status_result = await db.execute(
        select(PostPlatform.status, func.count(PostPlatform.id))
        .where(PostPlatform.workspace_id == workspace_id)
        .group_by(PostPlatform.status)
    )
    status_counts = {row[0]: row[1] for row in status_result.all()}

    # Count by platform
    platform_result = await db.execute(
        select(PostPlatform.platform, func.count(PostPlatform.id))
        .where(
            PostPlatform.workspace_id == workspace_id,
            PostPlatform.status.in_(["scheduled", "publishing"]),
        )
        .group_by(PostPlatform.platform)
    )
    platform_counts = {row[0]: row[1] for row in platform_result.all()}

    # Upcoming schedule (next 7 days)
    upcoming = []
    for day_offset in range(7):
        day = now + timedelta(days=day_offset)
        day_start = day.replace(hour=0, minute=0, second=0)
        day_end = day.replace(hour=23, minute=59, second=59)

        day_count_result = await db.execute(
            select(func.count(PostPlatform.id)).where(
                PostPlatform.workspace_id == workspace_id,
                PostPlatform.status == "scheduled",
                PostPlatform.scheduled_at >= day_start,
                PostPlatform.scheduled_at <= day_end,
            )
        )
        count = day_count_result.scalar() or 0
        upcoming.append({
            "date": day.strftime("%Y-%m-%d"),
            "day_name": day.strftime("%A"),
            "scheduled_count": count,
        })

    # Overdue items (past scheduled_at but not yet published)
    overdue_result = await db.execute(
        select(func.count(PostPlatform.id)).where(
            PostPlatform.workspace_id == workspace_id,
            PostPlatform.status.in_(["scheduled", "publishing"]),
            PostPlatform.scheduled_at < now,
        )
    )
    overdue_count = overdue_result.scalar() or 0

    # Average publish delay (scheduled_at vs published_at)
    delay_result = await db.execute(
        select(
            func.avg(
                func.extract("epoch", PostPlatform.published_at) - func.extract("epoch", PostPlatform.scheduled_at)
            )
        ).where(
            PostPlatform.workspace_id == workspace_id,
            PostPlatform.status == "published",
            PostPlatform.scheduled_at.isnot(None),
            PostPlatform.published_at.isnot(None),
        )
    )
    avg_delay_seconds = delay_result.scalar() or 0

    return {
        "by_status": status_counts,
        "by_platform": platform_counts,
        "upcoming_7_days": upcoming,
        "overdue_count": overdue_count,
        "avg_publish_delay_seconds": round(avg_delay_seconds, 0),
        "total_active": sum(status_counts.get(s, 0) for s in ["scheduled", "publishing"]),
    }
