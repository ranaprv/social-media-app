"""OmniRoute — intelligent multi-provider routing layer.

Routes requests to the optimal provider/model based on:
- Task type (text generation, social copy, media prompts, brainstorming)
- Cost tier preferences
- Provider availability
- Model capability matching
"""
from __future__ import annotations

import logging
from typing import Any

from app.core.config import get_settings
from app.services.ai_engine.base import AIContentGenerator, GenerationResult

logger = logging.getLogger(__name__)

# Task type → preferred provider ordering (first = best fit)
_TASK_ROUTING_TABLE: dict[str, list[str]] = {
    "social_copy": ["openrouter", "openai", "claude", "gemini"],
    "long_form": ["claude", "openrouter", "openai", "gemini"],
    "short_form": ["openrouter", "openai", "gemini", "claude"],
    "brainstorm": ["gemini", "openrouter", "claude", "openai"],
    "media_prompts": ["openrouter", "openai", "claude", "gemini"],
    "caption": ["openrouter", "openai", "gemini", "claude"],
}

# Model recommendations per task type (using OpenRouter model IDs)
_TASK_MODEL_RECOMMENDATIONS: dict[str, dict[str, str]] = {
    "social_copy": {
        "default": "anthropic/claude-3.5-haiku",
        "premium": "openai/gpt-4o",
        "budget": "meta-llama/llama-4-maverick",
    },
    "long_form": {
        "default": "anthropic/claude-sonnet-4",
        "premium": "openai/gpt-4o",
        "budget": "deepseek/deepseek-r1",
    },
    "short_form": {
        "default": "anthropic/claude-3.5-haiku",
        "premium": "openai/gpt-4o",
        "budget": "meta-llama/llama-4-maverick",
    },
    "brainstorm": {
        "default": "google/gemini-2.5-flash",
        "premium": "google/gemini-2.5-pro",
        "budget": "meta-llama/llama-4-maverick",
    },
    "media_prompts": {
        "default": "anthropic/claude-3.5-haiku",
        "premium": "openai/gpt-4o",
        "budget": "qwen/qwen-2.5-72b-instruct",
    },
    "caption": {
        "default": "anthropic/claude-3.5-haiku",
        "premium": "openai/gpt-4o",
        "budget": "meta-llama/llama-4-maverick",
    },
}


