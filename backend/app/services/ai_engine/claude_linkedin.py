"""Claude-powered generator optimised for LinkedIn long-form content."""
from __future__ import annotations

import logging
from typing import Any

from app.services.ai_engine.base import AIContentGenerator, GenerationResult

logger = logging.getLogger(__name__)

# LinkedIn-specific system prompt constants
_LINKEDIN_SYSTEM_PREFIX = (
    "You are a LinkedIn thought-leadership content strategist. "
    "Write professional, insight-driven posts that spark discussion. "
    "Use short paragraphs, line breaks for readability, and a compelling hook in the first line."
)


class ClaudeLinkedInGenerator(AIContentGenerator):
    """Generates LinkedIn posts via Anthropic Claude."""

    provider_name = "claude"
    default_model = "claude-sonnet-4-20250514"

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
        """Call Anthropic Messages API for a LinkedIn post draft."""
        system_prompt = _LINKEDIN_SYSTEM_PREFIX
        if brand_voice:
            system_prompt += f"\nBrand voice: {brand_voice}"
        if target_audience:
            system_prompt += f"\nTarget audience: {target_audience}"

        user_prompt = f"Write a LinkedIn post about: {topic}"
        if additional_context:
            user_prompt += f"\n\nAdditional context: {additional_context}"

        # ── Real Anthropic SDK call (when API key is configured) ────────
        if self._api_key:
            try:
                import anthropic

                client = anthropic.AsyncAnthropic(api_key=self._api_key)
                response = await client.messages.create(
                    model=self.default_model,
                    max_tokens=max_tokens,
                    temperature=0.7,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}],
                )
                text = response.content[0].text if response.content else ""
                tokens = getattr(response, "usage", None)
                total_tokens = (tokens.input_tokens + tokens.output_tokens) if tokens else 0
                logger.info("Claude LinkedIn generation OK — %d tokens", total_tokens)
                return GenerationResult(
                    text=text,
                    provider=self.provider_name,
                    model=self.default_model,
                    tokens_used=total_tokens,
                )
            except Exception:
                logger.exception("Anthropic SDK call failed")

        # ── Mock fallback (no API key or SDK error) ────────────────────
        logger.warning("Claude LinkedIn: using mock fallback (no API key)")
        audience_text = target_audience if target_audience else "professionals"
        mock_text = (
            f"\U0001f680 {topic}\n\n"
            f"I've been thinking a lot about {topic} lately, and here's my take:\n\n"
            f"The key insight is that {audience_text} "
            f"need to embrace change early.\n\n"
            f"3 things to remember:\n"
            f"1. Start small, iterate fast\n"
            f"2. Measure what matters\n"
            f"3. Share your learnings\n\n"
            f"What's your experience? \U0001f447\n\n"
            f"#ThoughtLeadership #ProfessionalGrowth"
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
        """Generate DALL-E / image prompts for a LinkedIn carousel or banner."""
        base_style = style or "professional corporate photography, clean design, blue tones"
        prompts = []
        for i in range(count):
            prompts.append({
                "prompt": (
                    f"A professional LinkedIn banner visualising: {text_content[:120]}. "
                    f"Style: {base_style}. Aspect ratio: {aspect_ratio}."
                ),
                "style": base_style,
                "aspect_ratio": aspect_ratio,
            })
        return prompts
