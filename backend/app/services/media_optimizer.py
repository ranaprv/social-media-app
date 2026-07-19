"""Media optimizer — auto-resize, format convert for each platform.

Analyzes media files and returns platform-specific optimization specs.
Provides resize/crop/convert instructions for images and videos.
"""
import logging
from typing import Any

logger = logging.getLogger(__name__)

# Platform-specific media specs
PLATFORM_MEDIA_SPECS: dict[str, dict[str, Any]] = {
    "linkedin": {
        "image": {
            "recommended_size": (1200, 627),
            "aspect_ratio": "1.91:1",
            "max_size_mb": 100,
            "formats": ["jpg", "jpeg", "png", "gif"],
            "notes": "Landscape preferred. 1200x627 for link previews.",
        },
        "video": {
            "max_duration_seconds": 600,
            "max_size_mb": 200,
            "formats": ["mp4"],
            "recommended_resolution": "1920x1080",
            "aspect_ratio": "16:9",
            "notes": "MP4 with H.264 codec preferred.",
        },
    },
    "x": {
        "image": {
            "recommended_size": (1600, 900),
            "aspect_ratio": "16:9",
            "max_size_mb": 5,
            "formats": ["jpg", "jpeg", "png", "gif", "webp"],
            "max_images": 4,
            "notes": "16:9 landscape or 1:1 square. Max 4 images per tweet.",
        },
        "video": {
            "max_duration_seconds": 140,
            "max_size_mb": 512,
            "formats": ["mp4"],
            "recommended_resolution": "1920x1080",
            "aspect_ratio": "16:9 or 1:1",
            "notes": "Max 2:20 for free tier. H.264 codec.",
        },
        "gif": {
            "max_size_mb": 15,
            "formats": ["gif"],
            "notes": "GIFs auto-convert to video. Keep under 15MB.",
        },
    },
    "instagram": {
        "image": {
            "recommended_size": (1080, 1080),
            "aspect_ratio": "1:1",
            "max_size_mb": 30,
            "formats": ["jpg", "jpeg", "png"],
            "notes": "1:1 square for feed. 1080x1350 for portrait (4:5).",
        },
        "reel": {
            "recommended_size": (1080, 1920),
            "aspect_ratio": "9:16",
            "max_duration_seconds": 90,
            "max_size_mb": 256,
            "formats": ["mp4", "mov"],
            "recommended_resolution": "1080x1920",
            "notes": "Vertical video only. 9:16 aspect ratio required.",
        },
        "carousel": {
            "max_items": 10,
            "min_items": 2,
            "mixed_media": True,
            "notes": "Can mix images and videos. All images should have same aspect ratio.",
        },
    },
    "facebook": {
        "image": {
            "recommended_size": (1200, 630),
            "aspect_ratio": "1.91:1",
            "max_size_mb": 10,
            "formats": ["jpg", "jpeg", "png", "gif", "webp"],
            "notes": "1200x630 for link previews. 1080x1080 for square.",
        },
        "video": {
            "max_duration_seconds": 14400,
            "max_size_mb": 10240,
            "formats": ["mp4", "mov"],
            "recommended_resolution": "1920x1080",
            "aspect_ratio": "16:9",
            "notes": "Up to 4 hours. H.264 preferred.",
        },
    },
    "youtube": {
        "thumbnail": {
            "recommended_size": (1280, 720),
            "aspect_ratio": "16:9",
            "max_size_mb": 2,
            "formats": ["jpg", "jpeg", "png", "gif", "bmp"],
            "notes": "1280x720 minimum. Critical for click-through rate.",
        },
        "video": {
            "max_duration_seconds": 43200,
            "max_size_mb": 256000,
            "formats": ["mp4", "avi", "mov", "wmv", "mkv", "flv", "webm"],
            "recommended_resolution": "1920x1080",
            "aspect_ratio": "16:9",
            "notes": "Up to 12 hours / 256GB. H.264 preferred.",
        },
    },
}


def get_platform_media_specs(platform: str, media_type: str = "image") -> dict[str, Any] | None:
    """Get media specifications for a platform and type."""
    specs = PLATFORM_MEDIA_SPECS.get(platform, {})
    return specs.get(media_type)


