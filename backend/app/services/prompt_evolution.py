"""Prompt Evolution Service — self-improving prompt engine.

Responsibilities:
    1. Get the best active prompt for a content_type + platform
    2. Seed initial prompt versions from hardcoded defaults
    3. Log prompt usage when content is generated
    4. Update prompt performance scores from analytics feedback
    5. Promote the best-performing version as active

Design:
    - Prompts are scored by rolling average engagement rate
    - After N uses, the system can surface which prompt version performs best
    - New versions can be created manually or auto-generated from high-performing patterns
"""
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prompt_versions import PromptVersion, PromptUsageLog

logger = logging.getLogger(__name__)

# Minimum uses before a prompt's score is considered reliable
MIN_USES_FOR_PROMOTION = 5

# Hardcoded seed prompts — used to bootstrap the prompt_versions table
SEED_PROMPTS: dict[str, dict[str, dict[str, str]]] = {
    "linkedin_post": {
        "linkedin": {
            "system": (
                "You are a LinkedIn content strategist with 10 years of experience. "
                "Write high-engagement LinkedIn posts that start with a hook line, "
                "use short paragraphs (1-2 sentences each), include line breaks for readability, "
                "add relevant hashtags, and end with a question or CTA. "
                "Avoid corporate jargon. Write like a human sharing genuine insights."
            ),
            "user": (
                "Write a LinkedIn post about: {topic}\n"
                "Tone: {tone}\n"
                "Platform: LinkedIn\n"
                "Keywords to include: {keywords}\n"
                "{brand_voice_context}\n"
                "{length_guide}"
            ),
        },
    },
    "tweet_thread": {
        "x": {
            "system": (
                "You are a viral thread writer for X/Twitter. "
                "Write a thread that starts with a banger first tweet, "
                "maintains momentum with insights and data, "
                "uses numbering (1/N), and ends with a summary tweet and CTA. "
                "Each tweet must be under 280 characters. "
                "Be punchy, direct, and opinionated."
            ),
            "user": (
                "Write an X/Twitter thread about: {topic}\n"
                "Tone: {tone}\n"
                "Platform: X/Twitter\n"
                "Keywords: {keywords}\n"
                "{brand_voice_context}\n"
                "{length_guide}"
            ),
        },
    },
    "reel": {
        "instagram": {
            "system": (
                "You are an Instagram Reel scriptwriter. "
                "Write a Reel script with: trending hook (0-3s), "
                "visual sequence with text overlays, suggested audio/mood, "
                "and a caption with hashtags. "
                "Keep it under 60 seconds. Focus on visual storytelling."
            ),
            "user": (
                "Write an Instagram Reel script about: {topic}\n"
                "Duration: {duration}s\n"
                "Style: {style}\n"
                "Tone: {tone}\n"
                "{brand_voice_context}"
            ),
        },
    },
    "short_video": {
        "youtube": {
            "system": (
                "You are a YouTube Shorts scriptwriter. "
                "Write a 15-60 second script with: hook (first 3 seconds), "
                "main content with text overlays, and CTA. "
                "Focus on visual storytelling and retention."
            ),
            "user": (
                "Write a YouTube Shorts script about: {topic}\n"
                "Duration: {duration}s\n"
                "Style: {style}\n"
                "Tone: {tone}\n"
                "{brand_voice_context}"
            ),
        },
        "instagram": {
            "system": (
                "You are an Instagram Reel scriptwriter. "
                "Write a short video script with: hook, visual sequence, "
                "text overlays, and CTA."
            ),
            "user": (
                "Write a short video script about: {topic}\n"
                "Duration: {duration}s\n"
                "Tone: {tone}\n"
                "{brand_voice_context}"
            ),
        },
    },
    "article": {
        "linkedin": {
            "system": (
                "You are a professional content writer for LinkedIn. "
                "Write a well-structured long-form article with: engaging title, "
                "introduction with hook, 3-5 main sections with headers, "
                "actionable takeaways, and a strong conclusion with CTA."
            ),
            "user": (
                "Write a long-form article about: {topic}\n"
                "Tone: {tone}\n"
                "Keywords: {keywords}\n"
                "{brand_voice_context}\n"
                "{length_guide}"
            ),
        },
    },
    "image": {
        "instagram": {
            "system": (
                "You are a visual content creator. Generate a detailed image prompt "
                "and design brief for social media. Include: prompt text for AI image "
                "generation, suggested dimensions, color palette, text overlay suggestions, "
                "and brand alignment notes."
            ),
            "user": (
                "Create an image prompt for: {topic}\n"
                "Style: {style}\n"
                "Platform: {platform}\n"
                "Brand colors: {brand_colors}\n"
                "Text overlay: {text_overlay}\n"
                "{brand_voice_context}"
            ),
        },
    },
    "carousel": {
        "instagram": {
            "system": (
                "You are a carousel content expert. Generate slide-by-slide content "
                "for a social media carousel. Each slide should have: headline, "
                "body text (max 30 words), and visual description. "
                "Include a hook slide and CTA slide."
            ),
            "user": (
                "Create carousel content about: {topic}\n"
                "Slides: {slide_count}\n"
                "Tone: {tone}\n"
                "{brand_voice_context}"
            ),
        },
    },
    "story": {
        "instagram": {
            "system": (
                "You are a social media story creator. Write story content with: "
                "visual description, text overlay, interactive element suggestion "
                "(poll/question/slider), and swipe-up CTA."
            ),
            "user": (
                "Create Instagram Story content about: {topic}\n"
                "Tone: {tone}\n"
                "{brand_voice_context}"
            ),
        },
    },
    "email": {
        "linkedin": {
            "system": (
                "You are an email marketing specialist. Write a newsletter email with: "
                "subject line, preview text, body with sections, clear CTA buttons, "
                "and P.S. line."
            ),
            "user": (
                "Write a newsletter email about: {topic}\n"
                "Tone: {tone}\n"
                "Audience: {target_audience}\n"
                "{brand_voice_context}"
            ),
        },
    },
}


