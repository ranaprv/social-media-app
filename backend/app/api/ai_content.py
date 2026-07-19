"""AI Content Engine — multi-model content generation with Google Drive saving."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
import json

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import get_settings
from app.models.user import User
from app.models.workspace import WorkspaceMember
from app.models.content import BrandVoice
from app.services.llm import call_llm, call_llm_json, get_available_models
from app.services.google_drive import drive_service

router = APIRouter(prefix="/ai", tags=["ai-content"])

CONTENT_TYPES = {
    "image": {"label": "Static Image", "platforms": ["instagram", "facebook", "linkedin", "x"]},
    "carousel": {"label": "Carousel / Slideshow", "platforms": ["instagram", "linkedin"]},
    "article": {"label": "Long-form Article", "platforms": ["linkedin", "x"]},
    "linkedin_post": {"label": "LinkedIn Post", "platforms": ["linkedin"]},
    "short_video": {"label": "Short Video (Reel/Short)", "platforms": ["instagram", "youtube", "x"]},
    "long_video": {"label": "Long Video", "platforms": ["youtube", "facebook"]},
    "reel": {"label": "Instagram Reel", "platforms": ["instagram"]},
    "story": {"label": "Story", "platforms": ["instagram", "facebook"]},
    "tweet_thread": {"label": "X/Twitter Thread", "platforms": ["x"]},
    "email": {"label": "Email Newsletter", "platforms": []},
}

SYSTEM_PROMPTS = {
    "image": "You are a visual content creator. Generate a detailed image prompt and design brief for social media. Include: prompt text for AI image generation, suggested dimensions, color palette, text overlay suggestions, and brand alignment notes.",
    "carousel": "You are a carousel content expert. Generate slide-by-slide content for a social media carousel. Each slide should have: headline, body text (max 30 words), and visual description. Include a hook slide and CTA slide.",
    "article": "You are a professional content writer. Write a well-structured long-form article with: engaging title, introduction with hook, 3-5 main sections with headers, actionable takeaways, and a strong conclusion with CTA.",
    "linkedin_post": "You are a LinkedIn content strategist. Write a high-engagement LinkedIn post. Start with a hook line, use short paragraphs, include line breaks for readability, add relevant hashtags, end with a question or CTA.",
    "short_video": "You are a short-form video scriptwriter. Write a script for a 15-60 second video (Reel/Short/TikTok). Include: hook (0-3s), content (3-45s), CTA (45-60s), text overlays, and suggested music/mood.",
    "long_video": "You are a YouTube scriptwriter. Write a video script with: title, thumbnail text, hook (first 10 seconds), chapter timestamps, main content sections, B-roll suggestions, and end screen CTA.",
    "reel": "You are an Instagram Reel creator. Write a Reel script with: trending hook, visual sequence, text overlays, suggested audio, and caption with hashtags.",
    "story": "You are a social media story creator. Write story content with: visual description, text overlay, interactive element suggestion (poll/question/slider), and swipe-up CTA.",
    "tweet_thread": "You are a viral thread writer. Write a Twitter/X thread. Start with a banger first tweet, maintain momentum, use numbering (1/N), include insights/data where possible, end with a summary tweet and CTA.",
    "email": "You are an email marketing specialist. Write a newsletter email with: subject line, preview text, body with sections, clear CTA buttons, and P.S. line.",
}


async def _get_brand_voice_context(workspace_id: str, db: AsyncSession) -> str:
    result = await db.execute(select(BrandVoice).where(BrandVoice.workspace_id == workspace_id))
    bv = result.scalar_one_or_none()
    if not bv:
        return ""
    parts = []
    if bv.tone:
        parts.append(f"Tone: {bv.tone}")
    if bv.writing_style:
        parts.append(f"Style: {bv.writing_style}")
    if bv.emoji_usage:
        parts.append(f"Emoji: {bv.emoji_usage}")
    return "\n".join(parts)


@router.get("/content-types")
async def list_content_types():
    """List available content types."""
    return {"content_types": CONTENT_TYPES}


@router.get("/models")
async def list_content_models():
    """List available LLM models for content generation."""
    return {"models": get_available_models()}


@router.post("/generate-content")
async def generate_content(
    request: dict,
):
    """Generate content using selected model and content type."""
    content_type = request.get("content_type", "linkedin_post")
    topic = request.get("topic", "")
    platform = request.get("platform", "linkedin")
    provider = request.get("provider", "openai")
    model = request.get("model", None)
    custom_prompt = request.get("custom_prompt", "")
    brand_voice = request.get("brand_voice", "")
    tone = request.get("tone", "")
    keywords = request.get("keywords", [])
    length = request.get("length", "medium")
    workspace_id = request.get("workspace_id", "")

    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required")

    # Get brand voice context from workspace
    bv_context = ""
    if workspace_id:
        bv_context = await _get_brand_voice_context(workspace_id, db)

    # Build prompt
    system_prompt = SYSTEM_PROMPTS.get(content_type, SYSTEM_PROMPTS["linkedin_post"])

    prompt_parts = [f"Create {content_type} content about: {topic}"]
    if platform:
        prompt_parts.append(f"Platform: {platform}")
    if tone:
        prompt_parts.append(f"Tone: {tone}")
    if keywords:
        prompt_parts.append(f"Keywords to include: {', '.join(keywords)}")
    if custom_prompt:
        prompt_parts.append(f"Additional instructions: {custom_prompt}")
    if brand_voice:
        prompt_parts.append(f"\nBrand voice guidelines:\n{brand_voice}")
    elif bv_context:
        prompt_parts.append(f"\nBrand voice:\n{bv_context}")

    length_guide = {
        "short": "Keep it concise and punchy.",
        "medium": "Write a balanced piece with good detail.",
        "long": "Write a comprehensive, detailed piece.",
    }
    prompt_parts.append(length_guide.get(length, length_guide["medium"]))

    full_prompt = "\n".join(prompt_parts)

    # Generate content
    content = await call_llm(full_prompt, system_prompt, provider=provider, model=model, temperature=0.7)

    if not content:
        content = f"[Placeholder — configure {provider} API key for {content_type} generation]\n\nPrompt: {full_prompt[:200]}..."

    # Generate hashtags
    hashtag_prompt = f"Generate 5-10 relevant hashtags for this {platform} content about {topic}. Return as JSON array of strings."
    hashtags_raw = await call_llm_json(hashtag_prompt, provider=provider, model=model, temperature=0.5)
    hashtags = hashtags_raw if isinstance(hashtags_raw, list) else [f"#{topic.replace(' ', '').title()}"]

    # Save to Google Drive if requested
    drive_url = None
    save_to_drive = request.get("save_to_drive", False)
    if save_to_drive:
        drive_result = await drive_service.upload_file(
            file_bytes=content.encode("utf-8"),
            filename=f"{content_type}_{topic[:50].replace(' ', '_')}.md",
            mime_type="text/markdown",
            folder_id=request.get("drive_folder_id"),
        )
        if drive_result:
            drive_url = drive_result.get("url")

    return {
        "content": content,
        "content_type": content_type,
        "platform": platform,
        "hashtags": hashtags,
        "provider": provider,
        "model": model,
        "drive_url": drive_url,
    }


@router.post("/generate-video-script")
async def generate_video_script(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a complete video pipeline: script + voiceover text + thumbnail prompt."""
    topic = request.get("topic", "")
    platform = request.get("platform", "youtube")
    provider = request.get("provider", "openai")
    model = request.get("model", None)
    duration_seconds = request.get("duration", 60)
    style = request.get("style", "professional")

    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required")

    # Step 1: Generate video script
    script_prompt = f"""Write a {duration_seconds}-second video script for {platform} about: {topic}
Style: {style}

Return JSON with:
- "title": video title
- "hook": first 3-5 seconds script
- "sections": array of {{timestamp, visual, narration, text_overlay}} objects
- "cta": call-to-action ending
- "total_duration": estimated seconds"""

    script = await call_llm_json(script_prompt, system_prompt="You are a video scriptwriter.", provider=provider, model=model)

    if not script:
        script = {
            "title": f"Video about {topic}",
            "hook": f"Stop scrolling! Here's what you need to know about {topic}.",
            "sections": [
                {"timestamp": "0:00-0:05", "visual": "Face to camera or text overlay", "narration": f"Hook about {topic}", "text_overlay": topic},
                {"timestamp": "0:05-0:30", "visual": "Screen recording or B-roll", "narration": "Main content", "text_overlay": "Key point 1"},
                {"timestamp": "0:30-0:50", "visual": "Graphics or demo", "narration": "Supporting details", "text_overlay": "Key point 2"},
            ],
            "cta": "Follow for more tips!",
            "total_duration": duration_seconds,
        }

    # Step 2: Generate voiceover text
    voiceover_text = ""
    for section in script.get("sections", []):
        voiceover_text += section.get("narration", "") + " "
    voiceover_text += script.get("cta", "")
    voiceover_text = voiceover_text.strip()

    # Step 3: Generate thumbnail prompt
    thumbnail_prompt_text = f"Create a YouTube thumbnail for: {script.get('title', topic)}. Style: {style}. Include bold text overlay with the title, vibrant colors, and an eye-catching composition."

    # Step 4: Save everything to Google Drive
    drive_url = None
    save_to_drive = request.get("save_to_drive", False)
    if save_to_drive:
        # Save script
        script_content = json.dumps(script, indent=2)
        drive_result = await drive_service.upload_file(
            file_bytes=script_content.encode("utf-8"),
            filename=f"script_{topic[:30].replace(' ', '_')}.json",
            mime_type="application/json",
            folder_id=request.get("drive_folder_id"),
        )
        if drive_result:
            drive_url = drive_result.get("url")

    return {
        "script": script,
        "voiceover_text": voiceover_text,
        "thumbnail_prompt": thumbnail_prompt_text,
        "drive_url": drive_url,
        "provider": provider,
        "model": model,
    }


@router.post("/save-to-drive")
async def save_content_to_drive(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Save generated content to Google Drive."""
    content = request.get("content", "")
    filename = request.get("filename", "content.md")
    content_type_mime = request.get("mime_type", "text/markdown")
    folder_id = request.get("folder_id", None)

    if not content:
        raise HTTPException(status_code=400, detail="Content is required")

    result = await drive_service.upload_file(
        file_bytes=content.encode("utf-8"),
        filename=filename,
        mime_type=content_type_mime,
        folder_id=folder_id,
    )

    if not result:
        raise HTTPException(status_code=503, detail="Google Drive not configured. Set GOOGLE_DRIVE_CREDENTIALS_FILE.")

    return result
