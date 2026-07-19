"""Multi-language caption translator — translate captions for global reach.

Translates content into target languages while preserving platform
tone and formatting.
"""
import logging
from typing import Any

from app.services.llm import call_llm

logger = logging.getLogger(__name__)

LANGUAGE_NAMES = {
    "en": "English", "es": "Spanish", "fr": "French", "de": "German",
    "it": "Italian", "pt": "Portuguese", "ja": "Japanese", "ko": "Korean",
    "zh": "Chinese", "ar": "Arabic", "hi": "Hindi", "ru": "Russian",
    "nl": "Dutch", "sv": "Swedish", "pl": "Polish", "tr": "Turkish",
    "th": "Thai", "vi": "Vietnamese", "id": "Indonesian", "ms": "Malay",
}


async def translate_caption(
    caption: str,
    target_language: str,
    source_language: str = "en",
    platform: str = "linkedin",
    preserve_hashtags: bool = True,
    provider: str = "openai",
) -> dict[str, Any]:
    """Translate a caption to the target language.

    Preserves platform tone, formatting, and optionally hashtags.
    """
    target_name = LANGUAGE_NAMES.get(target_language, target_language)

    system_prompt = (
        f"You are an expert social media translator. "
        f"Translate the following {platform} caption to {target_name}.\n\n"
        "Rules:\n"
        "- Preserve the original tone and style\n"
        "- Keep the same line break structure\n"
        "- Keep hashtags in English (don't translate them)\n"
        "- Keep @mentions unchanged\n"
        "- Keep URLs unchanged\n"
        "- Adapt cultural references if needed\n"
        "- Maintain the same engagement level\n"
    )

    if preserve_hashtags:
        system_prompt += "- Preserve all hashtags exactly as-is\n"

    try:
        translated = await call_llm(
            prompt=f"Translate this caption:\n\n{caption}",
            system_prompt=system_prompt,
            provider=provider,
            max_tokens=1500,
            temperature=0.3,
        )

        if translated:
            return {
                "original": caption,
                "translated": translated,
                "source_language": source_language,
                "target_language": target_language,
                "target_language_name": target_name,
                "platform": platform,
                "char_count": len(translated),
                "word_count": len(translated.split()),
            }

    except Exception as e:
        logger.error(f"Translation failed: {e}")

    return {
        "original": caption,
        "translated": caption,
        "error": "Translation failed",
        "source_language": source_language,
        "target_language": target_language,
    }


async def translate_multi_language(
    caption: str,
    target_languages: list[str],
    platform: str = "linkedin",
    provider: str = "openai",
) -> dict[str, Any]:
    """Translate a caption into multiple languages at once."""
    import asyncio

    tasks = {
        lang: translate_caption(caption, lang, platform=platform, provider=provider)
        for lang in target_languages
    }

    results: dict[str, Any] = {}
    responses = await asyncio.gather(*tasks.values(), return_exceptions=True)

    for lang, response in zip(tasks.keys(), responses):
        if isinstance(response, Exception):
            results[lang] = {"error": str(response)}
        else:
            results[lang] = response

    return {
        "original": caption,
        "translations": results,
        "languages_count": len(target_languages),
    }
