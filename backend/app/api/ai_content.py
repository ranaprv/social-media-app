from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.workspace import WorkspaceMember
from app.models.content import Post, BrandVoice
from app.schemas import (
    AIContentRequest,
    AIContentResponse,
    AIResearchRequest,
    AIResearchTrendsResponse,
    AIResearchCompetitorsResponse,
    AIResearchKeywordsResponse,
    AIResearchIdeasResponse,
)

router = APIRouter(prefix="/ai", tags=["ai-content"])


async def get_brand_voice(workspace_id: str, db: AsyncSession) -> str:
    """Get brand voice context for AI generation."""
    result = await db.execute(
        select(BrandVoice).where(BrandVoice.workspace_id == workspace_id)
    )
    brand_voice = result.scalar_one_or_none()
    
    if not brand_voice:
        return ""
    
    parts = []
    if brand_voice.tone:
        parts.append(f"Tone: {brand_voice.tone}")
    if brand_voice.writing_style:
        parts.append(f"Style: {brand_voice.writing_style}")
    if brand_voice.emoji_usage:
        parts.append(f"Emoji: {brand_voice.emoji_usage}")
    
    return "\n".join(parts)


@router.post("/generate", response_model=AIContentResponse)
async def generate_content(
    workspace_id: str,
    request: AIContentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate AI content for a specific platform."""
    # Verify workspace access
    result = await db.execute(
        select(WorkspaceMember)
        .where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # Get brand voice
    brand_voice_context = await get_brand_voice(workspace_id, db)
    
    # Platform-specific prompts
    platform_prompts = {
        "linkedin": "Write a professional LinkedIn post",
        "x": "Write a tweet or thread for X/Twitter",
        "instagram": "Write an Instagram caption",
        "facebook": "Write a Facebook post",
        "youtube": "Write a YouTube video script",
    }
    
    platform_prompt = platform_prompts.get(request.platform, "Write social media content")
    
    # Build the full prompt
    prompt_parts = [
        f"{platform_prompt} about: {request.topic}",
    ]
    
    if request.content_type:
        prompt_parts.append(f"Content type: {request.content_type}")
    
    if request.tone:
        prompt_parts.append(f"Tone: {request.tone}")
    
    if request.keywords:
        prompt_parts.append(f"Keywords to include: {', '.join(request.keywords)}")
    
    if brand_voice_context:
        prompt_parts.append(f"\nBrand voice guidelines:\n{brand_voice_context}")
    
    length_guide = {
        "short": "Keep it concise (under 100 words)",
        "medium": "Write a medium-length post (100-250 words)",
        "long": "Write a detailed post (250-500 words)",
    }
    prompt_parts.append(length_guide.get(request.length, length_guide["medium"]))
    
    full_prompt = "\n".join(prompt_parts)
    
    # TODO: Integrate with actual AI providers (OpenAI, Anthropic, Gemini)
    # For now, return a placeholder response
    generated_content = f"[AI Generated Content]\n\n{full_prompt}\n\n---\n\nThis is a placeholder. Connect your AI provider API keys to generate real content."
    
    # Generate placeholder hashtags
    hashtags = [f"#{word.capitalize()}" for word in request.topic.split()[:5]]
    
    return AIContentResponse(
        content=generated_content,
        hashtags=hashtags,
        suggestions=[
            "Consider adding a call-to-action",
            "Add relevant emojis for engagement",
            "Include 3-5 relevant hashtags",
        ],
        engagement_score=0.75,
    )


@router.post("/rewrite", response_model=AIContentResponse)
async def rewrite_content(
    workspace_id: str,
    content: str,
    platform: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Rewrite existing content for a different platform."""
    # Verify workspace access
    result = await db.execute(
        select(WorkspaceMember)
        .where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # Get brand voice
    brand_voice_context = await get_brand_voice(workspace_id, db)
    
    # Platform-specific rewrite instructions
    rewrite_instructions = {
        "linkedin": "Rewrite for LinkedIn: professional tone, professional hashtags, longer form",
        "x": "Rewrite for X/Twitter: concise, punchy, under 280 characters per tweet, use thread if needed",
        "instagram": "Rewrite for Instagram: engaging caption, emojis, 30 hashtags max",
        "facebook": "Rewrite for Facebook: conversational, engaging, ask questions",
        "youtube": "Rewrite as a YouTube video script with hooks and CTAs",
    }
    
    instruction = rewrite_instructions.get(platform, f"Rewrite for {platform}")
    
    # TODO: Integrate with actual AI providers
    rewritten = f"[AI Rewritten for {platform.upper()}]\n\n{instruction}\n\nOriginal content:\n{content[:200]}..."
    
    return AIContentResponse(
        content=rewritten,
        hashtags=[],
        suggestions=[f"Optimized for {platform} best practices"],
        engagement_score=0.80,
    )


@router.post("/repurpose", response_model=list[AIContentResponse])
async def repurpose_content(
    workspace_id: str,
    content: str,
    source_platform: str,
    target_platforms: list[str],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Repurpose content from one platform to multiple others."""
    # Verify workspace access
    result = await db.execute(
        select(WorkspaceMember)
        .where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    results = []
    for target in target_platforms:
        # TODO: Integrate with actual AI providers
        repurposed = f"[AI Repurposed from {source_platform.upper()} to {target.upper()}]\n\nOriginal content:\n{content[:200]}..."
        
        results.append(AIContentResponse(
            content=repurposed,
            hashtags=[],
            suggestions=[f"Optimized for {target}"],
            engagement_score=0.75,
        ))
    
    return results
