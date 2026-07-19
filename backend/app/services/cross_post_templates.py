"""Cross-posting templates — adapt content for each platform.

Templates define how to transform a base post into platform-specific
content (caption length, hashtag format, media requirements, etc.).
"""
import logging
from typing import Any

logger = logging.getLogger(__name__)


# Platform-specific content adaptation rules
PLATFORM_TEMPLATES: dict[str, dict[str, Any]] = {
    "linkedin": {
        "name": "LinkedIn",
        "max_caption": 3000,
        "optimal_caption_range": (150, 300),
        "hashtag_format": "hashtag",  # #Topic
        "max_hashtags": 5,
        "cta_style": "question",  # End with a question for engagement
        "media_preference": "image",
        "tone": "professional",
        "line_breaks": True,  # Use line breaks for readability
        "emoji_usage": "minimal",
        "best_practices": [
            "Start with a hook in the first 2 lines",
            "Use line breaks for readability",
            "End with a question or CTA",
            "Tag relevant people/companies",
            "Share personal insights, not just links",
        ],
    },
    "x": {
        "name": "X (Twitter)",
        "max_caption": 280,
        "optimal_caption_range": (100, 200),
        "hashtag_format": "inline",  # #Topic inline
        "max_hashtags": 2,
        "cta_style": "retweet",  # Ask for RT
        "media_preference": "image",
        "tone": "casual",
        "line_breaks": False,
        "emoji_usage": "moderate",
        "best_practices": [
            "Keep it under 200 chars for best engagement",
            "Use threads for longer content",
            "Include 1-2 relevant hashtags",
            "Post at peak hours (12-3 PM)",
            "Engage with replies quickly",
        ],
    },
    "instagram": {
        "name": "Instagram",
        "max_caption": 2200,
        "optimal_caption_range": (125, 200),
        "hashtag_format": "block",  # Hashtags at end
        "max_hashtags": 30,  # Can use up to 30, but 3-5 is optimal
        "optimal_hashtags": 5,
        "cta_style": "save",  # Ask to save/share
        "media_preference": "image",
        "tone": "visual",
        "line_breaks": True,
        "emoji_usage": "heavy",
        "best_practices": [
            "Put key message in first 125 chars (before 'more')",
            "Use 3-5 relevant hashtags",
            "Include a clear CTA (save, share, comment)",
            "Use line breaks for readability",
            "Reels get 2x more reach than static posts",
        ],
    },
    "facebook": {
        "name": "Facebook",
        "max_caption": 63206,
        "optimal_caption_range": (80, 250),
        "hashtag_format": "inline",
        "max_hashtags": 3,
        "cta_style": "engage",  # Ask for reactions/comments
        "media_preference": "image",
        "tone": "conversational",
        "line_breaks": True,
        "emoji_usage": "moderate",
        "best_practices": [
            "Keep it concise (80-250 chars optimal)",
            "Use images or videos for 2x more engagement",
            "Ask questions to drive comments",
            "Post when your audience is online",
            "Use Facebook-native video when possible",
        ],
    },
    "youtube": {
        "name": "YouTube",
        "max_caption": 5000,
        "optimal_caption_range": (200, 500),
        "hashtag_format": "tags",  # At end of description
        "max_hashtags": 15,
        "cta_style": "subscribe",  # Ask to subscribe
        "media_preference": "video",
        "tone": "educational",
        "line_breaks": True,
        "emoji_usage": "minimal",
        "best_practices": [
            "Title: 60-70 chars optimal",
            "Description: 200-500 chars in first paragraph",
            "Include timestamps/chapters",
            "Add tags for discoverability",
            "End with subscribe + next video CTA",
            "Custom thumbnail is critical",
        ],
    },
}


def get_template(platform: str) -> dict[str, Any] | None:
    """Get the content adaptation template for a platform."""
    return PLATFORM_TEMPLATES.get(platform)


def adapt_content_for_platform(
    content: str,
    source_platform: str,
    target_platform: str,
) -> dict[str, Any]:
    """Adapt content from one platform format to another.

    Returns adapted content with platform-specific modifications.
    """
    source = PLATFORM_TEMPLATES.get(source_platform, {})
    target = PLATFORM_TEMPLATES.get(target_platform, {})

    if not target:
        return {"content": content, "warnings": [f"Unknown target platform: {target_platform}"]}

    adapted = content
    warnings: list[str] = []

    # Truncate if too long
    max_caption = target.get("max_caption", 999999)
    if len(adapted) > max_caption:
        adapted = adapted[:max_caption - 3] + "..."
        warnings.append(f"Content truncated to {max_caption} chars for {target_platform}")

    # Handle hashtag format
    if target.get("hashtag_format") == "block":
        # Move hashtags to end
        words = adapted.split()
        hashtags = [w for w in words if w.startswith("#")]
        non_hashtags = [w for w in words if not w.startswith("#")]
        if hashtags:
            adapted = " ".join(non_hashtags) + "\n\n" + " ".join(hashtags[:target.get("optimal_hashtags", 5)])
    elif target.get("hashtag_format") == "inline":
        # Keep hashtags inline but limit count
        words = adapted.split()
        hashtags = [w for w in words if w.startswith("#")]
        if len(hashtags) > target.get("max_hashtags", 3):
            max_h = target.get("max_hashtags", 3)
            # Keep only first N hashtags
            kept = 0
            new_words = []
            for w in words:
                if w.startswith("#"):
                    if kept < max_h:
                        new_words.append(w)
                        kept += 1
                else:
                    new_words.append(w)
            adapted = " ".join(new_words)

    # Remove line breaks if target doesn't support them
    if not target.get("line_breaks", True):
        adapted = adapted.replace("\n", " ")

    return {
        "content": adapted,
        "platform": target_platform,
        "template": target,
        "warnings": warnings,
    }


def get_cross_post_suggestions(
    content: str,
    source_platform: str,
) -> list[dict[str, Any]]:
    """Suggest how to adapt a post for all other platforms."""
    suggestions = []
    for platform, template in PLATFORM_TEMPLATES.items():
        if platform == source_platform:
            continue
        adapted = adapt_content_for_platform(content, source_platform, platform)
        suggestions.append({
            "platform": platform,
            "name": template["name"],
            "adapted_content": adapted["content"],
            "warnings": adapted["warnings"],
            "tips": template["best_practices"][:3],
            "optimal_length": template["optimal_caption_range"],
            "max_length": template["max_caption"],
        })
    return suggestions
