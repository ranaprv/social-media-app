"""Audience growth tracker — follower/subscriber trends.

Tracks audience growth across platforms and identifies growth patterns.
"""
import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Post, AnalyticsMetric

logger = logging.getLogger(__name__)


async def get_audience_growth(
    db: AsyncSession,
    workspace_id: str,
    days: int = 30,
) -> dict[str, Any]:
    """Get audience growth trends across platforms."""
    cutoff = datetime.utcnow() - timedelta(days=days)

    # Get follower/subscriber data from analytics
    result = await db.execute(
        select(
            func.date(AnalyticsMetric.recorded_at),
            AnalyticsMetric.platform,
            func.sum(AnalyticsMetric.reach),
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

    # Organize by platform
    platform_trends: dict[str, list[dict]] = {}
    for date_val, platform, reach in rows:
        if platform not in platform_trends:
            platform_trends[platform] = []
        platform_trends[platform].append({
            "date": str(date_val),
            "reach": reach or 0,
        })

    # Calculate growth metrics
    growth_summary: dict[str, dict[str, Any]] = {}
    for platform, data_points in platform_trends.items():
        if len(data_points) >= 2:
            first_reach = data_points[0]["reach"]
            last_reach = data_points[-1]["reach"]
            growth = last_reach - first_reach
            growth_pct = (growth / first_reach * 100) if first_reach > 0 else 0
        else:
            growth = 0
            growth_pct = 0

        growth_summary[platform] = {
            "total_reach": sum(d["reach"] for d in data_points),
            "avg_reach": round(sum(d["reach"] for d in data_points) / max(len(data_points), 1)),
            "growth": growth,
            "growth_pct": round(growth_pct, 1),
            "data_points": len(data_points),
            "trend": "up" if growth > 0 else "down" if growth < 0 else "flat",
        }

    return {
        "period_days": days,
        "by_platform": growth_summary,
        "trends": platform_trends,
    }
