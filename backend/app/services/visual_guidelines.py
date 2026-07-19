"""Visual Content Guidelines — per-platform image/video style guides.

Provides visual specifications and design guidelines for each platform.
"""
import logging
from typing import Any

logger = logging.getLogger(__name__)

VISUAL_GUIDELINES = {
    "linkedin": {
        "images": {
            "feed_post": {"size": "1200x627", "aspect_ratio": "1.91:1", "format": "JPG/PNG", "max_size_mb": 100},
            "article_cover": {"size": "744x400", "aspect_ratio": "1.86:1", "format": "JPG/PNG"},
            "carousel": {"size": "1080x1080", "aspect_ratio": "1:1", "max_slides": 10},
            "logo_clearspace": {"size": "400x400", "aspect_ratio": "1:1", "format": "PNG transparent"},
        },
        "video": {
            "feed": {"max_duration": "10 min", "resolution": "1920x1080", "aspect_ratio": "16:9", "format": "MP4"},
            "story": {"max_duration": "60s", "resolution": "1080x1920", "aspect_ratio": "9:16"},
        },
        "color_palette": {"primary": "#0A66C2", "accent": "#004182", "text": "#000000"},
        "typography": {"headline": "Bold, 24-32px", "body": "Regular, 14-16px", "caption": "Light, 12px"},
        "style_notes": [
            "Professional, clean design",
            "Minimal text on images",
            "High-quality photography or custom graphics",
            "Brand colors consistent across posts",
        ],
    },
    "x": {
        "images": {
            "tweet_image": {"size": "1600x900", "aspect_ratio": "16:9", "format": "JPG/PNG/GIF", "max_size_mb": 5},
            "tweet_carousel": {"size": "1600x900", "aspect_ratio": "16:9", "max_images": 4},
            "profile_banner": {"size": "1500x500", "aspect_ratio": "3:1", "format": "JPG/PNG"},
        },
        "video": {
            "tweet_video": {"max_duration": "2:20 free / 10min paid", "resolution": "1920x1080", "format": "MP4", "max_size_mb": 512},
        },
        "color_palette": {"primary": "#000000", "accent": "#1DA1F2", "text": "#000000"},
        "typography": {"tweet": "Regular, 15-16px", "thread_number": "Bold, 14px"},
        "style_notes": [
            "Bold, punchy visuals",
            "High contrast for scroll-stopping",
            "Memes and reactions work well",
            "Keep text minimal on images",
        ],
    },
    "instagram": {
        "images": {
            "feed_post": {"size": "1080x1080", "aspect_ratio": "1:1", "format": "JPG/PNG"},
            "portrait_post": {"size": "1080x1350", "aspect_ratio": "4:5", "format": "JPG/PNG"},
            "carousel": {"size": "1080x1080 or 1080x1350", "aspect_ratio": "1:1 or 4:5", "max_slides": 10},
            "story": {"size": "1080x1920", "aspect_ratio": "9:16", "format": "JPG/PNG"},
            "profile_photo": {"size": "320x320", "aspect_ratio": "1:1"},
        },
        "video": {
            "reel": {"max_duration": "90s", "resolution": "1080x1920", "aspect_ratio": "9:16", "format": "MP4"},
            "igtv": {"max_duration": "60 min", "resolution": "1920x1080", "aspect_ratio": "9:16 or 16:9"},
        },
        "color_palette": {"primary": "#E4405F", "accent": "#833AB4", "gradient": "#FCAF45"},
        "typography": {"caption": "Regular, 14-16px", "story_text": "Bold, 24-48px", "hashtag": "Regular, 12px"},
        "style_notes": [
            "Aesthetic, visually cohesive grid",
            "Consistent color palette across posts",
            "Faces and people perform best",
            "Carousel posts get 3x more engagement",
            "Reels prioritized by algorithm",
        ],
    },
    "facebook": {
        "images": {
            "feed_post": {"size": "1200x630", "aspect_ratio": "1.91:1", "format": "JPG/PNG"},
            "share_image": {"size": "1200x630", "aspect_ratio": "1.91:1", "format": "JPG/PNG"},
            "cover_photo": {"size": "820x312", "aspect_ratio": "2.63:1"},
            "event_cover": {"size": "1920x1005", "aspect_ratio": "1.91:1"},
        },
        "video": {
            "feed_video": {"max_duration": "4 hours", "resolution": "1920x1080", "format": "MP4", "max_size_mb": 10240},
            "story": {"max_duration": "60s", "resolution": "1080x1920", "aspect_ratio": "9:16"},
            "live": {"resolution": "1920x1080", "aspect_ratio": "16:9"},
        },
        "color_palette": {"primary": "#1877F2", "accent": "#42B72A", "text": "#000000"},
        "typography": {"post": "Regular, 15-16px", "headline": "Bold, 18-24px"},
        "style_notes": [
            "Conversational, approachable visuals",
            "Faces in images get 2x engagement",
            "Video auto-plays (design for sound-off)",
            "Event covers need high contrast",
        ],
    },
    "youtube": {
        "images": {
            "thumbnail": {"size": "1280x720", "aspect_ratio": "16:9", "format": "JPG/PNG", "max_size_mb": 2},
            "channel_art": {"size": "2560x1440", "aspect_ratio": "16:9", "safe_area": "1546x423"},
            "community_post": {"size": "1920x1080", "aspect_ratio": "16:9"},
        },
        "video": {
            "standard": {"resolution": "1920x1080", "aspect_ratio": "16:9", "format": "MP4", "max_size_mb": 256000},
            "shorts": {"resolution": "1080x1920", "aspect_ratio": "9:16", "max_duration": "60s"},
            "max_duration": "12 hours",
        },
        "color_palette": {"primary": "#FF0000", "accent": "#282828", "text": "#FFFFFF"},
        "typography": {"thumbnail_text": "Bold, 48-72px, high contrast", "description": "Regular, 14px"},
        "style_notes": [
            "Thumbnails are CRITICAL — 90% of click decision",
            "Use faces, emotions, bright colors on thumbnails",
            "Text on thumbnails must be readable at mobile size",
            "Consistent thumbnail style builds brand recognition",
            "First 5 seconds must hook viewer",
        ],
    },
}


def get_visual_guidelines(platform: str) -> dict[str, Any] | None:
    """Get visual guidelines for a platform."""
    return VISUAL_GUIDELINES.get(platform)


def get_all_guidelines() -> dict[str, Any]:
    """Get visual guidelines for all platforms."""
    return VISUAL_GUIDELINES


def get_thumbnail_checklist() -> list[dict[str, str]]:
    """Get YouTube thumbnail best practices checklist."""
    return [
        {"item": "High contrast colors", "why": "Readable at mobile size"},
        {"item": "Face with emotion", "why": "Faces get 30% more clicks"},
        {"item": "Text under 6 words", "why": "Too much text is unreadable"},
        {"item": "1280x720 minimum", "why": "YouTube requirement"},
        {"item": "Consistent brand style", "why": "Builds recognition"},
        {"item": "No misleading content", "why": "YouTube penalizes clickbait"},
    ]
