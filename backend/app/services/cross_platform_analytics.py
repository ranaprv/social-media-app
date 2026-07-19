"""Cross-platform analytics aggregation — unified metrics view.

Aggregates analytics data across all platforms into a single
unified view for comparison and reporting.
"""
import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Post, AnalyticsMetric

logger = logging.getLogger(__name__)


async def get_cross_platform_analytics(
    db: AsyncSession,
    workspace_id: str,
    days: int = 30,
) -> dict[str, Any]:
    """Get unified analytics across all platforms."""
    cutoff = datetime.utcnow() - timedelta(days=days)

    # Per-platform metrics
    platform_result = await db.execute(
        select(
            AnalyticsMetric.platform,
            func.sum(AnalyticsMetric.impressions),
            func.sum(AnalyticsMetric.engagement),
            func.sum(AnalyticsMetric.reach),
            func.sum(AnalyticsMetric.clicks),
            func.sum(AnalyticsMetric.likes),
            func.sum(AnalyticsMetric.shares),
            func.sum(AnalyticsMetric.comments),
            func.count(AnalyticsMetric.id),
        )
        .join(Post, Post.id == AnalyticsMetric.post_id)
        .where(
            Post.workspace_id == workspace_id,
            AnalyticsMetric.recorded_at >= cutoff,
        )
        .group_by(AnalyticsMetric.platform)
    )
    rows = platform_result.all()

    platforms: dict[str, dict[str, Any]] = {}
    totals = {"impressions": 0, "engagement": 0, "reach": 0, "clicks": 0}

    for row in rows:
        platform = row[0]
        imp = row[1] or 0
        eng = row[2] or 0
        reach = row[3] or 0
        clicks = row[4] or 0
        likes = row[5] or 0
        shares = row[6] or 0
        comments = row[7] or 0
        post_count = row[8] or 0

        eng_rate = (eng / imp * 100) if imp > 0 else 0

        platforms[platform] = {
            "impressions": imp,
            "engagement": eng,
            "reach": reach,
            "clicks": clicks,
            "likes": likes,
            "shares": shares,
            "comments": comments,
            "post_count": post_count,
            "engagement_rate": round(eng_rate, 2),
            "avg_impressions": round(imp / max(post_count, 1)),
            "avg_engagement": round(eng / max(post_count, 1)),
        }

        totals["impressions"] += imp
        totals["engagement"] += eng
        totals["reach"] += reach
        totals["clicks"] += clicks

    # Platform comparison ranking
    ranked = sorted(
        platforms.items(),
        key=lambda x: x[1]["engagement_rate"],
        reverse=True,
    )

    return {
        "period_days": days,
        "totals": totals,
        "by_platform": platforms,
        "platform_ranking": [
            {"rank": i + 1, "platform": p, "engagement_rate": d["engagement_rate"]}
            for i, (p, d) in enumerate(ranked)
        ],
        "best_platform": ranked[0][0] if ranked else None,
        "overall_engagement_rate": round(
            (totals["engagement"] / totals["impressions"] * 100)
            if totals["impressions"] > 0 else 0, 2
        ),
    }


async def get_cross_platform_trends(
    db: AsyncSession,
    workspace_id: str,
    days: int = 30,
) -> dict[str, Any]:
    """Get trend data across platforms over time."""
    cutoff = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(
            func.date(AnalyticsMetric.recorded_at),
            AnalyticsMetric.platform,
            func.sum(AnalyticsMetric.engagement),
            func.sum(AnalyticsMetric.impressions),
        )
        .join(Post, Post.id == AnalyticsMetric.post_id)
        .where(
            Post.workspace_id == workspace_id,
            AnalyticsMetric.recorded_at >= cutoff,
        )
        .group_by(func.date(AnalyticsMetric.recorded_at), AnalyticsMetric.platform)
        .order_by(func.date(AnalyticsMetric.recorded_at))
    )
    rows = result.all()

    # Organize by date and platform
    trends: dict[str, dict[str, dict]] = {}
    for date_val, platform, engagement, impressions in rows:
        date_str = str(date_val)
        if date_str not in trends:
            trends[date_str] = {}
        eng_rate = (engagement / impressions * 100) if impressions > 0 else 0
        trends[date_str][platform] = {
            "engagement": engagement or 0,
            "impressions": impressions or 0,
            "engagement_rate": round(eng_rate, 2),
        }

    return {
        "period_days": days,
        "trends": trends,
        "data_points": len(rows),
    }
