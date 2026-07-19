"""Viral Score Predictor — predict shareability before publishing.

Analyzes content characteristics to predict viral potential.
"""
import logging
import math
from typing import Any

logger = logging.getLogger(__name__)


def predict_viral_score(
    content: str,
    platform: str,
    media_count: int = 0,
    has_video: bool = False,
    posting_time_hour: int | None = None,
) -> dict[str, Any]:
    """Predict viral potential of content (0-100 score).

    Analyzes multiple factors:
      - Hook strength (first line)
      - Emotional triggers
      - Shareability factors
      - Platform optimization
      - Content format
    """
    score = 50  # Baseline
    factors: list[dict[str, Any]] = []

    # 1. Hook strength (first 100 chars)
    hook = content[:100].strip()
    hook_score = 50
    hook_triggers = {
        "number": any(c.isdigit() for c in hook[:30]),
        "question": "?" in hook,
        "contradiction": any(w in hook.lower() for w in ["but", "however", "actually", "secret", "truth"]),
        "curiosity": any(w in hook.lower() for w in ["why", "how", "what if", "the real"]),
        "urgency": any(w in hook.lower() for w in ["now", "today", "breaking", "urgent"]),
    }
    trigger_count = sum(hook_triggers.values())
    hook_score = 50 + (trigger_count * 10)
    factors.append({"factor": "hook_strength", "score": hook_score, "triggers": hook_triggers})

    # 2. Emotional triggers
    emotion_words = {
        "positive": {"love", "amazing", "incredible", "beautiful", "inspire", "hope", "joy", "happy"},
        "negative": {"shocking", "outrage", "unbelievable", "disgusting", "terrible", "angry"},
        "curiosity": {"secret", "hidden", "unknown", "mystery", "revealed", "exposed"},
    }
    words = set(content.lower().split())
    emotion_count = sum(len(words.intersection(v)) for v in emotion_words.values())
    emotion_score = min(50 + emotion_count * 15, 100)
    factors.append({"factor": "emotional_triggers", "score": emotion_score, "count": emotion_count})

    # 3. Shareability factors
    share_words = {"share", "tag", "forward", "rt", "repost", "must see", "everyone needs"}
    share_count = len(words.intersection(share_words))
    has_question = "?" in content
    has_list = any(content.count(str(i)) >= 1 for i in range(1, 10))
    share_score = 50
    if share_count > 0:
        share_score += 15
    if has_question:
        share_score += 10
    if has_list:
        share_score += 10
    factors.append({"factor": "shareability", "score": min(share_score, 100), "has_question": has_question, "has_list": has_list})

    # 4. Platform optimization
    platform_scores = {
        "linkedin": {"optimal_length": (150, 300), "bonus_media": 15, "bonus_question": 10},
        "x": {"optimal_length": (100, 200), "bonus_media": 10, "bonus_question": 8},
        "instagram": {"optimal_length": (125, 200), "bonus_media": 20, "bonus_question": 12},
        "facebook": {"optimal_length": (80, 250), "bonus_media": 15, "bonus_question": 10},
        "youtube": {"optimal_length": (200, 500), "bonus_media": 5, "bonus_question": 8},
    }
    ps = platform_scores.get(platform, {"optimal_length": (100, 300), "bonus_media": 10, "bonus_question": 8})
    content_len = len(content)
    opt_min, opt_max = ps["optimal_length"]
    platform_score = 60
    if opt_min <= content_len <= opt_max:
        platform_score = 90
    elif content_len < opt_min:
        platform_score = 70
    else:
        platform_score = 55
    factors.append({"factor": "platform_optimization", "score": platform_score})

    # 5. Media and format bonuses
    media_score = 50
    if media_count > 0:
        media_score += ps["bonus_media"]
    if has_video:
        media_score += 15
    factors.append({"factor": "media_format", "score": min(media_score, 100), "media_count": media_count, "has_video": has_video})

    # 6. Posting time factor
    time_score = 65
    if posting_time_hour is not None:
        if 8 <= posting_time_hour <= 12:
            time_score = 85
        elif 12 < posting_time_hour <= 17:
            time_score = 75
        elif 17 < posting_time_hour <= 21:
            time_score = 65
        else:
            time_score = 40
    factors.append({"factor": "posting_time", "score": time_score})

    # Calculate weighted overall score
    weights = {
        "hook_strength": 0.25,
        "emotional_triggers": 0.20,
        "shareability": 0.20,
        "platform_optimization": 0.15,
        "media_format": 0.10,
        "posting_time": 0.10,
    }
    overall = sum(
        f["score"] * weights.get(f["factor"], 0.1)
        for f in factors
    )
    overall = round(min(overall, 100))

    # Classification
    if overall >= 80:
        classification = "viral_potential"
        label = "High viral potential 🔥"
    elif overall >= 60:
        classification = "shareable"
        label = "Good shareability 👍"
    elif overall >= 40:
        classification = "moderate"
        label = "Moderate potential"
    else:
        classification = "low"
        label = "Low viral potential"

    # Suggestions for improvement
    suggestions: list[str] = []
    if hook_score < 70:
        suggestions.append("Add a stronger hook (number, question, or curiosity gap)")
    if media_count == 0:
        suggestions.append("Add visual content to increase shareability")
    if not has_question:
        suggestions.append("End with a question to boost comments")
    if overall < 60:
        suggestions.append("Keep it shorter and punchier for better engagement")

    return {
        "score": overall,
        "classification": classification,
        "label": label,
        "factors": factors,
        "suggestions": suggestions,
        "platform": platform,
    }
