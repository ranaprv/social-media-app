"""Bulk operations — schedule, publish, cancel in batch.

Efficiently handle bulk operations on PostPlatform entries.
"""
import logging
from datetime import datetime
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post_platform import PostPlatform

logger = logging.getLogger(__name__)


async def bulk_schedule(
    db: AsyncSession,
    workspace_id: str,
    post_ids: list[str],
    platforms: list[str],
    scheduled_at: datetime,
) -> dict[str, Any]:
    """Schedule multiple posts to multiple platforms in one operation."""
    created = []
    errors = []

    for post_id in post_ids:
        for platform in platforms:
            # Check for existing
            existing = await db.execute(
                select(PostPlatform).where(
                    PostPlatform.post_id == post_id,
                    PostPlatform.platform == platform,
                )
            )
            if existing.scalar_one_one():
                errors.append(f"Post {post_id} already has entry for {platform}")
                continue

            pp = PostPlatform(
                post_id=post_id,
                workspace_id=workspace_id,
                platform=platform,
                status="scheduled",
                scheduled_at=scheduled_at,
            )
            db.add(pp)
            created.append({"post_id": post_id, "platform": platform})

    await db.flush()

    return {
        "created": len(created),
        "errors": errors,
        "items": created,
    }


async def bulk_cancel(
    db: AsyncSession,
    workspace_id: str,
    item_ids: list[str] | None = None,
    post_ids: list[str] | None = None,
    platform: str | None = None,
) -> dict[str, Any]:
    """Cancel multiple scheduled items."""
    query = select(PostPlatform).where(
        PostPlatform.workspace_id == workspace_id,
        PostPlatform.status.in_(["draft", "scheduled"]),
    )

    if item_ids:
        query = query.where(PostPlatform.id.in_(item_ids))
    elif post_ids:
        query = query.where(PostPlatform.post_id.in_(post_ids))
    if platform:
        query = query.where(PostPlatform.platform == platform)

    result = await db.execute(query)
    items = result.scalars().all()

    cancelled = 0
    for item in items:
        item.status = "cancelled"
        item.error_message = "Cancelled via bulk operation"
        cancelled += 1

    await db.flush()

    return {"cancelled": cancelled}


async def bulk_update_caption(
    db: AsyncSession,
    workspace_id: str,
    item_ids: list[str],
    caption_template: str,
    replacements: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Update captions for multiple items using a template.

    Template supports placeholders: {platform}, {date}, {title}
    """
    result = await db.execute(
        select(PostPlatform).where(
            PostPlatform.id.in_(item_ids),
            PostPlatform.workspace_id == workspace_id,
        )
    )
    items = result.scalars().all()

    updated = 0
    for item in items:
        caption = caption_template
        if replacements:
            for key, value in replacements.items():
                caption = caption.replace(f"{{{key}}}", value)
        # Platform-specific placeholders
        caption = caption.replace("{platform}", item.platform)
        if item.scheduled_at:
            caption = caption.replace("{date}", item.scheduled_at.strftime("%Y-%m-%d"))

        item.caption = caption
        updated += 1

    await db.flush()

    return {"updated": updated}


async def bulk_reschedule(
    db: AsyncSession,
    workspace_id: str,
    item_ids: list[str],
    new_start: datetime,
    interval_minutes: int = 15,
) -> dict[str, Any]:
    """Reschedule multiple items with staggered times."""
    result = await db.execute(
        select(PostPlatform).where(
            PostPlatform.id.in_(item_ids),
            PostPlatform.workspace_id == workspace_id,
            PostPlatform.status.in_(["draft", "scheduled"]),
        ).order_by(PostPlatform.scheduled_at)
    )
    items = result.scalars().all()

    rescheduled = []
    current_time = new_start

    for item in items:
        item.scheduled_at = current_time
        item.status = "scheduled"
        rescheduled.append({
            "id": item.id,
            "platform": item.platform,
            "new_time": current_time.isoformat(),
        })
        from datetime import timedelta
        current_time += timedelta(minutes=interval_minutes)

    await db.flush()

    return {
        "rescheduled": len(rescheduled),
        "items": rescheduled,
    }