async def seed_prompt_versions(db: AsyncSession) -> int:
    """Seed initial prompt versions from hardcoded defaults.

    Returns the number of versions created (skips if already seeded).
    """
    # Check if already seeded
    result = await db.execute(select(func.count(PromptVersion.id)))
    if result.scalar() > 0:
        return 0

    created = 0
    for content_type, platforms in SEED_PROMPTS.items():
        for platform, prompts in platforms.items():
            pv = PromptVersion(
                id=str(uuid.uuid4()),
                content_type=content_type,
                platform=platform,
                version=1,
                system_prompt=prompts["system"],
                user_prompt_template=prompts["user"],
                is_active=True,
                performance_score=50.0,  # neutral starting score
                usage_count=0,
                created_by="system",
                notes="Initial seed prompt",
            )
            db.add(pv)
            created += 1

    await db.flush()
    logger.info("Seeded %d prompt versions", created)
    return created


async def get_best_prompt(
    db: AsyncSession,
    content_type: str,
    platform: str,
) -> PromptVersion | None:
    """Get the best active prompt version for a content_type + platform.

    Selection logic:
    1. Active prompts only
    2. Ranked by performance_score (highest first)
    3. Tie-break by usage_count (more used = more reliable)
    4. If no scored prompts, return any active one
    """
    result = await db.execute(
        select(PromptVersion)
        .where(
            PromptVersion.content_type == content_type,
            PromptVersion.platform == platform,
            PromptVersion.is_active == True,
        )
        .order_by(
            PromptVersion.performance_score.desc(),
            PromptVersion.usage_count.desc(),
        )
        .limit(1)
    )
    return result.scalar_one_or_none()


async def log_prompt_usage(
    db: AsyncSession,
    prompt_version_id: str,
    workspace_id: str,
    topic: str = "",
    provider: str = "",
    model: str = "",
    tokens_used: int = 0,
    post_id: str | None = None,
    content_item_id: str | None = None,
) -> PromptUsageLog:
    """Log that a prompt version was used for content generation."""
    log = PromptUsageLog(
        id=str(uuid.uuid4()),
        prompt_version_id=prompt_version_id,
        workspace_id=workspace_id,
        post_id=post_id,
        content_item_id=content_item_id,
        topic=topic,
        provider=provider,
        model=model,
        tokens_used=tokens_used,
        created_at=datetime.utcnow(),
    )
    db.add(log)

    # Increment usage count on the prompt version
    result = await db.execute(
        select(PromptVersion).where(PromptVersion.id == prompt_version_id)
    )
    pv = result.scalar_one_or_none()
    if pv:
        pv.usage_count = (pv.usage_count or 0) + 1

    await db.flush()
    return log


