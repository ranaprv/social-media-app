"""Content Audit Service — identify underperforming content.

Analyzes published content to find underperformers and suggest improvements.
"""
import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Post, AnalyticsMetric

logger = logging.getLogger(__name__)


async def audit_content(
    db: AsyncSession,
    workspace_id: str,
    days: int = 90,
    threshold_percentile: float = 25,
) -> dict[str, Any]:
    """Audit content performance and identify issues.

    Finds:
      - Underperforming posts (bottom percentile)
      - Overperforming posts (top percentile)
      - Content type patterns
      - Platform-specific issues
    """
    cutoff = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(
            Post.id,
            Post.title,
            Post.content,
            Post.platform,
            Post.published_at,
            Post.media_urls,
            AnalyticsMetric.impressions,
            AnalyticsMetric.engagement,
            AnalyticsMetric.clicks,
        )
        .join(AnalyticsMetric, Post.id == AnalyticsMetric.post_id)
        .where(
            Post.workspace_id == workspace_id,
            Post.status == "published",
            Post.published_at >= cutoff,
        )
        .order_by(Post.published_at.desc())
    )
    rows = result.all()

    if not rows:
        return {"message": "No published content to audit", "audit": None}

    # Calculate engagement rates
    post_data = []
    for row in rows:
        post_id, title, content, platform, published_at, media_urls, impressions, engagement, clicks = row
        eng_rate = (engagement / impressions * 100) if impressions and impressions > 0 else 0
        post_data.append({
            "id": post_id,
            "title": title,
            "platform": platform,
            "published_at": published_at.isoformat() if published_at else None,
            "has_media": bool(media_urls),
            "content_length": len(content or ""),
            "impressions": impressions or 0,
            "engagement": engagement or 0,
            "engagement_rate": round(eng_rate, 2),
        })

    # Sort by engagement rate
    post_data.sort(key=lambda x: x["engagement_rate"])

    # Split into underperformers and overperformers
    split_index = max(1, len(post_data) // 4)
    underperformers = post_data[:split_index]
    overperformers = post_data[-split_index:]

    # Analyze patterns
    avg_eng_rate = sum(p["engagement_rate"] for p in post_data) / len(post_data)
    avg_length = sum(p["content_length"] for p in post_data) / len(post_data)
    media_pct = sum(1 for p in post_data if p["has_media"]) / len(post_data) * 100

    # Issues found
    issues: list[dict[str, str]] = []

    # Check underperformers for common issues
    underperf_avg_length = sum(p["content_length"] for p in underperformers) / max(len(underperformers), 1)
    underperf_media_pct = sum(1 for p in underperformers if p["has_media"]) / max(len(underperformers), 1) * 100

    if underperf_media_pct < media_pct * 0.5:
        issues.append({
            "type": "media_gap",
            "severity": "high",
            "message": f"Underperformers have {underperf_media_pct:.0f}% media usage vs {media_pct:.0f}% overall. Add more visuals.",
        })

    if underperf_avg_length > avg_length * 1.5:
        issues.append({
            "type": "length_issue",
            "severity": "medium",
            "message": f"Underperformers are {underperf_avg_length:.0f} chars vs {avg_length:.0f} avg. Shorten content.",
        })

    # Platform issues
    platform_eng_rates: dict[str, list[float]] = {}
    for p in post_data:
        platform_eng_rates.setdefault(p["platform"], []).append(p["engagement_rate"])

    for platform, rates in platform_eng_rates.items():
        avg = sum(rates) / len(rates)
        if avg < 1.0:
            issues.append({
                "type": "platform_underperforming",
                "severity": "high",
                "message": f"{platform} averaging {avg:.1f}% engagement. Consider different content strategy.",
            })

    # Recommendations
    recommendations: list[str] = []
    if len(overperformers) > 0:
        top_type = overperformers[-1]
        recommendations.append(f"Double down on content like '{top_type['title'][:50]}' — highest engagement at {top_type['engagement_rate']}%")

    if media_pct < 50:
        recommendations.append("Only {:.0f}% of posts have media — aim for 80%+ visual content".format(media_pct))

    if avg_eng_rate < 2:
        recommendations.append("Overall engagement is low — test hooks, formats, and posting times")

    return {
        "period_days": days,
        "total_posts": len(post_data),
        "avg_engagement_rate": round(avg_eng_rate, 2),
        "avg_content_length": round(avg_length),
        "media_usage_pct": round(media_pct, 1),
        "underperformers": underperformers[:10],
        "overperformers": overperformers[-5:],
        "issues": issues,
        "recommendations": recommendations,
    }
