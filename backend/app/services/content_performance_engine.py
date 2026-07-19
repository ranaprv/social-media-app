"""Content Performance Scoring Engine — predict performance before publish.

Advanced multi-factor scoring that combines historical data with
content characteristics for more accurate predictions.
"""
import logging
import math
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Post, AnalyticsMetric

logger = logging.getLogger(__name__)


async def score_content_performance(
    db: AsyncSession,
    workspace_id: str,
    content: str,
    platform: str,
    media_count: int = 0,
    has_video: bool = False,
    posting_hour: int | None = None,
    content_type: str = "text",
) -> dict[str, Any]:
    """Advanced content performance scoring using historical data + content analysis.

    Combines:
      1. Historical engagement patterns for this workspace
      2. Content characteristic analysis
      3. Platform-specific optimization rules
      4. Time-based adjustments
    """
    # Get historical baseline for this platform
    baseline = await _get_baseline(db, workspace_id, platform)

    # Content analysis score
    content_score = _analyze_content(content, platform)

    # Media bonus
    media_score = _analyze_media(media_count, has_video, platform)

    # Time optimization
    time_score = _analyze_timing(posting_hour, platform)

    # Content type bonus
    type_bonus = _content_type_bonus(content_type, platform)

    # Weighted combination
    weights = {
        "content_quality": 0.30,
        "historical_baseline": 0.25,
        "media": 0.15,
        "timing": 0.15,
        "content_type": 0.15,
    }

    overall = (
        content_score * weights["content_quality"] +
        baseline["avg_score"] * weights["historical_baseline"] +
        media_score * weights["media"] +
        time_score * weights["timing"] +
        type_bonus * weights["content_type"]
    )
    overall = round(min(max(overall, 0), 100))

    # Confidence based on data availability
    confidence = "high" if baseline["data_points"] >= 50 else "medium" if baseline["data_points"] >= 20 else "low"

    # Detailed breakdown
    return {
        "score": overall,
        "confidence": confidence,
        "breakdown": {
            "content_quality": round(content_score),
            "historical_baseline": round(baseline["avg_score"]),
            "media": round(media_score),
            "timing": round(time_score),
            "content_type": round(type_bonus),
        },
        "predictions": {
            "estimated_impressions": round(baseline["avg_impressions"] * (overall / 50)),
            "estimated_engagement": round(baseline["avg_engagement"] * (overall / 50)),
            "estimated_engagement_rate": round(baseline["avg_eng_rate"] * (overall / 50), 2),
        },
        "suggestions": _generate_suggestions(content_score, media_score, time_score, platform),
    }


async def _get_baseline(db: AsyncSession, workspace_id: str, platform: str) -> dict:
    """Get historical baseline metrics for a platform."""
    cutoff = datetime.utcnow() - timedelta(days=90)

    result = await db.execute(
        select(
            func.count(Post.id),
            func.avg(AnalyticsMetric.impressions),
            func.avg(AnalyticsMetric.engagement),
        )
        .join(AnalyticsMetric, Post.id == AnalyticsMetric.post_id)
        .where(
            Post.workspace_id == workspace_id,
            AnalyticsMetric.platform == platform,
            Post.published_at >= cutoff,
        )
    )
    row = result.one()

    data_points = row[0] or 0
    avg_impressions = row[1] or 500
    avg_engagement = row[2] or 20
    avg_eng_rate = (avg_engagement / avg_impressions * 100) if avg_impressions > 0 else 4.0

    # Score baseline (normalize to 0-100)
    avg_score = min(avg_eng_rate * 10, 100)

    return {
        "data_points": data_points,
        "avg_impressions": avg_impressions,
        "avg_engagement": avg_engagement,
        "avg_eng_rate": avg_eng_rate,
        "avg_score": avg_score,
    }


def _analyze_content(content: str, platform: str) -> float:
    """Analyze content characteristics and return score."""
    score = 50.0
    words = content.split()
    word_count = len(words)
    char_count = len(content)

    # Hook strength
    hook = content[:100]
    if any(c.isdigit() for c in hook[:30]):
        score += 10
    if "?" in hook:
        score += 8
    if any(w in hook.lower() for w in ["secret", "truth", "why", "how"]):
        score += 7

    # Length optimization
    optimal_ranges = {"linkedin": (150, 300), "x": (80, 200), "instagram": (125, 200), "facebook": (80, 250), "youtube": (200, 500)}
    opt_min, opt_max = optimal_ranges.get(platform, (100, 300))
    if opt_min <= char_count <= opt_max:
        score += 10
    elif char_count < opt_min:
        score += 3
    else:
        score -= 5

    # Emotional triggers
    positive = {"amazing", "love", "incredible", "inspire", "beautiful", "happy"}
    words_set = set(content.lower().split())
    if words_set.intersection(positive):
        score += 5

    # Line breaks for readability
    if content.count("\n") >= 3:
        score += 5

    # Hashtags
    hashtags = [w for w in words if w.startswith("#")]
    optimal_ht = {"linkedin": 4, "x": 1, "instagram": 7, "facebook": 2, "youtube": 5}
    if abs(len(hashtags) - optimal_ht.get(platform, 3)) <= 2:
        score += 3

    return min(max(score, 0), 100)


def _analyze_media(media_count: int, has_video: bool, platform: str) -> float:
    """Score media usage."""
    score = 50.0
    if media_count >= 2:
        score += 25
    elif media_count == 1:
        score += 15
    if has_video:
        score += 20
    if platform == "instagram" and has_video:
        score += 10
    return min(score, 100)


def _analyze_timing(posting_hour: int | None, platform: str) -> float:
    """Score timing optimization."""
    if posting_hour is None:
        return 65.0
    peak_hours = {"linkedin": [8, 9, 10, 12], "x": [12, 13, 17], "instagram": [11, 14, 19], "facebook": [13, 15], "youtube": [15, 21]}
    if posting_hour in peak_hours.get(platform, []):
        return 90.0
    elif 8 <= posting_hour <= 20:
        return 70.0
    return 40.0


def _content_type_bonus(content_type: str, platform: str) -> float:
    """Bonus for optimal content types per platform."""
    bonuses = {
        "linkedin": {"article": 90, "post": 75, "poll": 85, "video": 80},
        "x": {"thread": 90, "tweet": 75, "poll": 85},
        "instagram": {"reel": 95, "carousel": 85, "post": 70, "story": 75},
        "facebook": {"video": 85, "post": 70, "live": 90},
        "youtube": {"short": 90, "video": 85, "community": 70},
    }
    return bonuses.get(platform, {}).get(content_type, 75.0)


def _generate_suggestions(content_score: float, media_score: float, time_score: float, platform: str) -> list[str]:
    """Generate actionable improvement suggestions."""
    suggestions = []
    if content_score < 70:
        suggestions.append("Improve hook — start with a number, question, or curiosity gap")
    if media_score < 70:
        suggestions.append("Add visual content (images or video) to boost engagement")
    if time_score < 70:
        suggestions.append("Post during peak hours for better reach")
    if not suggestions:
        suggestions.append("Content looks well-optimized for " + platform)
    return suggestions
