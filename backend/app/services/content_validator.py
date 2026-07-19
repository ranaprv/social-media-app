"""Content validation — enforces platform-specific limits before scheduling.

Use this before creating a PostPlatform row or before publishing.
"""
from typing import Any

from app.services.publishers.base import PlatformPublisher, ContentLimits


# Static limits for platforms not yet implemented as PlatformPublisher subclasses
PLATFORM_LIMITS: dict[str, dict[str, Any]] = {
    "instagram": {
        "max_caption_length": 2200,
        "max_media_count": 10,
        "supported_media_types": ["image", "reel", "carousel", "video"],
        "supported_image_formats": ["jpg", "jpeg", "png"],
        "supported_video_formats": ["mp4", "mov"],
        "max_video_duration_seconds": 90,  # Reels
    },
    "facebook": {
        "max_caption_length": 63206,
        "max_media_count": 10,
        "supported_media_types": ["image", "video"],
        "supported_image_formats": ["jpg", "jpeg", "png", "gif", "webp"],
        "supported_video_formats": ["mp4", "mov"],
        "max_video_duration_seconds": 14400,  # 4 hours
    },
    "youtube": {
        "max_caption_length": 5000,  # Description
        "max_title_length": 100,
        "max_media_count": 1,
        "supported_media_types": ["video", "image"],
        "supported_image_formats": ["jpg", "jpeg", "png", "gif", "bmp"],
        "supported_video_formats": ["mp4", "avi", "mov", "wmv", "mkv", "flv", "webm"],
        "max_video_duration_seconds": 43200,  # 12 hours
        "max_video_size_mb": 256000,  # 256 GB
    },
    "tiktok": {
        "max_caption_length": 2200,
        "max_media_count": 1,
        "supported_media_types": ["video"],
        "supported_video_formats": ["mp4", "mov"],
        "max_video_duration_seconds": 600,  # 10 minutes
    },
    "linkedin": {
        "max_caption_length": 3000,
        "max_media_count": 5,
        "supported_media_types": ["image", "video", "document"],
        "supported_image_formats": ["jpg", "jpeg", "png", "gif"],
        "supported_video_formats": ["mp4"],
        "max_video_duration_seconds": 600,
    },
    "x": {
        "max_caption_length": 280,
        "max_media_count": 4,
        "supported_media_types": ["image", "video", "gif"],
        "supported_image_formats": ["jpg", "jpeg", "png", "gif", "webp"],
        "supported_video_formats": ["mp4"],
        "max_video_duration_seconds": 140,
    },
}


def get_limits(platform: str) -> ContentLimits | dict[str, Any] | None:
    """Get content limits for a platform."""
    # Try the PlatformPublisher first
    from app.services.publishers import get_publisher
    publisher = get_publisher(platform)
    if publisher:
        return publisher.content_limits()

    # Fall back to static definitions
    return PLATFORM_LIMITS.get(platform)


def validate_caption(caption: str, platform: str) -> list[str]:
    """Validate caption length for a platform. Returns errors (empty = OK)."""
    limits = get_limits(platform)
    if not limits:
        return [f"Unknown platform: {platform}"]

    max_len = (
        limits.max_caption_length
        if isinstance(limits, ContentLimits)
        else limits.get("max_caption_length", 999999)
    )

    errors: list[str] = []
    if len(caption) > max_len:
        errors.append(
            f"Caption exceeds {max_len} characters for {platform} "
            f"(got {len(caption)})"
        )
    return errors


def validate_media(
    media_assets: list[dict[str, Any]], platform: str
) -> list[str]:
    """Validate media files for a platform. Returns errors (empty = OK)."""
    limits = get_limits(platform)
    if not limits:
        return [f"Unknown platform: {platform}"]

    if isinstance(limits, ContentLimits):
        max_count = limits.max_media_count
        supported_types = limits.supported_media_types
    else:
        max_count = limits.get("max_media_count", 0)
        supported_types = limits.get("supported_media_types", [])

    errors: list[str] = []

    if len(media_assets) > max_count:
        errors.append(
            f"Too many media files for {platform}: {len(media_assets)} (max {max_count})"
        )

    for i, asset in enumerate(media_assets):
        asset_type = asset.get("content_type", asset.get("type", ""))
        if asset_type and supported_types and asset_type not in supported_types:
            errors.append(
                f"Media {i+1}: '{asset_type}' not supported on {platform}. "
                f"Supported: {', '.join(supported_types)}"
            )

    return errors


def validate_post(
    caption: str,
    platform: str,
    media_assets: list[dict[str, Any]] | None = None,
) -> list[str]:
    """Full validation: caption + media. Returns all errors (empty = OK)."""
    errors = validate_caption(caption, platform)
    if media_assets:
        errors.extend(validate_media(media_assets, platform))
    return errors
