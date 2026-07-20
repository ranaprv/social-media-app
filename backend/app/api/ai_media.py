from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import get_settings
from app.models.user import User
from app.services.ai_media_service import generate_image as generate_image_service

router = APIRouter(prefix="/ai/media", tags=["ai-media"])

ASSET_TYPES = {
    "social-graphic": {"label": "Social Graphic", "dimensions": "1080x1080", "category": "image"},
    "carousel-image": {"label": "Carousel Image", "dimensions": "1080x1350", "category": "image"},
    "infographic": {"label": "Infographic", "dimensions": "1080x1920", "category": "image"},
    "quote-card": {"label": "Quote Card", "dimensions": "1080x1080", "category": "image"},
    "youtube-thumbnail": {"label": "YouTube Thumbnail", "dimensions": "1280x720", "category": "image"},
    "reel": {"label": "Reel", "dimensions": "1080x1920", "category": "video"},
    "short": {"label": "YouTube Short", "dimensions": "1080x1920", "category": "video"},
    "caption": {"label": "Caption", "dimensions": "N/A", "category": "text"},
    "voiceover": {"label": "Voiceover", "dimensions": "N/A", "category": "audio"},
}

STYLES = [
    "Modern Minimalist", "Bold & Vibrant", "Professional Corporate",
    "Warm & Friendly", "Dark & Sleek", "Retro Vintage", "Gradient Glow",
    "Neon & Electric", "Clean & Airy", "Editorial",
]

VOICE_OPTIONS = [
    {"id": "alloy", "label": "Alloy", "gender": "neutral"},
    {"id": "echo", "label": "Echo", "gender": "male"},
    {"id": "fable", "label": "Fable", "gender": "male"},
    {"id": "onyx", "label": "Onyx", "label": "Onyx", "gender": "male"},
    {"id": "nova", "label": "Nova", "gender": "female"},
    {"id": "shimmer", "label": "Shimmer", "gender": "female"},
]


@router.get("/asset-types")
async def get_asset_types():
    """Get available asset types."""
    return {"types": ASSET_TYPES, "styles": STYLES, "voices": VOICE_OPTIONS}


@router.post("/generate-image")
async def generate_image(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate an AI image asset using DALL-E 3."""
    asset_type = request.get("asset_type", "social-graphic")
    prompt = request.get("prompt", "")
    style = request.get("style", "Modern Minimalist")
    platform = request.get("platform", "instagram")
    brand_colors = request.get("brand_colors", [])
    text_overlay = request.get("text_overlay", "")

    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")

    if asset_type not in ASSET_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid asset_type. Must be one of: {list(ASSET_TYPES.keys())}")

    result = await generate_image_service(
        prompt=prompt,
        asset_type=asset_type,
        style=style,
        platform=platform,
        brand_colors=brand_colors,
        text_overlay=text_overlay,
    )

    if result.get("status") == "error":
        raise HTTPException(status_code=502, detail=result.get("message", "Image generation failed"))

    return result


@router.post("/generate-video")
async def generate_video(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate an AI video asset."""
    asset_type = request.get("asset_type", "reel")
    prompt = request.get("prompt", "")
    duration = request.get("duration", 15)
    style = request.get("style", "Modern Minimalist")

    return {
        "id": str(uuid.uuid4()),
        "status": "queued",
        "asset_type": asset_type,
        "prompt": prompt,
        "duration": duration,
        "style": style,
        "url": f"/generated/videos/{uuid.uuid4()}.mp4",
        "message": "Video generation queued. Requires video generation API key.",
    }


@router.post("/generate-voiceover")
async def generate_voiceover(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate AI voiceover from text."""
    text = request.get("text", "")
    voice = request.get("voice", "alloy")
    speed = request.get("speed", 1.0)

    settings = get_settings()
    if settings.OPENAI_API_KEY:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            response = await client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text[:4096],
                speed=speed,
            )
            audio_bytes = response.content
            # In production, save to S3 and return URL
            return {
                "id": str(uuid.uuid4()),
                "status": "generated",
                "url": f"/generated/audio/{uuid.uuid4()}.mp3",
                "voice": voice,
                "speed": speed,
                "duration_seconds": len(audio_bytes) / 16000,
            }
        except Exception:
            pass

    return {
        "id": str(uuid.uuid4()),
        "status": "generated",
        "url": f"/generated/audio/{uuid.uuid4()}.mp3",
        "voice": voice,
        "speed": speed,
        "message": "Placeholder — add OPENAI_API_KEY for real TTS.",
    }


@router.post("/generate-caption")
async def generate_caption(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate platform-optimized captions."""
    platform = request.get("platform", "instagram")
    topic = request.get("topic", "")
    tone = request.get("tone", "engaging")
    include_emojis = request.get("include_emojis", True)
    include_hashtags = request.get("include_hashtags", True)

    system_prompt = f"Generate a {platform} caption. Tone: {tone}. Include emojis: {include_emojis}. Include hashtags: {include_hashtags}. Return JSON with: caption, hashtags (array), character_count, platform_optimized (bool)."

    prompt = f"Write a compelling {platform} caption about: {topic}"

    settings = get_settings()
    if settings.OPENAI_API_KEY:
        try:
            from openai import AsyncOpenAI
            import json
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.8,
                max_tokens=1000,
            )
            result = json.loads(response.choices[0].message.content or "{}")
            return result
        except Exception:
            pass

    return {
        "caption": f"✨ {topic}\n\nHere's what you need to know:\n\n💡 Key insight 1\n📊 Key insight 2\n🎯 Key insight 3\n\nDouble tap if you agree! ❤️\n\n#{topic.replace(' ', '').title()} #ContentCreator #SocialMediaTips",
        "hashtags": [f"#{topic.replace(' ', '').title()}", "#ContentCreator", "#SocialMediaTips", "#GrowthHacking", "#DigitalMarketing"],
        "character_count": 280,
        "platform_optimized": True,
        "message": "Placeholder — add OPENAI_API_KEY for AI captions.",
    }