def analyze_media_for_platform(
    file_info: dict[str, Any],
    platform: str,
) -> dict[str, Any]:
    """Analyze a media file against platform requirements.

    Args:
        file_info: {"width": int, "height": int, "format": str, "size_mb": float, "duration_seconds": float}
        platform: Target platform.

    Returns optimization recommendations.
    """
    media_type = "video" if file_info.get("duration_seconds") else "image"
    if file_info.get("format") == "gif":
        media_type = "gif"
    if platform == "youtube" and file_info.get("is_thumbnail"):
        media_type = "thumbnail"
    if platform == "instagram" and file_info.get("is_reel"):
        media_type = "reel"

    specs = get_platform_media_specs(platform, media_type)
    if not specs:
        return {
            "status": "unknown",
            "message": f"No specs for {platform}/{media_type}",
        }

    issues: list[str] = []
    recommendations: list[str] = []
    needs_optimization = False

    # Check format
    supported = specs.get("formats", [])
    file_format = file_info.get("format", "").lower()
    if supported and file_format not in supported:
        issues.append(f"Format '{file_format}' not supported. Use: {', '.join(supported)}")
        needs_optimization = True

    # Check file size
    max_size = specs.get("max_size_mb", 999)
    file_size = file_info.get("size_mb", 0)
    if file_size > max_size:
        issues.append(f"File size {file_size}MB exceeds max {max_size}MB")
        needs_optimization = True

    # Check dimensions
    width = file_info.get("width", 0)
    height = file_info.get("height", 0)
    rec_size = specs.get("recommended_size")
    rec_ratio = specs.get("aspect_ratio")

    if rec_size and width and height:
        rec_w, rec_h = rec_size
        if width < rec_w * 0.5 or height < rec_h * 0.5:
            recommendations.append(
                f"Image is small ({width}x{height}). Recommended: {rec_w}x{rec_h}"
            )
            needs_optimization = True

        # Check aspect ratio
        if rec_ratio and width and height:
            actual_ratio = round(width / height, 2)
            if ":" in str(rec_ratio):
                parts = rec_ratio.split(":")
                expected_ratio = round(int(parts[0]) / int(parts[1]), 2)
                if abs(actual_ratio - expected_ratio) > 0.15:
                    recommendations.append(
                        f"Aspect ratio {actual_ratio}:1 doesn't match {rec_ratio}. "
                        f"Crop to {rec_ratio} for best results."
                    )
                    needs_optimization = True

    # Check duration
    if media_type in ("video", "reel", "gif"):
        max_duration = specs.get("max_duration_seconds", 9999)
        duration = file_info.get("duration_seconds", 0)
        if duration > max_duration:
            issues.append(f"Duration {duration}s exceeds max {max_duration}s")
            needs_optimization = True

    # Generate optimization instructions
    instructions: list[dict[str, Any]] = []
    if needs_optimization:
        if rec_size and (width != rec_size[0] or height != rec_size[1]):
            instructions.append({
                "action": "resize",
                "from": f"{width}x{height}",
                "to": f"{rec_size[0]}x{rec_size[1]}",
                "method": "center_crop" if rec_ratio else "fit",
            })

        if file_format and supported and file_format not in supported:
            instructions.append({
                "action": "convert",
                "from": file_format,
                "to": supported[0],
            })

        if file_size > max_size:
            instructions.append({
                "action": "compress",
                "from_mb": file_size,
                "to_mb": round(max_size * 0.9, 1),
                "method": "quality_reduce" if media_type == "image" else "bitrate_reduce",
            })

    return {
        "platform": platform,
        "media_type": media_type,
        "status": "needs_optimization" if needs_optimization else "ok",
        "issues": issues,
        "recommendations": recommendations,
        "instructions": instructions,
        "specs": specs,
    }


def get_optimization_summary(
    media_assets: list[dict[str, Any]],
    platforms: list[str],
) -> dict[str, Any]:
    """Get optimization summary for multiple assets across platforms."""
    results: dict[str, list[dict]] = {}

    for platform in platforms:
        platform_results = []
        for asset in media_assets:
            analysis = analyze_media_for_platform(asset, platform)
            if analysis["status"] == "needs_optimization":
                platform_results.append({
                    "asset_name": asset.get("name", "unknown"),
                    "issues": analysis["issues"],
                    "instructions": analysis["instructions"],
                })
        results[platform] = platform_results

    total_issues = sum(len(v) for v in results.values())

    return {
        "total_assets": len(media_assets),
        "platforms_checked": len(platforms),
        "total_issues": total_issues,
        "by_platform": results,
        "all_clear": total_issues == 0,
    }
