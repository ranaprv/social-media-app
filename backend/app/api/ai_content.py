"""AI Content Engine — multi-model content generation with self-improving prompts.

Uses PromptEvolutionService to:
  - Fetch the best-performing prompt for each content_type + platform
  - Log usage for performance tracking
  - Seed initial prompts on first use
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
import json
import logging

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import get_settings
from app.models.user import User
from app.models.workspace import WorkspaceMember
from app.models.content import BrandVoice
from app.services.llm import call_llm, call_llm_json, get_available_models
from app.services.google_drive import drive_service
from app.services.prompt_evolution import (
    seed_prompt_versions,
    get_best_prompt,
    log_prompt_usage,
    create_prompt_version,
    get_prompt_analytics,
)

logger = logging.getLogger(__name__)

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

# Fallback system prompts (used only if DB has no prompt versions yet)
_FALLBACK_SYSTEM_PROMPTS = {
    "image": "You are a visual content creator. Generate a detailed image prompt and design brief for social media.",
    "carousel": "You are a carousel content expert. Generate slide-by-slide content for a social media carousel.",
    "article": "You are a professional content writer. Write a well-structured long-form article.",
    "linkedin_post": "You are a LinkedIn content strategist. Write a high-engagement LinkedIn post.",
    "short_video": "You are a short-form video scriptwriter. Write a script for a 15-60 second video.",
    "long_video": "You are a YouTube scriptwriter. Write a video script with title, hook, chapters, and CTA.",
    "reel": "You are an Instagram Reel creator. Write a Reel script with trending hook and visual sequence.",
    "story": "You are a social media story creator. Write story content with interactive elements.",
    "tweet_thread": "You are a viral thread writer. Write a Twitter/X thread with numbering and momentum.",
    "email": "You are an email marketing specialist. Write a newsletter with subject line, body, and CTA.",
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


@router.get("/prompt-analytics")
async def prompt_analytics(
    content_type: str = None,
    platform: str = None,
    days: int = 30,
    db: AsyncSession = Depends(get_db),
):
    """Get analytics for prompt versions — which ones perform best."""
    return await get_prompt_analytics(db, content_type=content_type, platform=platform, days=days)


@router.post("/prompt-auto-evolve")
async def prompt_auto_evolve(
    request: dict,
    db: AsyncSession = Depends(get_db),
):
    """Auto-evolve a prompt using LLM analysis of performance data.

    Self-improvement loop:
      1. Analyzes current prompt performance
      2. Gathers usage patterns (high/low performing topics)
      3. Asks LLM to suggest improvements
      4. Creates a new prompt version from the suggestion
      5. New version becomes active, old one deactivated

    Minimum requirements: 3 uses + 2 scored engagements.
    """
    content_type = request.get("content_type", "")
    platform = request.get("platform", "")
    provider = request.get("provider", "openai")
    model = request.get("model", None)

    if not content_type or not platform:
        raise HTTPException(status_code=400, detail="content_type and platform are required")

    # Seed prompts if needed
    await seed_prompt_versions(db)

    from app.services.prompt_auto_evolver import suggest_prompt_improvements
    result = await suggest_prompt_improvements(
        db=db,
        content_type=content_type,
        platform=platform,
        provider=provider,
        model=model,
    )

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@router.get("/content-patterns")
async def content_patterns(
    workspace_id: str = "default",
    platform: str = None,
    days: int = 90,
    db: AsyncSession = Depends(get_db),
):
    """Analyze published posts and extract winning patterns.

    Returns hook patterns, CTA patterns, content structures,
    avoid patterns, and a ready-to-inject learning context string.
    """
    from app.services.content_pattern_learner import extract_winning_patterns
    return await extract_winning_patterns(db, workspace_id, platform=platform, days=days)


@router.post("/quick-research")
async def quick_research(
    request: dict,
):
    """Quick topic research using web search + LLM analysis.

    Returns web results, summary, key insights, and suggested content angles.
    Uses DuckDuckGo (free, no API key) + LLM for analysis.
    """
    topic = request.get("topic", "")
    platform = request.get("platform", "linkedin")
    aspect = request.get("aspect", "general")

    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required")

    from app.services.web_search import research_topic
    return await research_topic(topic, platform, aspect)


@router.post("/prompt-versions")
async def create_new_prompt_version(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new prompt version. Deactivates the old active one."""
    content_type = request.get("content_type", "")
    platform = request.get("platform", "")
    system_prompt = request.get("system_prompt", "")
    user_prompt_template = request.get("user_prompt_template", "")

    if not content_type or not platform or not system_prompt or not user_prompt_template:
        raise HTTPException(status_code=400, detail="content_type, platform, system_prompt, and user_prompt_template are required")

    pv = await create_prompt_version(
        db=db,
        content_type=content_type,
        platform=platform,
        system_prompt=system_prompt,
        user_prompt_template=user_prompt_template,
        created_by=str(current_user.id),
        notes=request.get("notes", ""),
        temperature=request.get("temperature", 0.7),
        max_tokens=request.get("max_tokens", 3000),
    )

    return {
        "id": pv.id,
        "content_type": pv.content_type,
        "platform": pv.platform,
        "version": pv.version,
        "is_active": pv.is_active,
        "performance_score": pv.performance_score,
    }


