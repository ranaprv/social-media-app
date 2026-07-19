"""Admin dashboard metrics — real-time system health and usage stats.

Provides workspace-level and system-level metrics for the admin dashboard.
"""
import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Post, PlatformConnection, AnalyticsMetric
from app.models.post_platform import PostPlatform

logger = logging.getLogger(__name__)


async def get_workspace_metrics(
    db: AsyncSession,
    workspace_id: str,
) -> dict[str, Any]:
    """Get comprehensive workspace metrics for the admin dashboard."""
    now = datetime.utcnow()
    last_7d = now - timedelta(days=7)
    last_30d = now - timedelta(days=30)

    # Post counts
    total_posts = (await db.execute(
        select(func.count(Post.id)).where(Post.workspace_id == workspace_id)
    )).scalar() or 0

    posts_7d = (await db.execute(
        select(func.count(Post.id)).where(
            Post.workspace_id == workspace_id,
            Post.created_at >= last_7d,
        )
    )).scalar() or 0

    # Platform entries
    total_entries = (await db.execute(
        select(func.count(PostPlatform.id)).where(
            PostPlatform.workspace_id == workspace_id,
        )
    )).scalar() or 0

    entries_by_status = {}
    status_result = await db.execute(
        select(PostPlatform.status, func.count(PostPlatform.id))
        .where(PostPlatform.workspace_id == workspace_id)
        .group_by(PostPlatform.status)
    )
    for status, count in status_result.all():
        entries_by_status[status] = count

    # Connections
    connections_result = await db.execute(
        select(PlatformConnection.platform).where(
            PlatformConnection.workspace_id == workspace_id,
        )
    )
    connected_platforms = list(set(row[0] for row in connections_result.all()))

    # Analytics totals
    analytics_result = await db.execute(
        select(
            func.sum(AnalyticsMetric.impressions),
            func.sum(AnalyticsMetric.engagement),
            func.sum(AnalyticsMetric.reach),
            func.sum(AnalyticsMetric.clicks),
        ).join(Post, Post.id == AnalyticsMetric.post_id)
        .where(Post.workspace_id == workspace_id)
    )
    row = analytics_result.one()
    total_impressions = row[0] or 0
    total_engagement = row[1] or 0
    total_reach = row[2] or 0
    total_clicks = row[3] or 0

    # Recent analytics (last 7 days)
    recent_result = await db.execute(
        select(
            func.sum(AnalyticsMetric.impressions),
            func.sum(AnalyticsMetric.engagement),
        ).join(Post, Post.id == AnalyticsMetric.post_id)
        .where(
            Post.workspace_id == workspace_id,
            AnalyticsMetric.recorded_at >= last_7d,
        )
    )
    recent_row = recent_result.one()
    impressions_7d = recent_row[0] or 0
    engagement_7d = recent_row[1] or 0

    # Success rate
    published = entries_by_status.get("published", 0)
    failed = entries_by_status.get("failed", 0)
    total_attempted = published + failed
    success_rate = round((published / total_attempted * 100) if total_attempted > 0 else 0, 1)

    return {
        "posts": {
            "total": total_posts,
            "last_7_days": posts_7d,
        },
        "queue": {
            "total_entries": total_entries,
            "by_status": entries_by_status,
            "success_rate": success_rate,
        },
        "connections": {
            "count": len(connected_platforms),
            "platforms": connected_platforms,
        },
        "analytics": {
            "total_impressions": total_impressions,
            "total_engagement": total_engagement,
            "total_reach": total_reach,
            "total_clicks": total_clicks,
            "impressions_7d": impressions_7d,
            "engagement_7d": engagement_7d,
            "engagement_rate": round(
                (total_engagement / total_impressions * 100) if total_impressions > 0 else 0,
                2,
            ),
        },
    }


async def get_system_health(db: AsyncSession) -> dict[str, Any]:
    """Get system-wide health metrics across all workspaces."""
    now = datetime.utcnow()
    last_24h = now - timedelta(hours=24)

    # Total workspaces
    from app.models.workspace import Workspace
    total_workspaces = (await db.execute(
        select(func.count(Workspace.id))
    )).scalar() or 0

    # Total posts across all workspaces
    total_posts = (await db.execute(
        select(func.count(Post.id))
    )).scalar() or 0

    # Posts published in last 24h
    posts_24h = (await db.execute(
        select(func.count(PostPlatform.id)).where(
            PostPlatform.status == "published",
            PostPlatform.published_at >= last_24h,
        )
    )).scalar() or 0

    # Failed in last 24h
    failed_24h = (await db.execute(
        select(func.count(PostPlatform.id)).where(
            PostPlatform.status == "failed",
            PostPlatform.updated_at >= last_24h,
        )
    )).scalar() or 0

    # Queue depth
    queue_depth = (await db.execute(
        select(func.count(PostPlatform.id)).where(
            PostPlatform.status.in_(["scheduled", "publishing"]),
        )
    )).scalar() or 0

    return {
        "timestamp": now.isoformat(),
        "workspaces": total_workspaces,
        "total_posts": total_posts,
        "last_24h": {
            "published": posts_24h,
            "failed": failed_24h,
            "success_rate": round(
                (posts_24h / max(posts_24h + failed_24h, 1)) * 100, 1
            ),
        },
        "queue_depth": queue_depth,
    }
