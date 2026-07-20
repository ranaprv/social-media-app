"""Storyboard Service — detailed shot-by-shot video planning.

Takes a video script and produces a comprehensive storyboard with:
  - Shot-by-shot breakdown with timing, visuals, audio, transitions
  - Music/mood cues per section
  - Thumbnail concepts (multiple options for A/B testing)
  - Multi-provider image prompts (DALL-E, Midjourney, Stable Diffusion)
  - Platform-specific formatting

No external APIs required — uses LLM for detailed planning.
"""
import logging
from typing import Any

from app.services.llm import call_llm_json

logger = logging.getLogger(__name__)


# Platform-specific video specs
PLATFORM_SPECS = {
    "youtube": {
        "max_duration": 43200,  # 12 hours
        "optimal_short": (15, 60),
        "optimal_long": (300, 900),
        "aspect_ratio": "16:9",
        "resolution": "1920x1080",
        "thumbnail_size": "1280x720",
    },
    "instagram": {
        "max_duration": 90,
        "optimal_short": (15, 60),
        "optimal_long": (60, 90),
        "aspect_ratio": "9:16",
        "resolution": "1080x1920",
        "thumbnail_size": "1080x1080",
    },
    "tiktok": {
        "max_duration": 600,
        "optimal_short": (15, 60),
        "optimal_long": (60, 180),
        "aspect_ratio": "9:16",
        "resolution": "1080x1920",
        "thumbnail_size": "1080x1920",
    },
    "x": {
        "max_duration": 140,
        "optimal_short": (15, 45),
        "optimal_long": (45, 140),
        "aspect_ratio": "16:9",
        "resolution": "1920x1080",
        "thumbnail_size": "1200x675",
    },
    "facebook": {
        "max_duration": 14400,
        "optimal_short": (15, 60),
        "optimal_long": (60, 300),
        "aspect_ratio": "16:9",
        "resolution": "1920x1080",
        "thumbnail_size": "1200x630",
    },
}


async def generate_storyboard(
    script: dict,
    platform: str = "youtube",
    style: str = "professional",
    provider: str = "openai",
    model: str | None = None,
) -> dict[str, Any]:
    """Generate a detailed storyboard from a video script.

    Args:
        script: Video script dict with title, hook, sections, cta
        platform: Target platform
        style: Visual style
        provider: LLM provider
        model: Optional model override

    Returns:
        {
            "storyboard": [...],           # shot-by-shot breakdown
            "thumbnail_concepts": [...],    # 3 thumbnail options for A/B test
            "image_prompts": {...},         # multi-provider image prompts
            "music_cues": [...],            # music/mood suggestions per section
            "transitions": [...],           # transition suggestions
            "platform_specs": {...},        # platform technical specs
            "total_estimated_duration": int,
        }
    """
    spec = PLATFORM_SPECS.get(platform, PLATFORM_SPECS["youtube"])

    # Build the storyboard generation prompt
    sections_text = ""
    for i, section in enumerate(script.get("sections", [])):
        sections_text += (
            f"  Section {i+1}: {section.get('timestamp', 'TBD')}\n"
            f"    Visual: {section.get('visual', 'TBD')}\n"
            f"    Narration: {section.get('narration', 'TBD')}\n"
            f"    Text overlay: {section.get('text_overlay', 'none')}\n\n"
        )

    storyboard_prompt = f"""Create a detailed video storyboard for this script.

Title: {script.get('title', 'Untitled')}
Hook: {script.get('hook', 'No hook')}
Platform: {platform} ({spec['aspect_ratio']}, {spec['resolution']})
Style: {style}
Duration: {script.get('total_duration', 60)} seconds

Script sections:
{sections_text}

CTA: {script.get('cta', 'Follow for more!')}

Generate a detailed storyboard with:

1. SHOT-BY-SHOT BREAKDOWN — for each shot:
   - shot_number
   - timestamp (start-end)
   - duration_seconds
   - visual_description (what the viewer sees — camera angle, subject, background)
   - narration (what's spoken/voiceover)
   - text_overlay (on-screen text)
   - movement (camera or subject movement)
   - mood (emotion/energy of the shot)

2. THUMBNAIL CONCEPTS — 3 options for A/B testing:
   - concept_text (bold text overlay)
   - visual_description (what the thumbnail shows)
   - color_scheme (dominant colors)
   - style (dramatic, clean, minimal, bold)

3. MUSIC CUES — per section:
   - section
   - mood (upbeat, calm, dramatic, etc.)
   - energy_level (1-10)
   - suggested_genre

4. TRANSITIONS — between sections:
   - from_shot
   - to_shot
   - transition_type (cut, fade, zoom, swipe, etc.)

Return ONLY valid JSON."""

    result = await call_llm_json(
        prompt=storyboard_prompt,
        system_prompt=(
            "You are an expert video producer and storyboard artist. "
            "Create detailed, production-ready storyboards. "
            "Be specific about camera angles, lighting, and visual composition. "
            "Return ONLY valid JSON."
        ),
        provider=provider,
        model=model,
        temperature=0.5,
        max_tokens=3000,
    )

    if not result or not isinstance(result, dict):
        # Fallback: create basic storyboard from script sections
        result = _fallback_storyboard(script, spec)

    # Generate multi-provider image prompts for thumbnails
    image_prompts = await _generate_image_prompts(
        title=script.get("title", ""),
        platform=platform,
        style=style,
        thumbnail_concepts=result.get("thumbnail_concepts", []),
        provider=provider,
        model=model,
    )

    result["image_prompts"] = image_prompts
    result["platform_specs"] = spec

    return result


