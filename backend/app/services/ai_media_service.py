"""AI Media Service — DALL-E 3 image generation with visual guidelines.

Generates platform-optimized images using DALL-E 3, applies visual
guidelines per platform, and saves to S3 (or returns DALL-E URL).
"""
import logging
import uuid
from typing import Any

from app.core.config import get_settings
from app.services.visual_guidelines import get_visual_guidelines

logger = logging.getLogger(__name__)

# DALL-E 3 supported sizes
DALL_E_SIZES = {
    "1024x1024": "1024x1024",
    "1024x1792": "1024x1792",
    "1792x1024": "1792x1024",
}

# Asset type → DALL-E size mapping (closest match)
ASSET_TO_SIZE = {
    "social-graphic": "1024x1024",
    "carousel-image": "1024x1792",
    "infographic": "1024x1792",
    "quote-card": "1024x1024",
    "youtube-thumbnail": "1792x1024",
}

# Style → DALL-E prompt prefix
STYLE_PROMPTS = {
    "Modern Minimalist": "clean, minimal design with lots of whitespace, simple shapes, modern typography",
    "Bold & Vibrant": "bold vibrant colors, high contrast, energetic composition, eye-catching",
    "Professional Corporate": "professional corporate style, clean lines, business-appropriate, polished",
    "Warm & Friendly": "warm inviting colors, friendly approachable feel, soft lighting, welcoming",
    "Dark & Sleek": "dark moody aesthetic, sleek modern design, dramatic lighting, premium feel",
    "Retro Vintage": "retro vintage aesthetic, nostalgic color palette, classic design elements",
    "Gradient Glow": "vibrant gradient colors, glowing effects, modern digital aesthetic",
    "Neon & Electric": "neon electric colors, dark background, futuristic cyberpunk aesthetic",
    "Clean & Airy": "clean airy design, light colors, open space, fresh feel",
    "Editorial": "editorial magazine style, sophisticated layout, typographic focus",
}


def _build_image_prompt(
    user_prompt: str,
    asset_type: str,
    style: str,
    platform: str,
    brand_colors: list[str] | None = None,
    text_overlay: str = "",
) -> str:
    """Build enhanced DALL-E prompt with visual guidelines context."""
    parts = [user_prompt]

    # Add style
    style_desc = STYLE_PROMPTS.get(style, style)
    parts.append(f"Style: {style_desc}")

    # Add platform context
    guidelines = get_visual_guidelines(platform)
    if guidelines:
        notes = guidelines.get("style_notes", [])
        if notes:
            parts.append(f"Platform notes for {platform}: {'; '.join(notes[:3])}")

    # Add brand colors
    if brand_colors:
        parts.append(f"Brand colors: {', '.join(brand_colors)}")

    # Add text overlay instruction
    if text_overlay:
        parts.append(f"Include text overlay: '{text_overlay}'")

    # DALL-E quality instruction
    parts.append("High quality, professional, social media ready, no watermarks")

    return ". ".join(parts)


def _get_dalle_size(asset_type: str) -> str:
    """Map asset type to DALL-E 3 supported size."""
    return ASSET_TO_SIZE.get(asset_type, "1024x1024")


async def generate_image(
    prompt: str,
    asset_type: str = "social-graphic",
    style: str = "Modern Minimalist",
    platform: str = "instagram",
    brand_colors: list[str] | None = None,
    text_overlay: str = "",
) -> dict[str, Any]:
    """Generate image via DALL-E 3. Returns URL and metadata.

    If S3 is configured, uploads there and returns permanent URL.
    Otherwise returns DALL-E URL (expires in ~1 hour).
    """
    settings = get_settings()

    if not settings.OPENAI_API_KEY:
        return {
            "status": "error",
            "error": "OPENAI_API_KEY not configured",
            "message": "Add OPENAI_API_KEY to .env for image generation.",
        }

    enhanced_prompt = _build_image_prompt(prompt, asset_type, style, platform, brand_colors, text_overlay)
    dalle_size = _get_dalle_size(asset_type)

    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        response = await client.images.generate(
            model="dall-e-3",
            prompt=enhanced_prompt,
            size=dalle_size,
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url
        revised_prompt = response.data[0].revised_prompt

        # Try to save to S3 for permanent URL
        final_url = image_url
        thumbnail_url = None

        try:
            import httpx
            async with httpx.AsyncClient() as http_client:
                img_response = await http_client.get(image_url, timeout=30)
                if img_response.status_code == 200:
                    img_bytes = img_response.content

                    from app.services.storage import storage
                    image_key = f"generated/images/{uuid.uuid4()}.png"
                    s3_url = await storage.upload_file(img_bytes, image_key, "image/png")
                    if s3_url:
                        final_url = s3_url
                        # Generate thumbnail key
                        thumb_key = f"generated/thumbs/{uuid.uuid4()}.png"
                        thumbnail_url = await storage.upload_file(img_bytes, thumb_key, "image/png")
        except Exception as e:
            logger.warning(f"S3 upload failed, using DALL-E URL: {e}")

        asset_id = str(uuid.uuid4())
        dimensions = DALL_E_SIZES.get(dalle_size, "1024x1024")

        return {
            "id": asset_id,
            "status": "generated",
            "asset_type": asset_type,
            "prompt": prompt,
            "enhanced_prompt": enhanced_prompt,
            "revised_prompt": revised_prompt,
            "style": style,
            "platform": platform,
            "url": final_url,
            "thumbnail_url": thumbnail_url or final_url,
            "dimensions": dimensions,
            "text_overlay": text_overlay,
            "provider": "dall-e-3",
            "model": "dall-e-3",
        }

    except Exception as e:
        logger.error(f"DALL-E 3 generation failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "message": f"Image generation failed: {e}",
        }
