"""Automated content calendar reminders.

Sends reminders for upcoming posts, deadlines, and review requests.
"""
import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post_platform import PostPlatform

logger = logging.getLogger(__name__)


async def get_upcoming_reminders(
    db: AsyncSession,
    workspace_id: str,
    hours_ahead: int = 24,
) -> list[dict[str, Any]]:
    """Get upcoming reminders for posts due in the next N hours."""
    now = datetime.utcnow()
    cutoff = now + timedelta(hours=hours_ahead)

    result = await db.execute(
        select(PostPlatform).where(
            PostPlatform.workspace_id == workspace_id,
            PostPlatform.status.in_(["scheduled", "review"]),
            PostPlatform.scheduled_at.isnot(None),
            PostPlatform.scheduled_at <= cutoff,
            PostPlatform.scheduled_at > now,
        ).order_by(PostPlatform.scheduled_at)
    )
    items = result.scalars().all()

    reminders: list[dict[str, Any]] = []
    for item in items:
        hours_until = (item.scheduled_at - now).total_seconds() / 3600

        if item.status == "review":
            reminders.append({
                "type": "approval_needed",
                "severity": "high",
                "post_id": item.post_id,
                "platform": item.platform,
                "message": f"Post for {item.platform} needs approval",
                "scheduled_at": item.scheduled_at.isoformat(),
                "hours_until": round(hours_until, 1),
            })
        elif hours_until <= 1:
            reminders.append({
                "type": "publishing_soon",
                "severity": "high",
                "post_id": item.post_id,
                "platform": item.platform,
                "message": f"Post for {item.platform} publishing in {round(hours_until * 60)} minutes",
                "scheduled_at": item.scheduled_at.isoformat(),
                "hours_until": round(hours_until, 1),
            })
        elif hours_until <= 6:
            reminders.append({
                "type": "upcoming",
                "severity": "medium",
                "post_id": item.post_id,
                "platform": item.platform,
                "message": f"Post for {item.platform} scheduled in {round(hours_until, 1)} hours",
                "scheduled_at": item.scheduled_at.isoformat(),
                "hours_until": round(hours_until, 1),
            })
        else:
            reminders.append({
                "type": "scheduled",
                "severity": "low",
                "post_id": item.post_id,
                "platform": item.platform,
                "message": f"Post for {item.platform} scheduled at {item.scheduled_at.strftime('%H:%M')}",
                "scheduled_at": item.scheduled_at.isoformat(),
                "hours_until": round(hours_until, 1),
            })

    return reminders


async def check_overdue_posts(
    db: AsyncSession,
    workspace_id: str,
) -> list[dict[str, Any]]:
    """Check for posts that are overdue (past scheduled_at but not published)."""
    now = datetime.utcnow()

    result = await db.execute(
        select(PostPlatform).where(
            PostPlatform.workspace_id == workspace_id,
            PostPlatform.status.in_(["scheduled", "publishing"]),
            PostPlatform.scheduled_at.isnot(None),
            PostPlatform.scheduled_at < now,
        )
    )
    items = result.scalars().all()

    overdue: list[dict[str, Any]] = []
    for item in items:
        overdue_minutes = (now - item.scheduled_at).total_seconds() / 60
        overdue.append({
            "post_id": item.post_id,
            "platform": item.platform,
            "status": item.status,
            "scheduled_at": item.scheduled_at.isoformat(),
            "overdue_minutes": round(overdue_minutes),
        })

    return overdue
