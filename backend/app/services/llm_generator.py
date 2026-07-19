"""LLM-powered content generator for ContentSlots.

Builds prompts from strategy context and calls LLM to generate social media posts.
Enriched with pillar hooks, persona pain points, content types, brand voice samples,
and diversity checks against recent posts.
"""
import logging
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Platform-specific formatting guidance
PLATFORM_GUIDANCE = {
    "linkedin": "Write a professional LinkedIn post. Use short paragraphs. Start with a hook. End with a CTA or question.",
    "x": "Write a tweet (max 280 chars). Be punchy. Use 1-3 relevant hashtags. No thread — single tweet only.",
    "instagram": "Write an Instagram caption. Start with a hook in the first line. Use line breaks for readability. Include 5-10 relevant hashtags at the end.",
    "facebook": "Write a Facebook post. Conversational tone. Ask a question to drive comments.",
    "youtube": "Write a YouTube video title (max 70 chars) and description (first 2 lines that show before 'Show more'). Be SEO-friendly.",
}


async def _fetch_recent_posts(
    db: AsyncSession,
    workspace_id: str,
    pillar_name: str,
    platform: str,
    limit: int = 5,
) -> list[str]:
    """Fetch recent generated content in same pillar+platform for diversity checks."""
    from app.models.strategy import ContentSlot

    result = await db.execute(
        select(ContentSlot.generated_content)
        .where(
            ContentSlot.workspace_id == workspace_id,
            ContentSlot.pillar_name == pillar_name,
            ContentSlot.platform == platform,
            ContentSlot.generated_content.isnot(None),
            ContentSlot.status.in_(["generated", "approved", "published"]),
        )
        .order_by(ContentSlot.scheduled_datetime.desc())
        .limit(limit)
    )
    return [row[0] for row in result.all() if row[0]]


async def generate_slot_content(
    db: AsyncSession,
    slot: Any,
    context: dict[str, Any],
) -> dict[str, Any] | None:
    """Generate content for a single ContentSlot using LLM.

    Args:
        db: Database session
        slot: ContentSlot ORM object
        context: Strategy/brand context dict

    Returns:
        Dict with content, variants, scores, etc. or None on failure
    """
    from app.services.llm import call_llm_json

    platform = context["platform"]
    pillar = context["pillar"]
    brand_voice = context["brand_voice"]
    persona = context["persona"]
    strategy_pillars = context.get("strategy_pillars", [])
    workspace_id = context.get("workspace_id", "")

    # Look up the full pillar config for this pillar name
    pillar_config = {}
    for sp in strategy_pillars:
        if isinstance(sp, dict) and sp.get("name") == pillar:
            pillar_config = sp
            break

    # --- Build system prompt ---
    system_prompt_parts = [
        f"You are a social media content writer for a brand.",
        f"Brand voice: {brand_voice['tone']} tone, {brand_voice['style']} writing style.",
        f"Emoji usage: {brand_voice['emoji']}.",
        f"",
        f"Platform rules: {PLATFORM_GUIDANCE.get(platform, 'Write engaging social media content.')}",
        f"",
        f"Content pillar: {pillar}",
    ]

    # Include pillar hooks
    example_hooks = pillar_config.get("example_hooks", [])
    if example_hooks:
        system_prompt_parts.append(f"Example hooks for this pillar: {', '.join(example_hooks)}")

    # Include pillar content types
    content_types = pillar_config.get("content_types", [])
    if content_types:
        system_prompt_parts.append(f"Preferred content types: {', '.join(content_types)}")

    # Persona enrichment
    persona_name = persona.get("name", "General audience")
    persona_desc = persona.get("description", "")
    system_prompt_parts.append(f"Audience persona: {persona_name} — {persona_desc}")

    pain_points = persona.get("pain_points", [])
    if pain_points:
        system_prompt_parts.append(f"Audience pain points to address: {'; '.join(pain_points)}")

    content_prefs = persona.get("content_preferences", [])
    if content_prefs:
        system_prompt_parts.append(f"Audience content preferences: {'; '.join(content_prefs)}")

    system_prompt_parts.append("")
    system_prompt_parts.append("IMPORTANT: Output ONLY valid JSON. No markdown fences, no explanation.")

    system_prompt = "\n".join(system_prompt_parts)

    # --- Build user prompt ---
    prompt_parts = [
        f"Generate a social media post for {platform}.",
        f"",
        f"Topic/pillar: {pillar}",
        f"Scheduled: {context['scheduled_date']} at {context['scheduled_time']}",
    ]

    # Brand voice sample posts as few-shot examples
    if brand_voice.get("sample_posts"):
        samples = "\n".join(f"- {s}" for s in brand_voice["sample_posts"][:3])
        prompt_parts.append(f"\nReference examples of our brand voice:\n{samples}")

    # Diversity check: flag recent posts to avoid repetition
    if workspace_id:
        recent_posts = await _fetch_recent_posts(db, workspace_id, pillar, platform)
        if recent_posts:
            prompt_parts.append(f"\nRecent posts on this pillar+platform (AVOID repeating topics/hooks):")
            for rp in recent_posts[:3]:
                snippet = rp[:120].replace("\n", " ")
                prompt_parts.append(f"- \"{snippet}...\"")
            prompt_parts.append("")
            prompt_parts.append("IMPORTANT: Generate something different from the above. Fresh angle, new hook.")

    prompt_parts.append("")
    prompt_parts.append(
        """Return JSON with this exact schema:
{
  "content": "the main post text",
  "topic": "a concise topic title for this post",
  "variants": ["alternative version 1", "alternative version 2"],
  "brand_voice_score": 0.85
}"""
    )

    prompt = "\n".join(prompt_parts)

    # Call LLM
    try:
        result = await call_llm_json(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.8,
            max_tokens=1500,
        )

        if not result or not isinstance(result, dict):
            logger.warning(f"LLM returned invalid JSON for slot {slot.id}")
            return None

        if not result.get("content"):
            logger.warning(f"LLM returned empty content for slot {slot.id}")
            return None

        return {
            "content": result["content"],
            "topic": result.get("topic", pillar),
            "variants": result.get("variants", []),
            "brand_voice_score": result.get("brand_voice_score", 0.7),
            "prompt_used": f"System: {system_prompt[:200]}... User: {prompt[:200]}...",
            "model": "openai/gpt-4o",
            "tokens": len(result["content"].split()) * 2,  # rough estimate
        }

    except Exception as e:
        logger.error(f"LLM generation failed for slot {slot.id}: {e}")
        return None
