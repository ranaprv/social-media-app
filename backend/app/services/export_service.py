"""Export service — CSV/JSON scheduling reports.

Exports scheduling data, analytics, and queue status for reporting.
"""
import csv
import io
import json
import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Post, AnalyticsMetric
from app.models.post_platform import PostPlatform

logger = logging.getLogger(__name__)


async def export_schedule_csv(
    db: AsyncSession,
    workspace_id: str,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> str:
    """Export scheduling data as CSV."""
    now = datetime.utcnow()
    start = start_date or now - timedelta(days=30)
    end = end_date or now + timedelta(days=30)

    result = await db.execute(
        select(PostPlatform, Post.title, Post.content)
        .join(Post, PostPlatform.post_id == Post.id)
        .where(
            PostPlatform.workspace_id == workspace_id,
            PostPlatform.scheduled_at >= start,
            PostPlatform.scheduled_at <= end,
        )
        .order_by(PostPlatform.scheduled_at)
    )
    rows = result.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Post ID", "Title", "Platform", "Status",
        "Scheduled At", "Published At", "Platform Post ID",
        "Error", "Retry Count", "Caption Preview",
    ])

    for pp, title, content in rows:
        writer.writerow([
            pp.id,
            pp.post_id,
            title or "",
            pp.platform,
            pp.status,
            pp.scheduled_at.isoformat() if pp.scheduled_at else "",
            pp.published_at.isoformat() if pp.published_at else "",
            pp.platform_post_id or "",
            pp.error_message or "",
            pp.retry_count or 0,
            (pp.caption or content or "")[:100],
        ])

    return output.getvalue()


async def export_schedule_json(
    db: AsyncSession,
    workspace_id: str,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> dict[str, Any]:
    """Export scheduling data as structured JSON."""
    now = datetime.utcnow()
    start = start_date or now - timedelta(days=30)
    end = end_date or now + timedelta(days=30)

    result = await db.execute(
        select(PostPlatform, Post.title, Post.content)
        .join(Post, PostPlatform.post_id == Post.id)
        .where(
            PostPlatform.workspace_id == workspace_id,
            PostPlatform.scheduled_at >= start,
            PostPlatform.scheduled_at <= end,
        )
        .order_by(PostPlatform.scheduled_at)
    )
    rows = result.all()

    items = []
    for pp, title, content in rows:
        items.append({
            "id": pp.id,
            "post_id": pp.post_id,
            "title": title,
            "platform": pp.platform,
            "status": pp.status,
            "scheduled_at": pp.scheduled_at.isoformat() if pp.scheduled_at else None,
            "published_at": pp.published_at.isoformat() if pp.published_at else None,
            "platform_post_id": pp.platform_post_id,
            "error": pp.error_message,
            "retry_count": pp.retry_count or 0,
            "caption": (pp.caption or content or "")[:200],
        })

    return {
        "export_date": now.isoformat(),
        "workspace_id": workspace_id,
        "date_range": {"start": start.isoformat(), "end": end.isoformat()},
        "total_items": len(items),
        "items": items,
    }


async def export_analytics_csv(
    db: AsyncSession,
    workspace_id: str,
    days: int = 30,
) -> str:
    """Export analytics data as CSV."""
    cutoff = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(
            Post.id,
            Post.title,
            Post.platform,
            Post.published_at,
            AnalyticsMetric.impressions,
            AnalyticsMetric.engagement,
            AnalyticsMetric.reach,
            AnalyticsMetric.clicks,
            AnalyticsMetric.likes,
            AnalyticsMetric.shares,
            AnalyticsMetric.comments,
        )
        .join(AnalyticsMetric, Post.id == AnalyticsMetric.post_id)
        .where(
            Post.workspace_id == workspace_id,
            AnalyticsMetric.recorded_at >= cutoff,
        )
        .order_by(Post.published_at.desc())
    )
    rows = result.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Post ID", "Title", "Platform", "Published At",
        "Impressions", "Engagement", "Reach", "Clicks",
        "Likes", "Shares", "Comments", "Engagement Rate",
    ])

    for row in rows:
        eng_rate = (row[5] / row[4] * 100) if row[4] and row[4] > 0 else 0
        writer.writerow([
            row[0], row[1] or "", row[2],
            row[3].isoformat() if row[3] else "",
            row[4] or 0, row[5] or 0, row[6] or 0, row[7] or 0,
            row[8] or 0, row[9] or 0, row[10] or 0,
            round(eng_rate, 2),
        ])

    return output.getvalue()
