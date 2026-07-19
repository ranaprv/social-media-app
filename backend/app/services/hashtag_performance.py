"""Hashtag Performance Tracker — track hashtag reach over time, identify trending tags.

Analyzes hashtag usage in published posts and correlates with engagement.
"""
import logging
import re
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Post, AnalyticsMetric

logger = logging.getLogger(__name__)


async def get_hashtag_performance(
    db: AsyncSession,
    workspace_id: str,
    platform: str | None = None,
    days: int = 30,
) -> dict[str, Any]:
    """Analyze hashtag performance across published posts."""
    cutoff = datetime.utcnow() - timedelta(days=days)

    query = select(
        Post.content,
        Post.platform,
        Post.published_at,
        AnalyticsMetric.engagement,
        AnalyticsMetric.impressions,
    ).join(AnalyticsMetric, Post.id == AnalyticsMetric.post_id).where(
        Post.workspace_id == workspace_id,
        Post.published_at >= cutoff,
        Post.status == "published",
    )

    if platform:
        query = query.where(Post.platform == platform)

    result = await db.execute(query)
    rows = result.all()

    # Extract hashtags and compute performance
    hashtag_data: dict[str, dict[str, Any]] = {}

    for content, post_platform, published_at, engagement, impressions in rows:
        if not content:
            continue

        hashtags = re.findall(r"#\w+", content)
        eng_rate = (engagement / impressions * 100) if impressions and impressions > 0 else 0

        for tag in hashtags:
            tag_lower = tag.lower()
            if tag_lower not in hashtag_data:
                hashtag_data[tag_lower] = {
                    "tag": tag,
                    "usage_count": 0,
                    "total_engagement": 0,
                    "total_impressions": 0,
                    "platforms": set(),
                    "engagement_rates": [],
                }

            hashtag_data[tag_lower]["usage_count"] += 1
            hashtag_data[tag_lower]["total_engagement"] += engagement or 0
            hashtag_data[tag_lower]["total_impressions"] += impressions or 0
            hashtag_data[tag_lower]["platforms"].add(post_platform)
            hashtag_data[tag_lower]["engagement_rates"].append(eng_rate)

    # Compute scores
    hashtags = []
    for tag, data in hashtag_data.items():
        avg_eng_rate = sum(data["engagement_rates"]) / len(data["engagement_rates"]) if data["engagement_rates"] else 0
        hashtags.append({
            "tag": data["tag"],
            "usage_count": data["usage_count"],
            "avg_engagement_rate": round(avg_eng_rate, 2),
            "total_engagement": data["total_engagement"],
            "platforms": list(data["platforms"]),
            "performance_score": round(min(avg_eng_rate * 10, 100), 1),
        })

    # Sort by performance
    hashtags.sort(key=lambda x: x["performance_score"], reverse=True)

    # Identify trending (high recent usage + high engagement)
    trending = [h for h in hashtags if h["usage_count"] >= 3 and h["avg_engagement_rate"] > 3.0][:10]

    # Identify underperforming (used often but low engagement)
    underperforming = [h for h in hashtags if h["usage_count"] >= 3 and h["avg_engagement_rate"] < 1.0][:5]

    return {
        "total_unique_hashtags": len(hashtags),
        "hashtags": hashtags[:50],
        "trending": trending,
        "underperforming": underperforming,
        "top_performers": hashtags[:10],
        "period_days": days,
    }


async def get_hashtag_trends(
    db: AsyncSession,
    workspace_id: str,
    hashtag: str,
    days: int = 30,
) -> dict[str, Any]:
    """Track a specific hashtag's performance over time."""
    cutoff = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(
            func.date(Post.published_at),
            func.sum(AnalyticsMetric.engagement),
            func.sum(AnalyticsMetric.impressions),
            func.count(Post.id),
        )
        .join(AnalyticsMetric, Post.id == AnalyticsMetric.post_id)
        .where(
            Post.workspace_id == workspace_id,
            Post.published_at >= cutoff,
            Post.status == "published",
            Post.content.ilike(f"%{hashtag}%"),
        )
        .group_by(func.date(Post.published_at))
        .order_by(func.date(Post.published_at))
    )
    rows = result.all()

    trend_data = []
    for date_val, engagement, impressions, count in rows:
        eng_rate = (engagement / impressions * 100) if impressions and impressions > 0 else 0
        trend_data.append({
            "date": str(date_val),
            "usage_count": count or 0,
            "engagement": engagement or 0,
            "impressions": impressions or 0,
            "engagement_rate": round(eng_rate, 2),
        })

    return {
        "hashtag": hashtag,
        "trend": trend_data,
        "total_posts": sum(d["usage_count"] for d in trend_data),
        "avg_engagement_rate": round(
            sum(d["engagement_rate"] for d in trend_data) / max(len(trend_data), 1), 2
        ),
    }
