"""Gemini-powered generator optimised for Instagram engaging copy + image prompts."""
from __future__ import annotations

import logging
from typing import Any

from app.services.ai_engine.base import AIContentGenerator, GenerationResult

logger = logging.getLogger(__name__)

_INSTAGRAM_SYSTEM_PREFIX = (
    "You are an Instagram content specialist. "
    "Write engaging captions that stop the scroll. "
    "Use a strong hook in the first line, storytelling, emojis strategically, "
    "and end with a clear call-to-action. Keep captions under 2200 characters."
)


class GeminiInstagramGenerator(AIContentGenerator):
    """Generates Instagram captions and image prompts via Google Gemini."""

    provider_name = "gemini"
    default_model = "gemini-2.0-flash"

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self._api_key = api_key
        self.default_model = model or self.default_model

    async def generate_text(
        self,
        topic: str,
        *,
        target_audience: str | None = None,
        brand_voice: str | None = None,
        additional_context: str | None = None,
        max_tokens: int = 1000,
    ) -> GenerationResult:
        """Call Google Gemini API for an Instagram caption."""
        system_prompt = _INSTAGRAM_SYSTEM_PREFIX
        if brand_voice:
            system_prompt += f"\nBrand voice: {brand_voice}"
        if target_audience:
            system_prompt += f"\nTarget audience: {target_audience}"

        user_prompt = f"Write an Instagram caption for a post about: {topic}"
        if additional_context:
            user_prompt += f"\n\nDetails: {additional_context}"

        # ── Real Gemini SDK call ────────────────────────────────────────
        if self._api_key:
            try:
                from google import genai

                client = genai.Client(api_key=self._api_key)
                full_prompt = f"{system_prompt}\n\n{user_prompt}"
                response = await client.aio.models.generate_content(
                    model=self.default_model,
                    contents=full_prompt,
                    config=genai.types.GenerateContentConfig(
                        temperature=0.75,
                        max_output_tokens=max_tokens,
                    ),
                )
                text = response.text or ""
                logger.info("Gemini Instagram generation OK")
                return GenerationResult(
                    text=text,
                    provider=self.provider_name,
                    model=self.default_model,
                    tokens_used=0,  # Gemini response doesn't expose token counts directly
                )
            except Exception:
                logger.exception("Gemini SDK call failed")

        # ── Mock fallback ──────────────────────────────────────────────
        logger.warning("Gemini Instagram: using mock fallback (no API key)")
        mock_text = (
            f"✨ {topic} ✨\n\n"
            f"Ever wondered why {topic} matters so much?\n\n"
            f"Here's the truth 👇\n\n"
            f"{'For ' + target_audience + ', ' if target_audience else ''}"
            f"the difference between good and great is execution.\n\n"
            f"💾 Save this for later\n"
            f"📤 Share with someone who needs this\n"
            f"💬 Drop your thoughts below\n\n"
            f"{'#Inspiration #Growth' if not target_audience else '#CustomContent #Growth'}"
        )
        return GenerationResult(
            text=mock_text,
            provider=self.provider_name,
            model=self.default_model,
            tokens_used=0,
            metadata={"mock": True},
        )

    async def generate_media_prompts(
        self,
        text_content: str,
        *,
        style: str | None = None,
        aspect_ratio: str = "4:5",
        count: int = 1,
    ) -> list[dict[str, Any]]:
        """Generate image prompts optimised for Instagram carousel / feed posts."""
        base_style = style or "vibrant lifestyle photography, warm tones, natural lighting, Instagram aesthetic"
        prompts = []
        for i in range(count):
            prompts.append({
                "prompt": (
                    f"Instagram post visualisation: {text_content[:150]}. "
                    f"Style: {base_style}. Aspect ratio: {aspect_ratio}. "
                    f"Make it scroll-stopping and visually rich."
                ),
                "style": base_style,
                "aspect_ratio": aspect_ratio,
            })
        return prompts