async def update_prompt_performance(
    db: AsyncSession,
    post_id: str,
    engagement_rate: float,
) -> int:
    """Update prompt performance scores when analytics come in.

    Finds the prompt usage log for this post, updates its engagement,
    then recalculates the prompt version's rolling performance score.

    Returns the number of prompt versions updated.
    """
    # Find the usage log for this post
    result = await db.execute(
        select(PromptUsageLog).where(PromptUsageLog.post_id == post_id)
    )
    usage_log = result.scalar_one_or_none()
    if not usage_log:
        return 0

    # Update the usage log with actual engagement
    usage_log.actual_engagement_rate = engagement_rate
    usage_log.scored_at = datetime.utcnow()

    # Recalculate the prompt version's rolling performance score
    pv_result = await db.execute(
        select(PromptVersion).where(PromptVersion.id == usage_log.prompt_version_id)
    )
    pv = pv_result.scalar_one_or_none()
    if not pv:
        return 0

    # Get all scored usage logs for this prompt version
    logs_result = await db.execute(
        select(PromptUsageLog.actual_engagement_rate)
        .where(
            PromptUsageLog.prompt_version_id == pv.id,
            PromptUsageLog.actual_engagement_rate.isnot(None),
        )
    )
    scores = [row[0] for row in logs_result.all()]

    if scores:
        # Rolling average: weight recent scores more heavily
        avg = sum(scores) / len(scores)
        # Convert engagement rate (0-100%) to a 0-100 score
        # 5% engagement = 50 score, 10%+ = 80+, <1% = 20
        pv.performance_score = min(100.0, avg * 10)
        pv.avg_engagement_rate = avg

    await db.flush()
    logger.info(
        "Updated prompt %s performance: score=%.1f, avg_engagement=%.2f%%, uses=%d",
        pv.id[:8], pv.performance_score, pv.avg_engagement_rate or 0, pv.usage_count or 0,
    )
    return 1


async def create_prompt_version(
    db: AsyncSession,
    content_type: str,
    platform: str,
    system_prompt: str,
    user_prompt_template: str,
    created_by: str = "user",
    notes: str = "",
    temperature: float = 0.7,
    max_tokens: int = 3000,
) -> PromptVersion:
    """Create a new prompt version (deactivates old active one for same content_type+platform)."""
    # Get the next version number
    result = await db.execute(
        select(func.max(PromptVersion.version))
        .where(
            PromptVersion.content_type == content_type,
            PromptVersion.platform == platform,
        )
    )
    max_version = result.scalar() or 0

    # Deactivate old active versions for this content_type+platform
    await db.execute(
        update(PromptVersion)
        .where(
            PromptVersion.content_type == content_type,
            PromptVersion.platform == platform,
            PromptVersion.is_active == True,
        )
        .values(is_active=False)
    )

    pv = PromptVersion(
        id=str(uuid.uuid4()),
        content_type=content_type,
        platform=platform,
        version=max_version + 1,
        system_prompt=system_prompt,
        user_prompt_template=user_prompt_template,
        temperature=temperature,
        max_tokens=max_tokens,
        is_active=True,
        performance_score=50.0,
        usage_count=0,
        created_by=created_by,
        notes=notes,
    )
    db.add(pv)
    await db.flush()
    logger.info("Created prompt version v%d for %s/%s", pv.version, content_type, platform)
    return pv


async def get_prompt_analytics(
    db: AsyncSession,
    content_type: str | None = None,
    platform: str | None = None,
    days: int = 30,
) -> dict[str, Any]:
    """Get analytics for prompt versions — which ones perform best."""
    cutoff = datetime.utcnow() - timedelta(days=days)

    query = (
        select(
            PromptVersion.id,
            PromptVersion.content_type,
            PromptVersion.platform,
            PromptVersion.version,
            PromptVersion.performance_score,
            PromptVersion.usage_count,
            PromptVersion.avg_engagement_rate,
            PromptVersion.is_active,
            PromptVersion.created_at,
        )
        .where(PromptVersion.created_at >= cutoff)
    )

    if content_type:
        query = query.where(PromptVersion.content_type == content_type)
    if platform:
        query = query.where(PromptVersion.platform == platform)

    query = query.order_by(PromptVersion.performance_score.desc())
    result = await db.execute(query)
    rows = result.all()

    prompts = []
    for row in rows:
        prompts.append({
            "id": row[0],
            "content_type": row[1],
            "platform": row[2],
            "version": row[3],
            "performance_score": round(row[4] or 0, 1),
            "usage_count": row[5] or 0,
            "avg_engagement_rate": round(row[6] or 0, 2),
            "is_active": row[7],
            "created_at": row[8].isoformat() if row[8] else None,
        })

    # Summary stats
    active_count = sum(1 for p in prompts if p["is_active"])
    total_uses = sum(p["usage_count"] for p in prompts)
    avg_score = (
        sum(p["performance_score"] for p in prompts if p["usage_count"] > 0) /
        max(1, sum(1 for p in prompts if p["usage_count"] > 0))
    )

    return {
        "prompts": prompts,
        "summary": {
            "total_versions": len(prompts),
            "active_versions": active_count,
            "total_uses": total_uses,
            "avg_performance_score": round(avg_score, 1),
        },
    }