async def _generate_image_prompts(
    title: str,
    platform: str,
    style: str,
    thumbnail_concepts: list[dict],
    provider: str,
    model: str | None,
) -> dict[str, Any]:
    """Generate image prompts for multiple AI image generators."""
    spec = PLATFORM_SPECS.get(platform, PLATFORM_SPECS["youtube"])

    prompt_request = f"""Generate image generation prompts for a {platform} thumbnail about: "{title}"
Style: {style}
Dimensions: {spec['thumbnail_size']}
Aspect ratio: {spec['aspect_ratio']}

Create prompts for 3 different image generators:

1. DALL-E 3 prompt: Detailed natural language description (max 400 chars)
2. Midjourney prompt: With --ar, --style, --v parameters
3. Stable Diffusion prompt: With quality tags, negative prompt

Return JSON with:
{{
  "dalle": "prompt text for DALL-E 3",
  "midjourney": "prompt text --ar {spec['aspect_ratio'].replace(':', ':')} --style raw --v 6",
  "stable_diffusion": "prompt text",
  "negative_prompt": "things to avoid in the image"
}}"""

    prompts = await call_llm_json(
        prompt=prompt_request,
        system_prompt="You are an expert AI image prompt engineer. Create optimized prompts for each platform.",
        provider=provider,
        model=model,
        temperature=0.5,
        max_tokens=800,
    )

    if not prompts or not isinstance(prompts, dict):
        # Fallback prompts
        prompts = {
            "dalle": f"A professional {style} thumbnail for '{title}' on {platform}. Bold text, vibrant colors, eye-catching composition.",
            "midjourney": f"{title} thumbnail, {style} style, bold typography, vibrant --ar {spec['aspect_ratio'].replace(':', ':')} --style raw --v 6",
            "stable_diffusion": f"(masterpiece, best quality:1.4), {title}, {style} style, bold text overlay, professional thumbnail, vibrant colors",
            "negative_prompt": "blurry, low quality, text errors, watermark, cropped",
        }

    return prompts


def _fallback_storyboard(script: dict, spec: dict) -> dict:
    """Create a basic storyboard from script sections when LLM fails."""
    storyboard = []
    for i, section in enumerate(script.get("sections", [])):
        storyboard.append({
            "shot_number": i + 1,
            "timestamp": section.get("timestamp", f"0:{i*15:02d}-0:{(i+1)*15:02d}"),
            "duration_seconds": 15,
            "visual_description": section.get("visual", "B-roll footage"),
            "narration": section.get("narration", ""),
            "text_overlay": section.get("text_overlay", ""),
            "movement": "static" if i == 0 else "slow pan",
            "mood": "engaging" if i == 0 else "informative",
        })

    return {
        "storyboard": storyboard,
        "thumbnail_concepts": [
            {
                "concept_text": script.get("title", "Watch This"),
                "visual_description": "Bold text on gradient background",
                "color_scheme": ["#FF0000", "#000000", "#FFFFFF"],
                "style": "bold",
            }
        ],
        "music_cues": [
            {"section": "all", "mood": "upbeat", "energy_level": 7, "genre": "electronic"}
        ],
        "transitions": [],
        "total_estimated_duration": script.get("total_duration", 60),
    }
