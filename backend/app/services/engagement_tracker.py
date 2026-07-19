"""Engagement tracker — monitor comments, mentions, replies.

Tracks engagement signals across platforms and surfaces actionable
insights for community management.
"""
import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Post, AnalyticsMetric

logger = logging.getLogger(__name__)


async def get_engagement_summary(
    db: AsyncSession,
    workspace_id: str,
    days: int = 7,
) -> dict[str, Any]:
    """Get engagement summary for the workspace."""
    cutoff = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(
            func.sum(AnalyticsMetric.likes),
            func.sum(AnalyticsMetric.comments),
            func.sum(AnalyticsMetric.shares),
            func.sum(AnalyticsMetric.clicks),
            func.sum(AnalyticsMetric.engagement),
            func.count(AnalyticsMetric.id),
        )
        .join(Post, Post.id == AnalyticsMetric.post_id)
        .where(
            Post.workspace_id == workspace_id,
            AnalyticsMetric.recorded_at >= cutoff,
        )
    )
    row = result.one()

    likes = row[0] or 0
    comments = row[1] or 0
    shares = row[2] or 0
    clicks = row[3] or 0
    total_engagement = row[4] or 0
    post_count = row[5] or 0

    # Per-platform breakdown
    platform_result = await db.execute(
        select(
            AnalyticsMetric.platform,
            func.sum(AnalyticsMetric.likes),
            func.sum(AnalyticsMetric.comments),
            func.sum(AnalyticsMetric.shares),
        )
        .join(Post, Post.id == AnalyticsMetric.post_id)
        .where(
            Post.workspace_id == workspace_id,
            AnalyticsMetric.recorded_at >= cutoff,
        )
        .group_by(AnalyticsMetric.platform)
    )
    by_platform = {}
    for platform, p_likes, p_comments, p_shares in platform_result.all():
        by_platform[platform] = {
            "likes": p_likes or 0,
            "comments": p_comments or 0,
            "shares": p_shares or 0,
            "total": (p_likes or 0) + (p_comments or 0) + (p_shares or 0),
        }

    return {
        "period_days": days,
        "total": {
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "clicks": clicks,
            "engagement": total_engagement,
        },
        "per_post": {
            "avg_likes": round(likes / max(post_count, 1), 1),
            "avg_comments": round(comments / max(post_count, 1), 1),
            "avg_shares": round(shares / max(post_count, 1), 1),
        },
        "by_platform": by_platform,
        "engagement_rate": 0,
    }

    # Calculate engagement rate separately
    imp_result = await db.execute(
        select(func.sum(AnalyticsMetric.impressions))
        .join(Post, Post.id == AnalyticsMetric.post_id)
        .where(Post.workspace_id == workspace_id, AnalyticsMetric.recorded_at >= cutoff)
    )
    total_impressions = imp_result.scalar() or 1
    result["engagement_rate"] = round((total_engagement / total_impressions) * 100, 2)

    return result


async def get_top_engaging_posts(
    db: AsyncSession,
    workspace_id: str,
    limit: int = 10,
    days: int = 30,
) -> list[dict[str, Any]]:
    """Get posts with highest engagement."""
    cutoff = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(
            Post.id,
            Post.title,
            Post.platform,
            Post.published_at,
            func.sum(AnalyticsMetric.engagement).label("total_engagement"),
            func.sum(AnalyticsMetric.impressions).label("total_impressions"),
        )
        .join(AnalyticsMetric, Post.id == AnalyticsMetric.post_id)
        .where(
            Post.workspace_id == workspace_id,
            Post.status == "published",
            Post.published_at >= cutoff,
        )
        .group_by(Post.id)
        .order_by(func.sum(AnalyticsMetric.engagement).desc())
        .limit(limit)
    )
    rows = result.all()

    return [
        {
            "post_id": row[0],
            "title": row[1],
            "platform": row[2],
            "published_at": row[3].isoformat() if row[3] else None,
            "total_engagement": row[4] or 0,
            "total_impressions": row[5] or 0,
            "engagement_rate": round(
                ((row[4] or 0) / (row[5] or 1)) * 100, 2
            ),
        }
        for row in rows
    ]
