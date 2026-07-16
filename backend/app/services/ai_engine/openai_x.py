"""OpenAI-powered generator optimised for X/Twitter short-form threads."""
from __future__ import annotations

import logging
from typing import Any

from app.services.ai_engine.base import AIContentGenerator, GenerationResult

logger = logging.getLogger(__name__)

_TWITTER_SYSTEM_PREFIX = (
    "You are an expert X/Twitter content writer. "
    "Write concise, punchy tweets and threads. "
    "Use hooks, numbered threads, and strategic hashtags. "
    "Each tweet in a thread must be under 280 characters."
)


class OpenAIXGenerator(AIContentGenerator):
    """Generates X/Twitter posts and threads via OpenAI."""

    provider_name = "openai"
    default_model = "gpt-4o-mini"

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
        max_tokens: int = 800,
    ) -> GenerationResult:
        """Call OpenAI Chat Completions for a tweet thread."""
        system_prompt = _TWITTER_SYSTEM_PREFIX
        if brand_voice:
            system_prompt += f"\nBrand voice: {brand_voice}"
        if target_audience:
            system_prompt += f"\nTarget audience: {target_audience}"

        user_prompt = (
            f"Create a 3-5 tweet thread about: {topic}. "
            "Number each tweet. End with a CTA."
        )
        if additional_context:
            user_prompt += f"\n\nContext: {additional_context}"

        # ── Real OpenAI SDK call ────────────────────────────────────────
        if self._api_key:
            try:
                from openai import AsyncOpenAI

                client = AsyncOpenAI(api_key=self._api_key)
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
                logger.info("OpenAI X generation OK — %d tokens", total_tokens)
                return GenerationResult(
                    text=text,
                    provider=self.provider_name,
                    model=self.default_model,
                    tokens_used=total_tokens,
                )
            except Exception:
                logger.exception("OpenAI SDK call failed")

        # ── Mock fallback ──────────────────────────────────────────────
        logger.warning("OpenAI X: using mock fallback (no API key)")
        mock_text = (
            f"🧵 Thread: {topic}\n\n"
            f"1/ Here's what most people get wrong about {topic}... 👇\n\n"
            f"2/ The data tells a different story. "
            f"{'For ' + target_audience + ', ' if target_audience else ''}"
            f"the key is starting with first principles.\n\n"
            f"3/ Practical steps:\n"
            f"→ Audit your current approach\n"
            f"→ Identify one high-leverage change\n"
            f"→ Ship it this week\n\n"
            f"4/ TL;DR: {topic} is evolving fast. "
            f"Adapt or get left behind.\n\n"
            f"What's your take? Reply below 🔄"
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
        aspect_ratio: str = "16:9",
        count: int = 1,
    ) -> list[dict[str, Any]]:
        """Generate image prompts optimised for X/Twitter card previews."""
        base_style = style or "bold typography, vibrant gradient background, modern social media aesthetic"
        prompts = []
        for i in range(count):
            prompts.append({
                "prompt": (
                    f"Social media card for X/Twitter: {text_content[:120]}. "
                    f"Style: {base_style}. Ratio: {aspect_ratio}."
                ),
                "style": base_style,
                "aspect_ratio": aspect_ratio,
            })
        return prompts