@router.post("/generate-content")
async def generate_content(
    request: dict,
    db: AsyncSession = Depends(get_db),
):
    """Generate content using the best-performing prompt for the content_type + platform.

    Self-improving loop:
      1. Seed prompts on first use
      2. Fetch best active prompt from DB
      3. Generate content
      4. Log usage for performance tracking
    """
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

    # Step 0: Seed prompt versions on first use
    await seed_prompt_versions(db)

    # Step 1: Get brand voice context from workspace
    bv_context = ""
    if workspace_id:
        bv_context = await _get_brand_voice_context(workspace_id, db)

    # Step 2: Fetch best prompt from DB (self-improving)
    best_prompt = await get_best_prompt(db, content_type, platform)

    if best_prompt:
        system_prompt = best_prompt.system_prompt
        # Build user prompt from template
        length_guide = {
            "short": "Keep it concise and punchy.",
            "medium": "Write a balanced piece with good detail.",
            "long": "Write a comprehensive, detailed piece.",
        }
        prompt_vars = {
            "topic": topic,
            "platform": platform,
            "tone": tone or "professional",
            "keywords": ", ".join(keywords) if keywords else "none specified",
            "brand_voice_context": f"\nBrand voice:\n{bv_context}" if bv_context else "",
            "length_guide": length_guide.get(length, length_guide["medium"]),
            "duration": str(request.get("duration", 60)),
            "style": request.get("style", "professional"),
            "text_overlay": request.get("text_overlay", ""),
            "brand_colors": ", ".join(request.get("brand_colors", [])),
            "slide_count": str(request.get("slide_count", 5)),
            "target_audience": request.get("target_audience", "general audience"),
        }
        try:
            full_prompt = best_prompt.user_prompt_template.format(**prompt_vars)
        except KeyError:
            # Fallback if template has unexpected placeholders
            full_prompt = f"Create {content_type} content about: {topic}\nPlatform: {platform}\nTone: {tone}"
            if bv_context:
                full_prompt += f"\nBrand voice:\n{bv_context}"
    else:
        # Fallback to hardcoded prompts (shouldn't happen after seeding)
        system_prompt = _FALLBACK_SYSTEM_PROMPTS.get(content_type, _FALLBACK_SYSTEM_PROMPTS["linkedin_post"])
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

    # Add custom instructions on top if provided
    if custom_prompt:
        full_prompt += f"\n\nAdditional instructions: {custom_prompt}"

    # Step 2.5: Inject learning context from past performance
    if workspace_id:
        try:
            from app.services.content_pattern_learner import extract_winning_patterns
            patterns = await extract_winning_patterns(db, workspace_id, platform=platform)
            if patterns.get("learning_context"):
                full_prompt += f"\n\n{patterns['learning_context']}"
        except Exception:
            pass  # Non-critical — don't block generation if pattern learning fails

    # Step 3: Generate content
    content = await call_llm(full_prompt, system_prompt, provider=provider, model=model, temperature=0.7)

    if not content:
        content = f"[Placeholder — configure {provider} API key for {content_type} generation]\n\nPrompt: {full_prompt[:200]}..."

    # Step 4: Log prompt usage for self-improving tracking
    prompt_version_id = best_prompt.id if best_prompt else None
    if prompt_version_id:
        await log_prompt_usage(
            db=db,
            prompt_version_id=prompt_version_id,
            workspace_id=workspace_id or "default",
            topic=topic,
            provider=provider,
            model=model or "",
        )

    # Step 5: Generate hashtags
    hashtag_prompt = f"Generate 5-10 relevant hashtags for this {platform} content about {topic}. Return as JSON array of strings."
    hashtags_raw = await call_llm_json(hashtag_prompt, provider=provider, model=model, temperature=0.5)
    hashtags = hashtags_raw if isinstance(hashtags_raw, list) else [f"#{topic.replace(' ', '').title()}"]

    # Step 6: Save to Google Drive if requested
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
        "prompt_version_id": prompt_version_id,
        "prompt_version": best_prompt.version if best_prompt else None,
        "prompt_performance_score": best_prompt.performance_score if best_prompt else None,
    }


