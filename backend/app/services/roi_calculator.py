"""ROI Calculator — social media revenue attribution.

Calculates return on investment for social media activities.
"""
import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Post, AnalyticsMetric

logger = logging.getLogger(__name__)


async def calculate_roi(
    db: AsyncSession,
    workspace_id: str,
    days: int = 30,
    ad_spend: float = 0,
    time_cost_per_hour: float = 50,
    hours_per_week: float = 10,
) -> dict[str, Any]:
    """Calculate social media ROI."""
    cutoff = datetime.utcnow() - timedelta(days=days)

    # Get engagement metrics
    result = await db.execute(
        select(
            func.sum(AnalyticsMetric.impressions),
            func.sum(AnalyticsMetric.engagement),
            func.sum(AnalyticsMetric.clicks),
            func.sum(AnalyticsMetric.reach),
            func.count(Post.id),
        )
        .join(Post, Post.id == AnalyticsMetric.post_id)
        .where(
            Post.workspace_id == workspace_id,
            AnalyticsMetric.recorded_at >= cutoff,
        )
    )
    row = result.one()

    impressions = row[0] or 0
    engagement = row[1] or 0
    clicks = row[2] or 0
    reach = row[3] or 0
    post_count = row[4] or 0

    # Cost calculation
    weeks = max(days / 7, 1)
    time_cost = hours_per_week * time_cost_per_hour * weeks
    total_cost = ad_spend + time_cost

    # Value estimation (industry averages)
    # CPM (cost per 1000 impressions) benchmark: $5-15
    # CPC (cost per click) benchmark: $0.50-2.00
    # Engagement value: $0.01-0.05 per engagement
    impressions_value = (impressions / 1000) * 8  # $8 CPM average
    clicks_value = clicks * 1.50  # $1.50 CPC average
    engagement_value = engagement * 0.02  # $0.02 per engagement

    total_value = impressions_value + clicks_value + engagement_value

    # ROI calculation
    roi = ((total_value - total_cost) / max(total_cost, 1)) * 100
    cost_per_engagement = total_cost / max(engagement, 1)
    cost_per_click = total_cost / max(clicks, 1)

    # Efficiency score
    efficiency = min(100, (total_value / max(total_cost, 1)) * 50)

    return {
        "period_days": days,
        "investment": {
            "ad_spend": ad_spend,
            "time_cost": round(time_cost, 2),
            "total_cost": round(total_cost, 2),
            "hours_per_week": hours_per_week,
            "time_cost_per_hour": time_cost_per_hour,
        },
        "returns": {
            "impressions_value": round(impressions_value, 2),
            "clicks_value": round(clicks_value, 2),
            "engagement_value": round(engagement_value, 2),
            "total_value": round(total_value, 2),
        },
        "roi_percentage": round(roi, 1),
        "efficiency_score": round(efficiency),
        "cost_per_engagement": round(cost_per_engagement, 2),
        "cost_per_click": round(cost_per_click, 2),
        "metrics": {
            "impressions": impressions,
            "engagement": engagement,
            "clicks": clicks,
            "reach": reach,
            "posts": post_count,
        },
    }
