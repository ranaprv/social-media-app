"""Post preview — generate platform-specific previews before publishing.

Shows how a post will look on each platform with character counts,
media previews, and formatting.
"""
import logging
import re
from typing import Any

from app.services.cross_post_templates import PLATFORM_TEMPLATES

logger = logging.getLogger(__name__)


def generate_preview(
    content: str,
    platform: str,
    media_urls: list[str] | None = None,
    title: str | None = None,
) -> dict[str, Any]:
    """Generate a preview of how the post will look on a platform.

    Returns formatted preview with truncation, hashtag display,
    and platform-specific rendering.
    """
    template = PLATFORM_TEMPLATES.get(platform, {})
    max_caption = template.get("max_caption", 9999)
    optimal_range = template.get("optimal_caption_range", (0, 9999))

    # Check if content needs truncation
    is_truncated = len(content) > max_caption
    display_content = content[:max_caption] + "..." if is_truncated else content

    # Extract hashtags
    hashtags = re.findall(r"#\w+", display_content)
    content_without_hashtags = re.sub(r"#\w+", "", display_content).strip()

    # Platform-specific preview formatting
    preview_text = display_content
    if platform == "x" and len(display_content) > 280:
        preview_text = display_content[:277] + "..."

    # Calculate engagement indicators
    has_question = "?" in content
    has_emoji = bool(re.search(r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]", content))
    word_count = len(content.split())

    # Platform-specific notes
    notes: list[str] = []
    if platform == "instagram" and len(content) > 125:
        notes.append("Content after 125 chars hidden behind 'more' button")
    if platform == "x" and len(content) > 200:
        notes.append("Long tweets get less engagement — consider a thread")
    if not has_question:
        notes.append("Consider adding a question to boost comments")
    if not has_emoji and platform in ("instagram", "facebook"):
        notes.append("Add emojis to increase visual engagement")

    return {
        "platform": platform,
        "preview": preview_text,
        "title_preview": title[:100] if title else None,
        "char_count": len(content),
        "max_chars": max_caption,
        "is_truncated": is_truncated,
        "optimal_range": optimal_range,
        "in_optimal_range": optimal_range[0] <= len(content) <= optimal_range[1],
        "hashtags": hashtags,
        "hashtag_count": len(hashtags),
        "media_count": len(media_urls) if media_urls else 0,
        "word_count": word_count,
        "has_question": has_question,
        "has_emoji": has_emoji,
        "notes": notes,
        "platform_style": {
            "line_breaks": template.get("line_breaks", True),
            "emoji_usage": template.get("emoji_usage", "moderate"),
            "tone": template.get("tone", "professional"),
        },
    }


def generate_multi_platform_previews(
    content: str,
    platforms: list[str],
    media_urls: list[str] | None = None,
    title: str | None = None,
) -> dict[str, dict[str, Any]]:
    """Generate previews for multiple platforms."""
    return {
        platform: generate_preview(content, platform, media_urls, title)
        for platform in platforms
    }
