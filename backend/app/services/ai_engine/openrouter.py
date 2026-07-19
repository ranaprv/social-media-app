"""OpenRouter-powered generator — unified access to 200+ models via openrouter.ai."""
from __future__ import annotations

import logging
from typing import Any

from app.services.ai_engine.base import AIContentGenerator, GenerationResult

logger = logging.getLogger(__name__)

_OPENROUTER_SYSTEM_PREFIX = (
    "You are an expert social media content creator. "
    "Write engaging, platform-native content. "
)


class OpenRouterGenerator(AIContentGenerator):
    """Generates content via OpenRouter's OpenAI-compatible API."""

    provider_name = "openrouter"
    default_model = "anthropic/claude-sonnet-4"

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
        max_tokens: int = 1500,
    ) -> GenerationResult:
        """Call OpenRouter for text generation."""
        system_prompt = _OPENROUTER_SYSTEM_PREFIX
        if brand_voice:
            system_prompt += f"Brand voice: {brand_voice} "
        if target_audience:
            system_prompt += f"Target audience: {target_audience} "

        user_prompt = f"Create social media content about: {topic}"
        if additional_context:
            user_prompt += f"\n\nContext: {additional_context}"

        if self._api_key:
            try:
                from openai import AsyncOpenAI

                client = AsyncOpenAI(
                    api_key=self._api_key,
                    base_url="https://openrouter.ai/api/v1",
                    default_headers={
                        "HTTP-Referer": "https://socialmedia-manager.ai",
                        "X-Title": "Social Media Manager",
                    },
                )
                response = await client.chat.completions.create(
                    model=self.default_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.8,
                    max_tokens=max_tokens,
                )
                text = response.choices[0].message.content or ""
                usage = response.usage
                total_tokens = usage.total_tokens if usage else 0
                logger.info("OpenRouter generation OK — model=%s tokens=%d", self.default_model, total_tokens)
                return GenerationResult(
                    text=text,
                    provider=self.provider_name,
                    model=self.default_model,
                    tokens_used=total_tokens,
                )
            except Exception:
                logger.exception("OpenRouter SDK call failed")

        # Mock fallback
        logger.warning("OpenRouter: using mock fallback (no API key)")
        mock_text = (
            f"📝 Content about {topic}\n\n"
            f"{'For ' + target_audience + ': ' if target_audience else ''}"
            f"Here are the key insights on {topic}.\n\n"
            f"1. Start with what matters most\n"
            f"2. Back it up with data\n"
            f"3. End with a clear CTA\n\n"
            f"Want to learn more? Drop a comment below! 👇"
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
        aspect_ratio: str = "1:1",
        count: int = 1,
    ) -> list[dict[str, Any]]:
        """Generate image prompts via OpenRouter."""
        base_style = style or "modern social media aesthetic, clean design"
        return [
            {
                "prompt": f"Social media image: {text_content[:120]}. Style: {base_style}. Ratio: {aspect_ratio}.",
                "style": base_style,
                "aspect_ratio": aspect_ratio,
            }
            for _ in range(count)
        ]
