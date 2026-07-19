"""AI Caption Generator — generate platform-specific captions using LLM.

Takes a topic or base content and generates optimized captions
for each platform with proper formatting, hashtags, and CTAs.
"""
import logging
from typing import Any

from app.services.llm import call_llm

logger = logging.getLogger(__name__)

CAPTION_SYSTEM_PROMPTS = {
    "linkedin": (
        "You are an expert LinkedIn caption writer. Generate a LinkedIn post caption.\n"
        "Rules:\n"
        "- Start with a compelling hook (first 2 lines visible before 'see more')\n"
        "- Use line breaks for readability\n"
        "- Share insights, not just links\n"
        "- End with a question or CTA to drive comments\n"
        "- Keep under 3000 characters\n"
        "- Professional but human tone\n"
        "- 3-5 relevant hashtags at the end"
    ),
    "x": (
        "You are an expert X/Twitter caption writer. Generate a tweet.\n"
        "Rules:\n"
        "- Maximum 280 characters\n"
        "- Make every word count\n"
        "- Use 1-2 relevant hashtags\n"
        "- No line breaks\n"
        "- Punchy, attention-grabbing\n"
        "- Consider making it a thread starter if the topic is complex"
    ),
    "instagram": (
        "You are an expert Instagram caption writer.\n"
        "Rules:\n"
        "- First line is the hook (visible before 'more')\n"
        "- Use emojis to break up text\n"
        "- Ask a question to boost comments\n"
        "- Include a CTA (save, share, tag someone)\n"
        "- Add 3-5 hashtags at the end\n"
        "- Max 2200 characters\n"
        "- Relatable and conversational tone"
    ),
    "facebook": (
        "You are an expert Facebook post writer.\n"
        "Rules:\n"
        "- Keep it concise (80-250 characters optimal)\n"
        "- Ask questions to drive comments\n"
        "- Use a conversational tone\n"
        "- Include a clear CTA\n"
        "- No hashtag spam (0-3 max)"
    ),
    "youtube": (
        "You are an expert YouTube description writer.\n"
        "Rules:\n"
        "- First 2 lines are critical (shown before 'more')\n"
        "- Include timestamps/chapters if applicable\n"
        "- Add relevant keywords for SEO\n"
        "- Include links (social, website)\n"
        "- End with subscribe + bell CTA\n"
        "- Max 5000 characters"
    ),
}


async def generate_caption(
    topic: str,
    platform: str,
    tone: str = "professional",
    brand_voice: str | None = None,
    keywords: list[str] | None = None,
    include_hashtags: bool = True,
    include_cta: bool = True,
    provider: str = "openai",
    max_length: int | None = None,
) -> dict[str, Any]:
    """Generate an AI caption for a specific platform.

    Returns the generated caption with metadata.
    """
    system_prompt = CAPTION_SYSTEM_PROMPTS.get(platform, CAPTION_SYSTEM_PROMPTS["linkedin"])

    if brand_voice:
        system_prompt += f"\n\nBrand voice: {brand_voice}"

    user_prompt = f"Write a {platform} post about: {topic}\n\nTone: {tone}\n"
    if keywords:
        user_prompt += f"Keywords to include: {', '.join(keywords)}\n"
    if include_hashtags:
        user_prompt += "Include relevant hashtags.\n"
    if include_cta:
        user_prompt += "Include a call-to-action.\n"

    try:
        caption = await call_llm(
            prompt=user_prompt,
            system_prompt=system_prompt,
            provider=provider,
            max_tokens=1000,
            temperature=0.8,
        )

        if caption:
            # Apply length limit
            if max_length and len(caption) > max_length:
                caption = caption[:max_length - 3] + "..."

            # Extract hashtags
            words = caption.split()
            hashtags = [w for w in words if w.startswith("#")]

            return {
                "caption": caption,
                "platform": platform,
                "char_count": len(caption),
                "word_count": len(caption.split()),
                "hashtags": hashtags,
                "has_cta": any(
                    word in caption.lower()
                    for word in ["comment", "share", "save", "follow", "subscribe", "click", "link", "check out", "what do you think"]
                ),
                "provider": provider,
            }

    except Exception as e:
        logger.error(f"Caption generation failed: {e}")

    return {
        "caption": "",
        "platform": platform,
        "error": "Caption generation failed",
        "char_count": 0,
        "word_count": 0,
        "hashtags": [],
        "has_cta": False,
    }


async def generate_multi_platform_captions(
    topic: str,
    platforms: list[str],
    tone: str = "professional",
    brand_voice: str | None = None,
    keywords: list[str] | None = None,
    provider: str = "openai",
) -> dict[str, dict[str, Any]]:
    """Generate captions for multiple platforms at once."""
    import asyncio

    tasks = {
        p: generate_caption(topic, p, tone, brand_voice, keywords, provider=provider)
        for p in platforms
    }

    results: dict[str, dict[str, Any]] = {}
    responses = await asyncio.gather(*tasks.values(), return_exceptions=True)

    for platform, response in zip(tasks.keys(), responses):
        if isinstance(response, Exception):
            results[platform] = {"error": str(response), "platform": platform}
        else:
            results[platform] = response

    return results


async def improve_caption(
    caption: str,
    platform: str,
    instruction: str = "Make it more engaging",
    provider: str = "openai",
) -> dict[str, Any]:
    """Improve an existing caption with specific instructions."""
    system_prompt = (
        f"You are an expert {platform} content writer. "
        "Rewrite the caption to be better while keeping the core message. "
        f"Instruction: {instruction}"
    )

    try:
        improved = await call_llm(
            prompt=f"Improve this caption:\n\n{caption}",
            system_prompt=system_prompt,
            provider=provider,
            max_tokens=1000,
            temperature=0.7,
        )

        if improved:
            return {
                "original": caption,
                "improved": improved,
                "platform": platform,
                "instruction": instruction,
                "char_count": len(improved),
                "word_count": len(improved.split()),
            }

    except Exception as e:
        logger.error(f"Caption improvement failed: {e}")

    return {"original": caption, "improved": caption, "error": "Improvement failed"}
