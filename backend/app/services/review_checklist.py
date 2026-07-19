"""Pre-Publish Review Checklist — quality gate before content goes live.

Generates and validates checklists based on platform requirements.
"""
import logging
from typing import Any

logger = logging.getLogger(__name__)

# Platform-specific checklist items
PLATFORM_CHECKLISTS = {
    "linkedin": [
        {"item": "Hook is compelling (first 2 lines visible)", "category": "content", "critical": True},
        {"item": "Line breaks used for readability", "category": "formatting", "critical": False},
        {"item": "Under 3000 characters", "category": "limits", "critical": True},
        {"item": "3-5 relevant hashtags at end", "category": "hashtags", "critical": False},
        {"item": "CTA or question at end", "category": "engagement", "critical": True},
        {"item": "No engagement pods or follow-for-follow", "category": "compliance", "critical": True},
        {"item": "Tagged relevant people/companies", "category": "engagement", "critical": False},
    ],
    "x": [
        {"item": "Under 280 characters", "category": "limits", "critical": True},
        {"item": "1-2 hashtags max", "category": "hashtags", "critical": False},
        {"item": "No engagement bait (like if you agree)", "category": "compliance", "critical": True},
        {"item": "Clear and concise message", "category": "content", "critical": True},
        {"item": "Consider thread if complex topic", "category": "formatting", "critical": False},
    ],
    "instagram": [
        {"item": "First 125 chars are compelling (before 'more')", "category": "content", "critical": True},
        {"item": "3-5 relevant hashtags at end", "category": "hashtags", "critical": False},
        {"item": "CTA (save, share, tag someone)", "category": "engagement", "critical": True},
        {"item": "Emojis used appropriately", "category": "formatting", "critical": False},
        {"item": "Under 2200 characters", "category": "limits", "critical": True},
        {"item": "No engagement pods", "category": "compliance", "critical": True},
        {"item": "Media meets platform specs (1080x1080 or 1080x1350)", "category": "media", "critical": False},
    ],
    "facebook": [
        {"item": "Under 250 characters for optimal reach", "category": "limits", "critical": False},
        {"item": "Question or engagement prompt", "category": "engagement", "critical": True},
        {"item": "No engagement bait (like if you agree)", "category": "compliance", "critical": True},
        {"item": "Image or video attached", "category": "media", "critical": False},
        {"item": "1-3 hashtags max", "category": "hashtags", "critical": False},
    ],
    "youtube": [
        {"item": "Title under 100 characters", "category": "limits", "critical": True},
        {"item": "Description has keywords in first 200 chars", "category": "seo", "critical": True},
        {"item": "Timestamps included", "category": "formatting", "critical": False},
        {"item": "Subscribe + bell CTA at end", "category": "engagement", "critical": True},
        {"item": "Custom thumbnail uploaded", "category": "media", "critical": True},
        {"item": "No misleading titles or thumbnails", "category": "compliance", "critical": True},
    ],
}

# Universal checklist items
UNIVERSAL_CHECKLIST = [
    {"item": "Brand voice consistent with guidelines", "category": "brand", "critical": True},
    {"item": "Spelling and grammar checked", "category": "quality", "critical": True},
    {"item": "Links tested and working", "category": "quality", "critical": True},
    {"item": "Media files accessible and correct format", "category": "media", "critical": True},
    {"item": "Alt text added to images", "category": "accessibility", "critical": False},
    {"item": "Content aligns with content pillar", "category": "strategy", "critical": False},
]


def get_review_checklist(platform: str) -> list[dict[str, Any]]:
    """Get the review checklist for a platform."""
    platform_items = PLATFORM_CHECKLISTS.get(platform, [])
    return platform_items + UNIVERSAL_CHECKLIST


def validate_checklist(
    checklist: list[dict[str, Any]],
    completed_items: list[str],
) -> dict[str, Any]:
    """Validate a completed checklist and return results."""
    total = len(checklist)
    completed = len([item for item in checklist if item["item"] in completed_items])
    critical_items = [item for item in checklist if item.get("critical")]
    critical_completed = len([item for item in critical_items if item["item"] in completed_items])

    all_critical_done = critical_completed == len(critical_items)
    score = round((completed / max(total, 1)) * 100)

    missing_critical = [
        item["item"] for item in critical_items
        if item["item"] not in completed_items
    ]

    return {
        "score": score,
        "total_items": total,
        "completed": completed,
        "critical_total": len(critical_items),
        "critical_completed": critical_completed,
        "all_critical_done": all_critical_done,
        "missing_critical": missing_critical,
        "ready_to_publish": all_critical_done and score >= 70,
    }


def get_all_platforms() -> list[str]:
    """Get all platforms with checklists."""
    return list(PLATFORM_CHECKLISTS.keys())
