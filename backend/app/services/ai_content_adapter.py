"""AI Content Adapter — rewrites content for each platform using LLM.

Takes a base post and generates platform-optimized versions:
  - LinkedIn: professional tone, longer form, line breaks
  - X: concise, punchy, 280 chars, thread-ready
  - Instagram: visual-first caption, hashtags, emoji
  - Facebook: conversational, question-driven
  - YouTube: SEO-optimized title + description
"""
import logging
from typing import Any

from app.services.llm import call_llm
from app.services.cross_post_templates import PLATFORM_TEMPLATES

logger = logging.getLogger(__name__)

PLATFORM_SYSTEM_PROMPTS = {
    "linkedin": (
        "You are an expert LinkedIn content writer. Rewrite the given content for LinkedIn. "
        "Make it professional, insightful, and engaging. Use line breaks for readability. "
        "Start with a hook. End with a question or CTA. Keep it under 3000 characters."
    ),
    "x": (
        "You are an expert X/Twitter writer. Rewrite the given content as a tweet. "
        "Be concise, punchy, and attention-grabbing. Maximum 280 characters. "
        "Use 1-2 relevant hashtags. No line breaks. Make every word count."
    ),
    "instagram": (
        "You are an expert Instagram caption writer. Rewrite the given content for Instagram. "
        "Make it visual, engaging, and relatable. Use emojis. Add 3-5 hashtags at the end. "
        "Put the key message in the first 125 characters. Max 2200 characters."
    ),
    "facebook": (
        "You are an expert Facebook content writer. Rewrite the given content for Facebook. "
        "Make it conversational and engaging. Ask questions to drive comments. "
        "Keep it concise (80-250 characters optimal for engagement)."
    ),
    "youtube": (
        "You are an expert YouTube content writer. Rewrite the given content as a YouTube "
        "video description. Start with a compelling summary (200-500 chars). "
        "Include relevant keywords for SEO. Add timestamps if applicable. "
        "End with subscribe + next video CTA. Max 5000 characters."
    ),
}


async def adapt_content_ai(
    content: str,
    source_platform: str,
    target_platform: str,
    provider: str = "openai",
    tone: str | None = None,
) -> dict[str, Any]:
    """Use AI to rewrite content for a specific platform.

    Falls back to rule-based adaptation if no LLM is available.

    Returns:
    {
        "adapted_content": str,
        "platform": str,
        "source_platform": str,
        "method": "ai" | "rule_based",
        "word_count": int,
        "char_count": int,
    }
    """
    system_prompt = PLATFORM_SYSTEM_PROMPTS.get(target_platform)
    if not system_prompt:
        return {
            "adapted_content": content,
            "platform": target_platform,
            "source_platform": source_platform,
            "method": "passthrough",
            "word_count": len(content.split()),
            "char_count": len(content),
        }

    if tone:
        system_prompt += f" Use a {tone} tone."

    user_prompt = f"Rewrite this content for {target_platform}:\n\n{content}"

    try:
        adapted = await call_llm(
            prompt=user_prompt,
            system_prompt=system_prompt,
            provider=provider,
            max_tokens=1500,
            temperature=0.7,
        )

        if adapted:
            # Apply platform limits
            limits = PLATFORM_TEMPLATES.get(target_platform, {})
            max_caption = limits.get("max_caption", 999999)
            if len(adapted) > max_caption:
                adapted = adapted[:max_caption - 3] + "..."

            return {
                "adapted_content": adapted,
                "platform": target_platform,
                "source_platform": source_platform,
                "method": "ai",
                "word_count": len(adapted.split()),
                "char_count": len(adapted),
            }

    except Exception as e:
        logger.warning(f"AI adaptation failed for {target_platform}: {e}")

    # Fallback to rule-based
    from app.services.cross_post_templates import adapt_content_for_platform
    result = adapt_content_for_platform(content, source_platform, target_platform)

    return {
        "adapted_content": result["content"],
        "platform": target_platform,
        "source_platform": source_platform,
        "method": "rule_based",
        "word_count": len(result["content"].split()),
        "char_count": len(result["content"]),
    }


async def batch_adapt_content(
    content: str,
    source_platform: str,
    target_platforms: list[str],
    provider: str = "openai",
    tone: str | None = None,
) -> dict[str, Any]:
    """Adapt content for multiple platforms in one call.

    Returns all adapted versions keyed by platform.
    """
    import asyncio

    tasks = {
        p: adapt_content_ai(content, source_platform, p, provider, tone)
        for p in target_platforms
        if p != source_platform
    }

    results: dict[str, Any] = {}
    if tasks:
        responses = await asyncio.gather(*tasks.values(), return_exceptions=True)
        for platform, response in zip(tasks.keys(), responses):
            if isinstance(response, Exception):
                logger.error(f"Batch adapt failed for {platform}: {response}")
                results[platform] = {
                    "adapted_content": content,
                    "platform": platform,
                    "method": "fallback",
                    "error": str(response),
                }
            else:
                results[platform] = response

    # Include original
    results[source_platform] = {
        "adapted_content": content,
        "platform": source_platform,
        "source_platform": source_platform,
        "method": "original",
        "word_count": len(content.split()),
        "char_count": len(content),
    }

    return {
        "adaptations": results,
        "source_platform": source_platform,
        "target_count": len(target_platforms),
    }
