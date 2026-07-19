"""Calendar service — full CRUD with drag-and-drop reschedule.

Replaces the mock calendar endpoints with real DB operations.
Supports date range queries, drag-and-drop rescheduling, and
campaign-based filtering.
"""
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Post, ContentCalendar
from app.models.post_platform import PostPlatform

logger = logging.getLogger(__name__)


async def get_calendar_events(
    db: AsyncSession,
    workspace_id: str,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    platform: str | None = None,
    status: str | None = None,
) -> list[dict[str, Any]]:
    """Get calendar events from real PostPlatform data.

    Each PostPlatform entry with a scheduled_at becomes a calendar event.
    """
    now = datetime.utcnow()
    if not start_date:
        start_date = now - timedelta(days=30)
    if not end_date:
        end_date = now + timedelta(days=60)

    # Query PostPlatform entries with scheduled_at in range
    query = (
        select(PostPlatform, Post.title, Post.content, Post.author_id)
        .join(Post, PostPlatform.post_id == Post.id)
        .where(
            PostPlatform.workspace_id == workspace_id,
            PostPlatform.scheduled_at >= start_date,
            PostPlatform.scheduled_at <= end_date,
        )
    )

    if platform:
        query = query.where(PostPlatform.platform == platform)
    if status:
        query = query.where(PostPlatform.status == status)

    query = query.order_by(PostPlatform.scheduled_at)
    result = await db.execute(query)
    rows = result.all()

    events = []
    for pp, title, content, author_id in rows:
        events.append({
            "id": pp.id,
            "post_id": pp.post_id,
            "title": title or (content[:50] + "..." if content and len(content) > 50 else content),
            "content_preview": (content[:100] + "..." if content and len(content) > 100 else content),
            "platform": pp.platform,
            "status": pp.status,
            "date": pp.scheduled_at.strftime("%Y-%m-%d") if pp.scheduled_at else None,
            "time_slot": pp.scheduled_at.strftime("%H:%M") if pp.scheduled_at else None,
            "scheduled_at": pp.scheduled_at.isoformat() if pp.scheduled_at else None,
            "published_at": pp.published_at.isoformat() if pp.published_at else None,
            "platform_post_id": pp.platform_post_id,
            "author_id": author_id,
            "media_urls": pp.media_asset_ids or [],
        })

    return events


async def reschedule_event(
    db: AsyncSession,
    workspace_id: str,
    item_id: str,
    new_date: str,
    new_time: str | None = None,
) -> dict[str, Any]:
    """Reschedule a calendar event (drag-and-drop handler).

    Args:
        item_id: PostPlatform row ID.
        new_date: New date in YYYY-MM-DD format.
        new_time: Optional new time in HH:MM format.
    """
    result = await db.execute(
        select(PostPlatform).where(
            PostPlatform.id == item_id,
            PostPlatform.workspace_id == workspace_id,
        )
    )
    pp = result.scalar_one_none()
    if not pp:
        return {"error": f"Event {item_id} not found"}

    if pp.status == "publishing":
        return {"error": "Cannot reschedule a post that is currently publishing"}

    # Parse new datetime
    try:
        if new_time:
            new_dt = datetime.strptime(f"{new_date} {new_time}", "%Y-%m-%d %H:%M")
        else:
            # Keep the same time, change the date
            old_time = pp.scheduled_at.strftime("%H:%M") if pp.scheduled_at else "09:00"
            new_dt = datetime.strptime(f"{new_date} {old_time}", "%Y-%m-%d %H:%M")
    except ValueError:
        return {"error": "Invalid date/time format"}

    old_time_str = pp.scheduled_at.isoformat() if pp.scheduled_at else "none"
    pp.scheduled_at = new_dt
    if pp.status == "published":
        pp.status = "scheduled"  # Allow re-scheduling published items

    await db.flush()

    return {
        "id": item_id,
        "old_scheduled_at": old_time_str,
        "new_scheduled_at": new_dt.isoformat(),
        "platform": pp.platform,
        "message": f"Rescheduled to {new_date} {new_time or ''}",
    }


async def get_calendar_stats(
    db: AsyncSession,
    workspace_id: str,
    month: int | None = None,
    year: int | None = None,
) -> dict[str, Any]:
    """Get calendar statistics for a month."""
    now = datetime.utcnow()
    target_month = month or now.month
    target_year = year or now.year

    month_start = datetime(target_year, target_month, 1)
    if target_month == 12:
        month_end = datetime(target_year + 1, 1, 1)
    else:
        month_end = datetime(target_year, target_month + 1, 1)

    # Count by platform
    platform_result = await db.execute(
        select(PostPlatform.platform, func.count(PostPlatform.id))
        .where(
            PostPlatform.workspace_id == workspace_id,
            PostPlatform.scheduled_at >= month_start,
            PostPlatform.scheduled_at < month_end,
        )
        .group_by(PostPlatform.platform)
    )
    by_platform = {row[0]: row[1] for row in platform_result.all()}

    # Count by status
    status_result = await db.execute(
        select(PostPlatform.status, func.count(PostPlatform.id))
        .where(
            PostPlatform.workspace_id == workspace_id,
            PostPlatform.scheduled_at >= month_start,
            PostPlatform.scheduled_at < month_end,
        )
        .group_by(PostPlatform.status)
    )
    by_status = {row[0]: row[1] for row in status_result.all()}

    # Count by day of week
    dow_result = await db.execute(
        select(
            func.extract("dow", PostPlatform.scheduled_at),
            func.count(PostPlatform.id),
        )
        .where(
            PostPlatform.workspace_id == workspace_id,
            PostPlatform.scheduled_at >= month_start,
            PostPlatform.scheduled_at < month_end,
        )
        .group_by(func.extract("dow", PostPlatform.scheduled_at))
    )
    by_day_of_week = {int(row[0]): row[1] for row in dow_result.all()}

    return {
        "month": target_month,
        "year": target_year,
        "total_events": sum(by_platform.values()),
        "by_platform": by_platform,
        "by_status": by_status,
        "by_day_of_week": by_day_of_week,
    }
