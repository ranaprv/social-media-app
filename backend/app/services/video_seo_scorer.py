"""Video SEO scoring algorithm — composite score for keyword viability.

Score breakdown (0-100):
  - Difficulty component:  max(0, 30 - keyword_difficulty)  → 30 pts max
  - Volume component:      high=30, medium=20, low=10       → 30 pts max
  - Competition component: low=40, medium=20, high=5        → 40 pts max

Higher score = easier to rank = better opportunity.
"""
import logging

logger = logging.getLogger(__name__)


def compute_video_seo_score(
    keyword_difficulty: int,
    search_volume: str,
    competition_level: str,
) -> int:
    """Compute composite Video SEO score (0-100).

    Low difficulty + high volume + low competition = high score (easy win).
    High difficulty + low volume + high competition = low score (hard to rank).

    Args:
        keyword_difficulty: 1-100 (1 = easy, 100 = impossible)
        search_volume: 'high', 'medium', or 'low'
        competition_level: 'low', 'medium', or 'high'

    Returns:
        int 0-100 composite score
    """
    # Difficulty: lower is better — max 30 points
    difficulty_score = max(0, 30 - keyword_difficulty)

    # Search volume: higher is better — max 30 points
    volume_map = {"high": 30, "medium": 20, "low": 10}
    volume_score = volume_map.get(search_volume.lower(), 15)

    # Competition: lower is better — max 40 points
    competition_map = {"low": 40, "medium": 20, "high": 5}
    competition_score = competition_map.get(competition_level.lower(), 15)

    total = min(100, difficulty_score + volume_score + competition_score)
    return max(0, total)


def compute_thumbnail_ctr_score(predicted_ctr: float, engagement_rate: float) -> int:
    """Score thumbnail/title variant by predicted CTR and engagement.

    Args:
        predicted_ctr: 0.0-1.0 (click-through rate)
        engagement_rate: 0.0-1.0 (likes/comments/shares ratio)

    Returns:
        int 0-100 score
    """
    ctr_score = min(50, predicted_ctr * 100)
    engagement_score = min(50, engagement_rate * 100)
    return min(100, int(ctr_score + engagement_score))


def score_to_tier(score: int) -> str:
    """Human-readable tier for a score."""
    if score >= 80:
        return "excellent"
    elif score >= 60:
        return "good"
    elif score >= 40:
        return "moderate"
    elif score >= 20:
        return "difficult"
    return "poor"
