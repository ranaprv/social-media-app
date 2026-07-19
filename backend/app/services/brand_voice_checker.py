"""Brand voice consistency checker.

Analyzes content against brand voice guidelines and reports
inconsistencies.
"""
import logging
from typing import Any

from app.services.llm import call_llm_json

logger = logging.getLogger(__name__)


async def check_brand_voice(
    content: str,
    brand_voice_config: dict[str, Any],
    platform: str = "linkedin",
    provider: str = "openai",
) -> dict[str, Any]:
    """Check if content matches brand voice guidelines.

    Args:
        content: The content to check.
        brand_voice_config: Brand voice settings (tone, style, vocabulary, etc.)
        platform: Target platform.
    """
    system_prompt = (
        "You are a brand voice consistency checker. "
        "Analyze the content against brand voice guidelines and return JSON.\n\n"
        "Return:\n"
        '- "score": 0-100 consistency score\n'
        '- "issues": [{type, description, severity, suggestion}]\n'
        '- "tone_match": "match" | "close" | "mismatch"\n'
        '- "style_match": "match" | "close" | "mismatch"\n'
        '- "vocabulary_match": "match" | "close" | "mismatch"\n'
    )

    voice_description = []
    if brand_voice_config.get("tone"):
        voice_description.append(f"Tone: {brand_voice_config['tone']}")
    if brand_voice_config.get("writing_style"):
        voice_description.append(f"Style: {brand_voice_config['writing_style']}")
    if brand_voice_config.get("vocabulary"):
        voice_description.append(f"Vocabulary: {brand_voice_config['vocabulary']}")
    if brand_voice_config.get("emoji_usage"):
        voice_description.append(f"Emoji: {brand_voice_config['emoji_usage']}")

    user_prompt = (
        f"Check this {platform} content against brand voice:\n\n"
        f"Brand Voice: {'; '.join(voice_description)}\n\n"
        f"Content:\n{content[:1000]}\n\n"
        "Identify inconsistencies in tone, style, vocabulary, and formatting."
    )

    try:
        result = await call_llm_json(
            prompt=user_prompt,
            system_prompt=system_prompt,
            provider=provider,
            temperature=0.3,
        )

        if result and isinstance(result, dict):
            return {
                "score": result.get("score", 50),
                "issues": result.get("issues", []),
                "tone_match": result.get("tone_match", "unknown"),
                "style_match": result.get("style_match", "unknown"),
                "vocabulary_match": result.get("vocabulary_match", "unknown"),
                "platform": platform,
            }

    except Exception as e:
        logger.error(f"Brand voice check failed: {e}")

    return {"score": 50, "issues": [], "error": "Check failed"}


async def batch_check_brand_voice(
    contents: list[dict[str, str]],
    brand_voice_config: dict[str, Any],
    provider: str = "openai",
) -> dict[str, Any]:
    """Check multiple pieces of content against brand voice."""
    import asyncio

    tasks = [
        check_brand_voice(
            item.get("content", ""),
            brand_voice_config,
            item.get("platform", "linkedin"),
            provider,
        )
        for item in contents
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    checked = []
    avg_score = 0
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            checked.append({"index": i, "error": str(result)})
        else:
            checked.append(result)
            avg_score += result.get("score", 0)

    avg_score = round(avg_score / max(len(checked), 1))

    return {
        "results": checked,
        "average_score": avg_score,
        "total_checked": len(checked),
        "consistency": "high" if avg_score >= 80 else "medium" if avg_score >= 60 else "low",
    }
