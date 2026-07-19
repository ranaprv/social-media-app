"""Content quality rubric — score content on 10 dimensions.

Provides detailed quality scoring across multiple dimensions
with actionable improvement suggestions.
"""
import logging
from typing import Any

logger = logging.getLogger(__name__)

RUBRIC_DIMENSIONS = [
    {"id": "clarity", "name": "Clarity", "weight": 0.15, "description": "Is the message clear and easy to understand?"},
    {"id": "engagement", "name": "Engagement Potential", "weight": 0.15, "description": "Will this drive likes, comments, shares?"},
    {"id": "relevance", "name": "Relevance", "weight": 0.12, "description": "Is it relevant to the audience and platform?"},
    {"id": "originality", "name": "Originality", "weight": 0.10, "description": "Is this unique or just rehashed content?"},
    {"id": "brand_alignment", "name": "Brand Alignment", "weight": 0.10, "description": "Does it match the brand voice and values?"},
    {"id": "platform_optimization", "name": "Platform Optimization", "weight": 0.12, "description": "Is it optimized for the target platform?"},
    {"id": "cta_effectiveness", "name": "CTA Effectiveness", "weight": 0.08, "description": "Is there a clear, compelling call to action?"},
    {"id": "visual_appeal", "name": "Visual Appeal", "weight": 0.08, "description": "Will the media/visuals support the message?"},
    {"id": "readability", "name": "Readability", "weight": 0.05, "description": "Is the text well-formatted and easy to scan?"},
    {"id": "compliance", "name": "Compliance", "weight": 0.05, "description": "Does it meet platform guidelines and regulations?"},
]


def score_content_rubric(
    content: str,
    platform: str,
    media_count: int = 0,
    has_cta: bool = False,
    brand_voice: str | None = None,
    target_audience: str | None = None,
) -> dict[str, Any]:
    """Score content across 10 quality dimensions.

    Returns dimension scores (0-100) and an overall weighted score.
    """
    scores: dict[str, dict[str, Any]] = {}
    content_len = len(content)
    word_count = len(content.split())

    # 1. Clarity
    has_simple_sentences = content.count(".") <= max(word_count / 10, 3)
    no_jargon = not any(w in content.lower() for w in ["synergy", "leverage", "paradigm", "holistic"])
    clarity_score = 70
    if has_simple_sentences:
        clarity_score += 15
    if no_jargon:
        clarity_score += 10
    if content_len < 500:
        clarity_score += 5
    scores["clarity"] = {"score": min(clarity_score, 100), "notes": "Clear and concise" if clarity_score > 80 else "Consider simplifying"}

    # 2. Engagement Potential
    has_question = "?" in content
    has_emoji = any(ord(c) > 0x1F600 for c in content)
    has_exclamation = "!" in content
    engagement_score = 50
    if has_question:
        engagement_score += 20
    if has_emoji:
        engagement_score += 10
    if has_exclamation:
        engagement_score += 5
    if media_count > 0:
        engagement_score += 15
    scores["engagement"] = {"score": min(engagement_score, 100), "notes": "High engagement potential" if engagement_score > 70 else "Add questions or media"}

    # 3. Relevance
    relevance_score = 75  # Baseline
    if target_audience:
        relevance_score += 10
    if platform in content.lower():
        relevance_score += 5
    scores["relevance"] = {"score": min(relevance_score, 100), "notes": "Relevant to audience" if relevance_score > 70 else "Ensure audience alignment"}

    # 4. Originality
    words = set(content.lower().split())
    generic_words = {"amazing", "incredible", "best", "top", "ultimate", "secret"}
    generic_count = len(words.intersection(generic_words))
    originality_score = 90 - (generic_count * 10)
    scores["originality"] = {"score": max(originality_score, 30), "notes": "Original content" if originality_score > 70 else "Avoid generic buzzwords"}

    # 5. Brand Alignment
    brand_score = 80
    if brand_voice:
        brand_score = 85
    scores["brand_alignment"] = {"score": brand_score, "notes": "Aligned with brand" if brand_score > 70 else "Review brand guidelines"}

    # 6. Platform Optimization
    from app.services.cross_post_templates import PLATFORM_TEMPLATES
    template = PLATFORM_TEMPLATES.get(platform, {})
    max_caption = template.get("max_caption", 9999)
    optimal = template.get("optimal_caption_range", (0, 9999))

    platform_score = 60
    if optimal[0] <= content_len <= optimal[1]:
        platform_score = 95
    elif content_len <= max_caption:
        platform_score = 75
    else:
        platform_score = 30
    scores["platform_optimization"] = {"score": platform_score, "notes": f"Optimal for {platform}" if platform_score > 80 else f"Adjust for {platform} limits"}

    # 7. CTA Effectiveness
    cta_words = ["comment", "share", "save", "follow", "subscribe", "click", "link", "check out", "what do you think", "drop", "tell me"]
    cta_count = sum(1 for w in cta_words if w in content.lower())
    cta_score = 50 + (cta_count * 15)
    if has_cta:
        cta_score = max(cta_score, 80)
    scores["cta_effectiveness"] = {"score": min(cta_score, 100), "notes": "Strong CTA" if cta_score > 70 else "Add a clear call to action"}

    # 8. Visual Appeal
    visual_score = 50 + (media_count * 15)
    scores["visual_appeal"] = {"score": min(visual_score, 100), "notes": f"{media_count} media files" if media_count > 0 else "Add media for visual appeal"}

    # 9. Readability
    lines = content.split("\n")
    has_line_breaks = len(lines) > 1
    avg_line_len = sum(len(l) for l in lines) / max(len(lines), 1)
    readability_score = 60
    if has_line_breaks:
        readability_score += 20
    if avg_line_len < 100:
        readability_score += 15
    scores["readability"] = {"score": min(readability_score, 100), "notes": "Well-formatted" if readability_score > 70 else "Add line breaks for readability"}

    # 10. Compliance
    compliance_score = 90
    if content_len > max_caption:
        compliance_score = 40
    scores["compliance"] = {"score": compliance_score, "notes": "Compliant" if compliance_score > 70 else "Exceeds platform limits"}

    # Overall score
    overall = sum(
        scores[d["id"]]["score"] * d["weight"]
        for d in RUBRIC_DIMENSIONS
    )
    overall = round(overall)

    # Rating
    if overall >= 85:
        rating = "excellent"
    elif overall >= 70:
        rating = "good"
    elif overall >= 50:
        rating = "fair"
    else:
        rating = "needs_work"

    # Top suggestions
    suggestions = []
    sorted_dims = sorted(scores.items(), key=lambda x: x[1]["score"])
    for dim_id, dim_data in sorted_dims[:3]:
        if dim_data["score"] < 70:
            suggestions.append(dim_data["notes"])

    return {
        "overall_score": overall,
        "rating": rating,
        "dimensions": scores,
        "platform": platform,
        "suggestions": suggestions,
    }
