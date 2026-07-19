"""Community Health Dashboard — engagement quality metrics.

Measures community health beyond simple engagement counts.
"""
import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Post, AnalyticsMetric

logger = logging.getLogger(__name__)


async def get_community_health(
    db: AsyncSession,
    workspace_id: str,
    days: int = 30,
) -> dict[str, Any]:
    """Get community health metrics."""
    cutoff = datetime.utcnow() - timedelta(days=days)

    # Basic engagement metrics
    result = await db.execute(
        select(
            func.sum(AnalyticsMetric.likes),
            func.sum(AnalyticsMetric.comments),
            func.sum(AnalyticsMetric.shares),
            func.sum(AnalyticsMetric.clicks),
            func.sum(AnalyticsMetric.impressions),
            func.count(Post.id),
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
    impressions = row[4] or 0
    post_count = row[5] or 0

    # Quality metrics
    eng_rate = (likes + comments + shares) / max(impressions, 1) * 100
    comment_ratio = comments / max(likes + comments + shares, 1) * 100
    share_ratio = shares / max(likes + comments + shares, 1) * 100
    virality = shares / max(post_count, 1)
    conversations = comments / max(post_count, 1)

    # Health score (0-100)
    health_score = 0
    if eng_rate > 5:
        health_score += 30
    elif eng_rate > 2:
        health_score += 20
    elif eng_rate > 1:
        health_score += 10

    if comment_ratio > 20:
        health_score += 25
    elif comment_ratio > 10:
        health_score += 15

    if virality > 5:
        health_score += 25
    elif virality > 2:
        health_score += 15

    if conversations > 3:
        health_score += 20
    elif conversations > 1:
        health_score += 10

    # Rating
    if health_score >= 80:
        rating = "excellent"
    elif health_score >= 60:
        rating = "good"
    elif health_score >= 40:
        rating = "fair"
    else:
        rating = "needs_attention"

    # Recommendations
    recommendations: list[str] = []
    if comment_ratio < 10:
        recommendations.append("Low comment ratio — add more questions and polls to spark conversations")
    if share_ratio < 5:
        recommendations.append("Low share rate — create more shareable content (lists, insights, controversial takes)")
    if conversations < 1:
        recommendations.append("Few conversations — engage more with comments to build community")
    if eng_rate < 2:
        recommendations.append("Low engagement rate — test different content formats and posting times")

    return {
        "period_days": days,
        "health_score": health_score,
        "rating": rating,
        "metrics": {
            "engagement_rate": round(eng_rate, 2),
            "comment_ratio": round(comment_ratio, 1),
            "share_ratio": round(share_ratio, 1),
            "virality": round(virality, 1),
            "conversations_per_post": round(conversations, 1),
        },
        "totals": {
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "clicks": clicks,
            "impressions": impressions,
            "posts": post_count,
        },
        "recommendations": recommendations,
    }
