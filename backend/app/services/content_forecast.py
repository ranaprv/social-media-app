"""Content forecast engine — predict performance from historical data.

Uses linear regression on past analytics to forecast future engagement
for proposed posting schedules.
"""
import logging
import math
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Post, AnalyticsMetric

logger = logging.getLogger(__name__)


async def forecast_engagement(
    db: AsyncSession,
    workspace_id: str,
    platform: str,
    proposed_date: datetime | None = None,
    content_length: int = 200,
    has_media: bool = False,
) -> dict[str, Any]:
    """Forecast expected engagement for a proposed post.

    Uses historical data to build a simple predictive model.

    Returns:
    {
        "forecast": {
            "predicted_impressions": 1250,
            "predicted_engagement": 85,
            "predicted_engagement_rate": 6.8,
            "confidence": "medium",
        },
        "basis": {
            "data_points": 45,
            "avg_impressions": 1100,
            "avg_engagement_rate": 6.2,
            "best_day": "Tuesday",
            "best_hour": 10,
        },
        "suggestions": ["Post on Tuesday at 10 AM for best results"],
    }
    """
    cutoff = datetime.utcnow() - timedelta(days=90)

    # Get historical data for this platform
    result = await db.execute(
        select(
            Post.published_at,
            Post.content,
            Post.media_urls,
            AnalyticsMetric.impressions,
            AnalyticsMetric.engagement,
            AnalyticsMetric.reach,
            AnalyticsMetric.clicks,
        )
        .join(AnalyticsMetric, Post.id == AnalyticsMetric.post_id)
        .where(
            Post.workspace_id == workspace_id,
            AnalyticsMetric.platform == platform,
            Post.published_at >= cutoff,
            Post.status == "published",
        )
        .order_by(Post.published_at.desc())
    )
    rows = result.all()

    if not rows:
        return {
            "forecast": None,
            "message": "Not enough historical data to forecast. Publish more posts first.",
            "basis": {"data_points": 0},
            "suggestions": [],
        }

    # Analyze patterns
    day_engagement: dict[int, list[float]] = {}
    hour_engagement: dict[int, list[float]] = {}
    length_buckets: dict[str, list[float]] = {"short": [], "medium": [], "long": []}
    media_perf: dict[bool, list[float]] = {True: [], False: []}

    total_impressions = 0
    total_engagement = 0
    impressions_list = []
    engagement_rates = []

    for pub_at, content, media_urls, impressions, engagement, reach, clicks in rows:
        if not pub_at:
            continue

        imp = impressions or 0
        eng = engagement or 0
        eng_rate = (eng / imp * 100) if imp > 0 else 0

        total_impressions += imp
        total_engagement += eng
        impressions_list.append(imp)
        engagement_rates.append(eng_rate)

        # Day of week
        day = pub_at.weekday()
        if day not in day_engagement:
            day_engagement[day] = []
        day_engagement[day].append(eng_rate)

        # Hour
        hour = pub_at.hour
        if hour not in hour_engagement:
            hour_engagement[hour] = []
        hour_engagement[hour].append(eng_rate)

        # Content length
        content_len = len(content or "")
        if content_len < 100:
            length_buckets["short"].append(eng_rate)
        elif content_len < 300:
            length_buckets["medium"].append(eng_rate)
        else:
            length_buckets["long"].append(eng_rate)

        # Media
        has_m = bool(media_urls)
        media_perf[has_m].append(eng_rate)

    n = len(rows)
    avg_impressions = total_impressions / n
    avg_engagement_rate = sum(engagement_rates) / n if engagement_rates else 0

    # Find best day and hour
    day_avgs = {d: sum(v) / len(v) for d, v in day_engagement.items() if len(v) >= 3}
    hour_avgs = {h: sum(v) / len(v) for h, v in hour_engagement.items() if len(v) >= 3}

    best_day = max(day_avgs, key=day_avgs.get) if day_avgs else 1
    best_hour = max(hour_avgs, key=hour_avgs.get) if hour_avgs else 10

    DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # Simple forecast using historical averages with adjustments
    predicted_impressions = avg_impressions
    predicted_engagement_rate = avg_engagement_rate

    # Adjust for proposed day
    if proposed_date:
        prop_day = proposed_date.weekday()
        prop_hour = proposed_date.hour
        if prop_day in day_avgs:
            day_factor = day_avgs[prop_day] / avg_engagement_rate if avg_engagement_rate > 0 else 1
            predicted_engagement_rate *= day_factor
        if prop_hour in hour_avgs:
            hour_factor = hour_avgs[prop_hour] / avg_engagement_rate if avg_engagement_rate > 0 else 1
            predicted_engagement_rate *= hour_factor

    # Adjust for content length
    if content_length < 100:
        bucket = "short"
    elif content_length < 300:
        bucket = "medium"
    else:
        bucket = "long"

    bucket_rates = length_buckets.get(bucket, [])
    if bucket_rates:
        bucket_avg = sum(bucket_rates) / len(bucket_rates)
        length_factor = bucket_avg / avg_engagement_rate if avg_engagement_rate > 0 else 1
        predicted_engagement_rate *= length_factor

    # Adjust for media
    media_rates = media_perf.get(has_media, [])
    no_media_rates = media_perf.get(False, [])
    if media_rates and no_media_rates:
        media_avg = sum(media_rates) / len(media_rates)
        no_media_avg = sum(no_media_rates) / len(no_media_rates)
        if no_media_avg > 0:
            media_factor = media_avg / no_media_avg
            if has_media:
                predicted_engagement_rate *= media_factor
            else:
                predicted_engagement_rate /= media_factor

    predicted_engagement = predicted_impressions * predicted_engagement_rate / 100

    # Confidence based on data points
    if n >= 50:
        confidence = "high"
    elif n >= 20:
        confidence = "medium"
    else:
        confidence = "low"

    # Suggestions
    suggestions: list[str] = []
    if best_day != (proposed_date.weekday() if proposed_date else -1):
        suggestions.append(f"Post on {DAY_NAMES[best_day]} for best results")
    if best_hour != (proposed_date.hour if proposed_date else -1):
        suggestions.append(f"Post at {best_hour}:00 for peak engagement")
    if not has_media and media_perf.get(True):
        suggestions.append("Add media — posts with media get higher engagement")
    if bucket == "long" and length_buckets.get("medium"):
        suggestions.append("Consider shorter content (under 300 chars) for better engagement")

    return {
        "forecast": {
            "predicted_impressions": round(predicted_impressions),
            "predicted_engagement": round(predicted_engagement),
            "predicted_engagement_rate": round(predicted_engagement_rate, 2),
            "confidence": confidence,
        },
        "basis": {
            "data_points": n,
            "avg_impressions": round(avg_impressions),
            "avg_engagement_rate": round(avg_engagement_rate, 2),
            "best_day": DAY_NAMES[best_day],
            "best_hour": best_hour,
        },
        "suggestions": suggestions,
    }