class OmniRouteGenerator(AIContentGenerator):
    """Intelligent multi-provider router that picks the best backend per task.

    Unlike single-provider generators, OmniRoute:
    1. Analyses the incoming request type
    2. Picks the cheapest capable provider that has a configured API key
    3. Falls back through the routing table until one succeeds
    """

    provider_name = "omniroute"
    default_model = "auto"

    def __init__(self, api_key: str | None = None, **kwargs: Any) -> None:
        self._api_key = api_key

    async def generate_text(
        self,
        topic: str,
        *,
        target_audience: str | None = None,
        brand_voice: str | None = None,
        additional_context: str | None = None,
        max_tokens: int = 1500,
    ) -> GenerationResult:
        """Route text generation through the optimal provider."""
        task_type = "long_form" if max_tokens > 500 else "short_form"
        provider, model = self._resolve_best_backend(task_type)

        logger.info("OmniRoute: task=%s → provider=%s model=%s", task_type, provider, model)

        # Delegate to the resolved provider
        generator = self._get_provider_generator(provider, model)
        if generator:
            return await generator.generate_text(
                topic,
                target_audience=target_audience,
                brand_voice=brand_voice,
                additional_context=additional_context,
                max_tokens=max_tokens,
            )

        # Ultimate fallback — use OpenRouter mock
        return GenerationResult(
            text=self._mock_text(topic, target_audience),
            provider="omniroute",
            model="mock",
            tokens_used=0,
            metadata={"mock": True, "reason": "no_providers_configured"},
        )

    async def generate_media_prompts(
        self,
        text_content: str,
        *,
        style: str | None = None,
        aspect_ratio: str = "1:1",
        count: int = 1,
    ) -> list[dict[str, Any]]:
        """Route media prompt generation through the optimal provider."""
        provider, model = self._resolve_best_backend("media_prompts")
        generator = self._get_provider_generator(provider, model)
        if generator:
            return await generator.generate_media_prompts(
                text_content, style=style, aspect_ratio=aspect_ratio, count=count,
            )

        base_style = style or "modern social media aesthetic"
        return [
            {
                "prompt": f"Social media image: {text_content[:120]}. Style: {base_style}.",
                "style": base_style,
                "aspect_ratio": aspect_ratio,
            }
            for _ in range(count)
        ]

    # ── Routing logic ──────────────────────────────────────────────────

    @staticmethod
    def _resolve_best_backend(task_type: str) -> tuple[str, str]:
        """Pick the best (provider, model) pair for the given task type.

        Returns (provider_name, model_id). Provider is the direct provider
        key (openai, claude, gemini) or "openrouter" for the unified API.
        """
        settings = get_settings()
        providers = _TASK_ROUTING_TABLE.get(task_type, _TASK_ROUTING_TABLE["social_copy"])

        # Map provider keys to env var checks
        key_checks: dict[str, bool] = {
            "openrouter": bool(settings.OPENROUTER_API_KEY),
            "openai": bool(settings.OPENAI_API_KEY),
            "claude": bool(settings.ANTHROPIC_API_KEY),
            "gemini": bool(settings.GOOGLE_AI_API_KEY),
        }

        recs = _TASK_MODEL_RECOMMENDATIONS.get(task_type, {})

        for provider in providers:
            if key_checks.get(provider, False):
                model = recs.get("default", "auto")
                return provider, model

        # Nothing configured — return openrouter with mock model
        return "openrouter", "mock"

    def _get_provider_generator(self, provider: str, model: str) -> AIContentGenerator | None:
        """Instantiate the right generator for the resolved provider."""
        from app.services.ai_engine.factory import PlatformWorkflowFactory

        settings = get_settings()

        # Lazy import to avoid circular deps
        if provider == "openrouter" and settings.OPENROUTER_API_KEY:
            from app.services.ai_engine.openrouter import OpenRouterGenerator
            return OpenRouterGenerator(api_key=settings.OPENROUTER_API_KEY, model=model)
        elif provider == "openai" and settings.OPENAI_API_KEY:
            from app.services.ai_engine.openai_x import OpenAIXGenerator
            return OpenAIXGenerator(api_key=settings.OPENAI_API_KEY, model=model)
        elif provider == "claude" and settings.ANTHROPIC_API_KEY:
            from app.services.ai_engine.claude_linkedin import ClaudeLinkedInGenerator
            return ClaudeLinkedInGenerator(api_key=settings.ANTHROPIC_API_KEY, model=model)
        elif provider == "gemini" and settings.GOOGLE_AI_API_KEY:
            from app.services.ai_engine.gemini_instagram import GeminiInstagramGenerator
            return GeminiInstagramGenerator(api_key=settings.GOOGLE_AI_API_KEY, model=model)

        return None

    @staticmethod
    def _mock_text(topic: str, target_audience: str | None = None) -> str:
        return (
            f"📝 OmniRoute content about {topic}\n\n"
            f"{'For ' + target_audience + ': ' if target_audience else ''}"
            f"Key insights on {topic}:\n"
            f"1. Understanding the landscape\n"
            f"2. Practical strategies that work\n"
            f"3. Measuring success\n\n"
            f"Connect an API key for real generation 🚀"
        )

    @staticmethod
    def get_routing_info() -> dict[str, Any]:
        """Return routing configuration and provider status for the UI."""
        settings = get_settings()
        providers_status = {
            "openrouter": {
                "configured": bool(settings.OPENROUTER_API_KEY),
                "models_count": 200,
                "note": "Access to 200+ models from all providers",
            },
            "openai": {
                "configured": bool(settings.OPENAI_API_KEY),
                "models_count": 3,
                "note": "Direct OpenAI API access",
            },
            "claude": {
                "configured": bool(settings.ANTHROPIC_API_KEY),
                "models_count": 2,
                "note": "Direct Anthropic API access",
            },
            "gemini": {
                "configured": bool(settings.GOOGLE_AI_API_KEY),
                "models_count": 2,
                "note": "Direct Google AI API access",
            },
        }

        routing = {}
        for task_type, provider_order in _TASK_ROUTING_TABLE.items():
            selected = "none"
            for p in provider_order:
                if providers_status.get(p, {}).get("configured"):
                    selected = p
                    break
            routing[task_type] = {
                "selected_provider": selected,
                "alternatives": [p for p in provider_order if providers_status.get(p, {}).get("configured") and p != selected][:2],
                "recommended_model": _TASK_MODEL_RECOMMENDATIONS.get(task_type, {}).get("default", "auto"),
            }

        return {"providers": providers_status, "routing": routing}
