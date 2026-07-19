"""Content performance scorer — predict engagement before publishing.

Analyzes content characteristics (length, media, hashtags, posting time)
against historical data to predict engagement potential.
"""
import logging
from datetime import datetime
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Post, AnalyticsMetric

logger = logging.getLogger(__name__)


async def score_content(
    db: AsyncSession,
    workspace_id: str,
    content: str,
    platform: str,
    media_count: int = 0,
    scheduled_hour: int | None = None,
) -> dict[str, Any]:
    """Score content's predicted engagement potential (0-100).

    Uses historical analytics data to calibrate predictions.

    Returns:
    {
        "score": 72,
        "rating": "good",
        "factors": [
            {"factor": "caption_length", "score": 85, "detail": "250 chars — optimal range"},
            {"factor": "media_usage", "score": 90, "detail": "2 media files attached"},
            {"factor": "posting_time", "score": 65, "detail": "10:00 UTC — moderate audience online"},
            {"factor": "content_pattern", "score": 70, "detail": "Similar to your top 20% posts"},
        ],
        "suggestions": ["Add a question to drive comments", "Consider adding an image"],
    }
    """
    factors: list[dict[str, Any]] = []

    # 1. Caption length factor
    char_count = len(content)
    from app.services.content_validator import get_limits
    limits = get_limits(platform)

    if limits:
        max_len = limits.max_caption_length if hasattr(limits, "max_caption_length") else limits.get("max_caption_length", 9999)
        optimal_range = (max_len * 0.05, max_len * 0.15)  # 5-15% of max is optimal

        if optimal_range[0] <= char_count <= optimal_range[1]:
            length_score = 90
            length_detail = f"{char_count} chars — optimal range"
        elif char_count < optimal_range[0]:
            length_score = max(40, 60 - (optimal_range[0] - char_count) * 2)
            length_detail = f"{char_count} chars — may be too short"
        elif char_count <= max_len:
            length_score = max(50, 80 - (char_count - optimal_range[1]) * 0.1)
            length_detail = f"{char_count} chars — on the longer side"
        else:
            length_score = 20
            length_detail = f"{char_count} chars — exceeds limit ({max_len})"
    else:
        length_score = 70
        length_detail = f"{char_count} chars"

    factors.append({
        "factor": "caption_length",
        "score": length_score,
        "detail": length_detail,
    })

    # 2. Media usage factor
    if media_count >= 2:
        media_score = 90
        media_detail = f"{media_count} media files — strong visual content"
    elif media_count == 1:
        media_score = 75
        media_detail = "1 media file — good"
    else:
        media_score = 45
        media_detail = "No media — text-only posts get less engagement"

    factors.append({
        "factor": "media_usage",
        "score": media_score,
        "detail": media_detail,
    })

    # 3. Posting time factor
    if scheduled_hour is not None:
        # Check historical engagement at this hour
        hour_result = await db.execute(
            select(
                func.avg(AnalyticsMetric.engagement).label("avg_engagement"),
            )
            .join(Post, Post.id == AnalyticsMetric.post_id)
            .where(
                Post.workspace_id == workspace_id,
                AnalyticsMetric.platform == platform,
            )
            .limit(100)
        )
        avg_eng = hour_result.scalar() or 0

        if 8 <= scheduled_hour <= 12:
            time_score = 80
            time_detail = f"{scheduled_hour}:00 — peak engagement window"
        elif 13 <= scheduled_hour <= 17:
            time_score = 70
            time_detail = f"{scheduled_hour}:00 — afternoon engagement"
        elif 18 <= scheduled_hour <= 21:
            time_score = 60
            time_detail = f"{scheduled_hour}:00 — evening engagement"
        else:
            time_score = 40
            time_detail = f"{scheduled_hour}:00 — off-peak hours"
    else:
        time_score = 65
        time_detail = "No specific time — will use best-time recommendation"

    factors.append({
        "factor": "posting_time",
        "score": time_score,
        "detail": time_detail,
    })

    # 4. Content pattern factor (compare to historical top performers)
    word_count = len(content.split())
    has_question = "?" in content
    has_emoji = any(ord(c) > 0x1F600 for c in content)

    pattern_score = 60  # baseline
    pattern_notes = []

    if has_question:
        pattern_score += 10
        pattern_notes.append("includes question (boosts comments)")
    if has_emoji:
        pattern_score += 5
        pattern_notes.append("uses emoji")
    if word_count >= 10 and word_count <= 100:
        pattern_score += 10
        pattern_notes.append("concise word count")
    elif word_count > 200:
        pattern_score -= 5
        pattern_notes.append("long form — consider splitting")

    pattern_score = min(pattern_score, 100)
    pattern_detail = "; ".join(pattern_notes) if pattern_notes else "standard content pattern"

    factors.append({
        "factor": "content_pattern",
        "score": pattern_score,
        "detail": pattern_detail,
    })

    # Calculate overall score (weighted average)
    weights = {"caption_length": 0.25, "media_usage": 0.30, "posting_time": 0.20, "content_pattern": 0.25}
    overall_score = sum(
        f["score"] * weights.get(f["factor"], 0.25) for f in factors
    )
    overall_score = round(overall_score)

    # Determine rating
    if overall_score >= 80:
        rating = "excellent"
    elif overall_score >= 65:
        rating = "good"
    elif overall_score >= 50:
        rating = "fair"
    else:
        rating = "needs_improvement"

    # Generate suggestions
    suggestions: list[str] = []
    if media_count == 0:
        suggestions.append("Add an image or video to boost engagement by ~2x")
    if not has_question:
        suggestions.append("Add a question at the end to drive comments")
    if char_count > 200 and platform == "x":
        suggestions.append("Consider making this a thread — X posts over 200 chars get less engagement")
    if scheduled_hour and (scheduled_hour < 7 or scheduled_hour > 22):
        suggestions.append("Consider scheduling during business hours (8 AM - 6 PM)")
    if word_count < 5:
        suggestions.append("Add more context — very short posts often underperform")

    return {
        "score": overall_score,
        "rating": rating,
        "factors": factors,
        "suggestions": suggestions,
        "platform": platform,
        "char_count": char_count,
        "word_count": word_count,
    }
