"""Platform deep features — Reels, Shorts, Articles scheduling.

Platform-specific scheduling for specialized content types.
"""
import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

# Platform deep feature specs
DEEP_FEATURES = {
    "instagram_reels": {
        "name": "Instagram Reels",
        "platform": "instagram",
        "max_duration_seconds": 90,
        "aspect_ratio": "9:16",
        "resolution": "1080x1920",
        "max_file_size_mb": 256,
        "supported_formats": ["mp4", "mov"],
        "features": ["text_overlay", "music", "effects", "polls", "quiz"],
        "best_practices": [
            "Hook in first 3 seconds",
            "Use trending audio",
            "Keep under 30 seconds for best reach",
            "Add text for silent viewers",
            "Use vertical format only",
        ],
    },
    "youtube_shorts": {
        "name": "YouTube Shorts",
        "platform": "youtube",
        "max_duration_seconds": 60,
        "aspect_ratio": "9:16",
        "resolution": "1080x1920",
        "max_file_size_mb": 256,
        "supported_formats": ["mp4", "mov", "webm"],
        "features": ["text_overlay", "music", "filters", "speed_control"],
        "best_practices": [
            "Hook in first 2 seconds",
            "Keep under 40 seconds",
            "Vertical format required",
            "Add #Shorts in title or description",
            "Use captions for accessibility",
        ],
    },
    "linkedin_articles": {
        "name": "LinkedIn Articles",
        "platform": "linkedin",
        "max_title_length": 200,
        "max_content_length": 120000,
        "supported_media": ["images", "links", "code_blocks"],
        "features": ["rich_text", "images", "links", "embeds"],
        "best_practices": [
            "Use a compelling headline",
            "Include 3-5 images",
            "Add internal/external links",
            "Use headers for scannability",
            "End with a question",
        ],
    },
    "facebook_stories": {
        "name": "Facebook Stories",
        "platform": "facebook",
        "max_duration_seconds": 60,
        "aspect_ratio": "9:16",
        "resolution": "1080x1920",
        "max_file_size_mb": 30,
        "supported_formats": ["mp4", "jpg", "png"],
        "features": ["text_overlay", "stickers", "polls", "links"],
        "best_practices": [
            "Keep text large and readable",
            "Use bright colors",
            "Add interactive stickers",
            "Include swipe-up link if available",
        ],
    },
}


def get_deep_feature_specs(platform_feature: str) -> dict[str, Any]:
    """Get specs for a platform deep feature."""
    return DEEP_FEATURES.get(platform_feature, {})


def get_available_deep_features(platform: str | None = None) -> list[dict[str, Any]]:
    """Get available deep features, optionally filtered by platform."""
    features = []
    for key, spec in DEEP_FEATURES.items():
        if platform and spec.get("platform") != platform:
            continue
        features.append({
            "key": key,
            "name": spec["name"],
            "platform": spec["platform"],
            "max_duration": spec.get("max_duration_seconds"),
            "aspect_ratio": spec.get("aspect_ratio"),
        })
    return features


async def validate_deep_feature_content(
    content: dict[str, Any],
    feature_type: str,
) -> dict[str, Any]:
    """Validate content against deep feature requirements."""
    spec = DEEP_FEATURES.get(feature_type)
    if not spec:
        return {"error": f"Unknown feature type: {feature_type}"}

    issues: list[str] = []

    # Duration check
    duration = content.get("duration_seconds", 0)
    max_duration = spec.get("max_duration_seconds")
    if max_duration and duration > max_duration:
        issues.append(f"Duration {duration}s exceeds max {max_duration}s")

    # Aspect ratio check
    width = content.get("width", 0)
    height = content.get("height", 0)
    if width and height and spec.get("aspect_ratio"):
        expected = spec["aspect_ratio"]
        if ":" in expected:
            parts = expected.split(":")
            expected_ratio = int(parts[0]) / int(parts[1])
            actual_ratio = width / height
            if abs(actual_ratio - expected_ratio) > 0.15:
                issues.append(f"Aspect ratio {actual_ratio:.2f} doesn't match {expected}")

    # Format check
    fmt = content.get("format", "")
    supported = spec.get("supported_formats", [])
    if fmt and supported and fmt.lower() not in supported:
        issues.append(f"Format '{fmt}' not supported. Use: {', '.join(supported)}")

    return {
        "feature_type": feature_type,
        "spec": spec,
        "issues": issues,
        "is_valid": len(issues) == 0,
    }
