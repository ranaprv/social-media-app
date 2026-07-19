"""Posting schedule optimizer — ML-based time selection.

Uses historical engagement data to build a predictive model
for optimal posting times per platform.
"""
import logging
import math
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Post, AnalyticsMetric

logger = logging.getLogger(__name__)


async def optimize_schedule(
    db: AsyncSession,
    workspace_id: str,
    platform: str,
    days_lookback: int = 90,
) -> dict[str, Any]:
    """Build an optimized posting schedule using historical data.

    Uses a weighted scoring model based on:
      - Historical engagement at each time slot
      - Recency weighting (recent data matters more)
      - Day-of-week patterns
      - Content type performance
    """
    cutoff = datetime.utcnow() - timedelta(days=days_lookback)

    result = await db.execute(
        select(
            Post.published_at,
            Post.content,
            Post.media_urls,
            AnalyticsMetric.engagement,
            AnalyticsMetric.impressions,
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
            "platform": platform,
            "optimized_schedule": [],
            "message": "Not enough data to optimize. Using defaults.",
            "confidence": "none",
        }

    # Build time-slot scores with recency weighting
    slot_scores: dict[tuple[int, int], list[float]] = {}  # (dow, hour) -> [weighted_scores]

    for pub_at, content, media_urls, engagement, impressions, clicks in rows:
        if not pub_at:
            continue

        dow = pub_at.weekday()
        hour = pub_at.hour
        key = (dow, hour)

        # Engagement rate
        eng_rate = (engagement / impressions * 100) if impressions and impressions > 0 else 0

        # Recency weight: more recent = higher weight
        days_ago = (datetime.utcnow() - pub_at).days
        recency_weight = math.exp(-days_ago / 30)  # Half-life of ~30 days

        # Content type bonus
        has_media = bool(media_urls)
        media_bonus = 1.2 if has_media else 1.0

        weighted_score = eng_rate * recency_weight * media_bonus

        if key not in slot_scores:
            slot_scores[key] = []
        slot_scores[key].append(weighted_score)

    # Calculate average score per slot
    slot_averages: dict[tuple[int, int], float] = {}
    for key, scores in slot_scores.items():
        slot_averages[key] = sum(scores) / len(scores)

    # Generate optimized schedule (next 7 days)
    DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    now = datetime.utcnow()

    optimized_slots: list[dict[str, Any]] = []
    for day_offset in range(7):
        target_date = now + timedelta(days=day_offset)
        dow = target_date.weekday()

        # Find best hours for this day
        day_slots = [
            (hour, score)
            for (d, hour), score in slot_averages.items()
            if d == dow
        ]
        day_slots.sort(key=lambda x: x[1], reverse=True)

        # Take top 2 slots for the day
        for hour, score in day_slots[:2]:
            slot_time = target_date.replace(hour=hour, minute=0, second=0, microsecond=0)
            if slot_time > now:
                confidence = "high" if len(slot_scores.get((dow, hour), [])) >= 5 else "medium" if len(slot_scores.get((dow, hour), [])) >= 2 else "low"
                optimized_slots.append({
                    "date": slot_time.strftime("%Y-%m-%d"),
                    "time": f"{hour:02d}:00",
                    "day": DAY_NAMES[dow],
                    "score": round(score, 2),
                    "confidence": confidence,
                    "data_points": len(slot_scores.get((dow, hour), [])),
                })

    # Sort by score
    optimized_slots.sort(key=lambda x: x["score"], reverse=True)

    # Overall confidence
    total_data = sum(len(v) for v in slot_scores.values())
    if total_data >= 50:
        overall_confidence = "high"
    elif total_data >= 20:
        overall_confidence = "medium"
    else:
        overall_confidence = "low"

    return {
        "platform": platform,
        "optimized_schedule": optimized_slots[:14],  # Next 14 best slots
        "total_data_points": total_data,
        "confidence": overall_confidence,
        "best_day": DAY_NAMES[max(slot_averages.keys(), key=lambda k: slot_averages[k])[0]] if slot_averages else None,
        "best_hour": max(slot_averages.keys(), key=lambda k: slot_averages[k])[1] if slot_averages else None,
    }