@router.post("/generate-content-variants")
async def generate_content_variants(
    request: dict,
    db: AsyncSession = Depends(get_db),
):
    """Generate multiple content variants, score each, return ranked results.

    Self-improving loop integration:
      1. Seeds prompts on first use
      2. Fetches best prompt from DB
      3. Generates N variants with temperature diversity
      4. Scores each with quality rubric + viral predictor
      5. Returns all variants ranked by combined score
      6. Logs usage for the best prompt
    """
    content_type = request.get("content_type", "linkedin_post")
    topic = request.get("topic", "")
    platform = request.get("platform", "linkedin")
    provider = request.get("provider", "openai")
    model = request.get("model", None)
    tone = request.get("tone", "")
    keywords = request.get("keywords", [])
    length = request.get("length", "medium")
    workspace_id = request.get("workspace_id", "")
    variant_count = request.get("variant_count", 3)

    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required")

    # Seed prompts
    await seed_prompt_versions(db)

    # Get brand voice
    bv_context = ""
    if workspace_id:
        bv_context = await _get_brand_voice_context(workspace_id, db)

    # Get best prompt
    best_prompt = await get_best_prompt(db, content_type, platform)

    if best_prompt:
        system_prompt = best_prompt.system_prompt
        length_guide = {
            "short": "Keep it concise and punchy.",
            "medium": "Write a balanced piece with good detail.",
            "long": "Write a comprehensive, detailed piece.",
        }
        prompt_vars = {
            "topic": topic,
            "platform": platform,
            "tone": tone or "professional",
            "keywords": ", ".join(keywords) if keywords else "none specified",
            "brand_voice_context": f"\nBrand voice:\n{bv_context}" if bv_context else "",
            "length_guide": length_guide.get(length, length_guide["medium"]),
            "duration": str(request.get("duration", 60)),
            "style": request.get("style", "professional"),
            "text_overlay": request.get("text_overlay", ""),
            "brand_colors": ", ".join(request.get("brand_colors", [])),
            "slide_count": str(request.get("slide_count", 5)),
            "target_audience": request.get("target_audience", "general audience"),
        }
        try:
            user_prompt = best_prompt.user_prompt_template.format(**prompt_vars)
        except KeyError:
            user_prompt = f"Create {content_type} content about: {topic}\nPlatform: {platform}\nTone: {tone}"
    else:
        system_prompt = _FALLBACK_SYSTEM_PROMPTS.get(content_type, _FALLBACK_SYSTEM_PROMPTS["linkedin_post"])
        user_prompt = f"Create {content_type} content about: {topic}\nPlatform: {platform}\nTone: {tone}"

    # Generate variants
    from app.services.multi_variant_generator import generate_variants
    result = await generate_variants(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        platform=platform,
        provider=provider,
        model=model,
        variant_count=variant_count,
        media_count=request.get("media_count", 0),
        has_cta=request.get("has_cta", False),
        brand_voice=bv_context or request.get("brand_voice"),
        target_audience=request.get("target_audience"),
    )

    # Log usage for the best prompt
    if best_prompt:
        await log_prompt_usage(
            db=db,
            prompt_version_id=best_prompt.id,
            workspace_id=workspace_id or "default",
            topic=topic,
            provider=provider,
            model=model or "",
        )

    # Generate hashtags for the best variant
    hashtag_prompt = f"Generate 5-10 relevant hashtags for this {platform} content about {topic}. Return as JSON array of strings."
    hashtags_raw = await call_llm_json(hashtag_prompt, provider=provider, model=model, temperature=0.5)
    hashtags = hashtags_raw if isinstance(hashtags_raw, list) else [f"#{topic.replace(' ', '').title()}"]

    return {
        "variants": result["variants"],
        "best_index": result["best_index"],
        "best_content": result["best_content"],
        "scores_summary": result["scores_summary"],
        "hashtags": hashtags,
        "content_type": content_type,
        "platform": platform,
        "provider": provider,
        "model": model,
        "prompt_version_id": best_prompt.id if best_prompt else None,
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

    # Seed prompts on first use
    await seed_prompt_versions(db)

    # Fetch best prompt for this content type
    video_content_type = "short_video" if duration_seconds <= 60 else "long_video"
    best_prompt = await get_best_prompt(db, video_content_type, platform)

    if best_prompt:
        system_prompt = best_prompt.system_prompt
        try:
            script_prompt = best_prompt.user_prompt_template.format(
                topic=topic, duration=duration_seconds, style=style, tone=style,
                platform=platform, brand_voice_context="",
            )
        except KeyError:
            script_prompt = f"Write a {duration_seconds}-second video script for {platform} about: {topic}\nStyle: {style}"
    else:
        system_prompt = "You are a video scriptwriter."
        script_prompt = f"""Write a {duration_seconds}-second video script for {platform} about: {topic}
Style: {style}

Return JSON with:
- "title": video title
- "hook": first 3-5 seconds script
- "sections": array of {{timestamp, visual, narration, text_overlay}} objects
- "cta": call-to-action ending
- "total_duration": estimated seconds"""

    script = await call_llm_json(script_prompt, system_prompt=system_prompt, provider=provider, model=model)

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

    # Log usage
    if best_prompt:
        await log_prompt_usage(
            db=db,
            prompt_version_id=best_prompt.id,
            workspace_id="default",
            topic=topic,
            provider=provider,
            model=model or "",
        )

    # Generate voiceover text
    voiceover_text = ""
    for section in script.get("sections", []):
        voiceover_text += section.get("narration", "") + " "
    voiceover_text += script.get("cta", "")
    voiceover_text = voiceover_text.strip()

    # Generate thumbnail prompt
    thumbnail_prompt_text = f"Create a YouTube thumbnail for: {script.get('title', topic)}. Style: {style}. Include bold text overlay with the title, vibrant colors, and an eye-catching composition."

    # Generate detailed storyboard
    storyboard = None
    try:
        from app.services.storyboard_service import generate_storyboard
        storyboard = await generate_storyboard(
            script=script,
            platform=platform,
            style=style,
            provider=provider,
            model=model,
        )
    except Exception as e:
        logger.warning("Storyboard generation failed: %s", e)

    # Save to Google Drive if requested
    drive_url = None
    save_to_drive = request.get("save_to_drive", False)
    if save_to_drive:
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
        "storyboard": storyboard,
        "drive_url": drive_url,
        "provider": provider,
        "model": model,
        "prompt_version_id": best_prompt.id if best_prompt else None,
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
