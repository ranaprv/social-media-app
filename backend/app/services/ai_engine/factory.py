"""Factory that resolves the correct AI generator.

Resolution order (no hardcoded platform→provider mapping):
    1. Explicit ``provider_override`` from the API request.
    2. Workspace-level config from ``platform_provider_configs`` table (set via UI).
    3. First available provider with a configured API key.
"""
from __future__ import annotations

import logging
from typing import Any, Type

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.schemas.ai_workflow import AIProvider, PlatformType
from app.services.ai_engine.base import AIContentGenerator

logger = logging.getLogger(__name__)

# All supported providers in preference order for fallback
_PROVIDER_FALLBACK_ORDER: list[AIProvider] = [
    AIProvider.OPENAI,
    AIProvider.CLAUDE,
    AIProvider.GEMINI,
]


class PlatformWorkflowFactory:
    """Creates the right ``AIContentGenerator`` instance.

    Usage::

        # With explicit provider (from request body)
        gen = PlatformWorkflowFactory.create(PlatformType.LINKEDIN, provider_override=AIProvider.CLAUDE)

        # With DB config lookup
        gen = await PlatformWorkflowFactory.create_from_db(
            db, workspace_id="ws-123", platform=PlatformType.LINKEDIN
        )
    """

    _registry: dict[AIProvider, Type[AIContentGenerator]] = {}

    @classmethod
    def register(cls, provider: AIProvider, generator_cls: Type[AIContentGenerator]) -> None:
        cls._registry[provider] = generator_cls
        logger.debug("Registered generator %s for provider %s", generator_cls.__name__, provider.value)

    # ── Primary creation methods ────────────────────────────────────────

    @classmethod
    async def create_from_db(
        cls,
        db: AsyncSession,
        workspace_id: str,
        platform: PlatformType,
    ) -> AIContentGenerator:
        """Look up the user-configured provider from the DB, fall back to first available."""
        if not cls._registry:
            cls._bootstrap_registry()

        provider = await cls._resolve_provider_from_db(db, workspace_id, platform)
        return cls._instantiate(provider)

    @classmethod
    def create(
        cls,
        platform: PlatformType,
        provider_override: AIProvider | None = None,
    ) -> AIContentGenerator:
        """Create generator with explicit provider or first available with an API key."""
        if not cls._registry:
            cls._bootstrap_registry()

        if provider_override:
            return cls._instantiate(provider_override)

        # No override — pick first provider that has a configured API key
        settings = get_settings()
        key_map: dict[AIProvider, str | None] = {
            AIProvider.OPENAI: settings.OPENAI_API_KEY or None,
            AIProvider.CLAUDE: settings.ANTHROPIC_API_KEY or None,
            AIProvider.GEMINI: settings.GOOGLE_AI_API_KEY or None,
        }
        for p in _PROVIDER_FALLBACK_ORDER:
            if key_map.get(p):
                logger.info("Auto-selected provider %s (has API key)", p.value)
                return cls._instantiate(p)

        # Last resort — OpenAI with mock fallback
        logger.warning("No AI API keys configured — using OpenAI mock fallback")
        return cls._instantiate(AIProvider.OPENAI)

    # ── DB resolution ───────────────────────────────────────────────────

    @classmethod
    async def _resolve_provider_from_db(
        cls,
        db: AsyncSession,
        workspace_id: str,
        platform: PlatformType,
    ) -> AIProvider:
        """Query ``platform_provider_configs`` for the user's chosen provider."""
        try:
            from app.models.ai_workflow import PlatformProviderConfig

            result = await db.execute(
                select(PlatformProviderConfig).where(
                    PlatformProviderConfig.workspace_id == workspace_id,
                    PlatformProviderConfig.platform == platform.value,
                    PlatformProviderConfig.is_active == 1,
                )
            )
            config = result.scalar_one_or_none()

            if config:
                try:
                    provider = AIProvider(config.provider)
                    logger.info(
                        "Resolved provider=%s for platform=%s workspace=%s (from DB config)",
                        provider.value,
                        platform.value,
                        workspace_id,
                    )
                    return provider
                except ValueError:
                    logger.warning("Invalid provider '%s' in DB config — falling back", config.provider)

        except Exception:
            logger.exception("Failed to read provider config from DB — falling back")

        # Fallback: first available with API key
        settings = get_settings()
        key_map: dict[AIProvider, str | None] = {
            AIProvider.OPENAI: settings.OPENAI_API_KEY or None,
            AIProvider.CLAUDE: settings.ANTHROPIC_API_KEY or None,
            AIProvider.GEMINI: settings.GOOGLE_AI_API_KEY or None,
        }
        for p in _PROVIDER_FALLBACK_ORDER:
            if key_map.get(p):
                return p

        return AIProvider.OPENAI  # mock fallback

    # ── Internal helpers ────────────────────────────────────────────────

    @classmethod
    def _instantiate(cls, provider: AIProvider) -> AIContentGenerator:
        """Create a generator instance, passing the relevant API key."""
        settings = get_settings()
        api_key_map: dict[AIProvider, str | None] = {
            AIProvider.CLAUDE: settings.ANTHROPIC_API_KEY or None,
            AIProvider.OPENAI: settings.OPENAI_API_KEY or None,
            AIProvider.GEMINI: settings.GOOGLE_AI_API_KEY or None,
        }
        generator_cls = cls._registry.get(provider)
        if generator_cls is None:
            raise ValueError(f"No generator registered for provider: {provider.value}")

        instance = generator_cls(api_key=api_key_map.get(provider))
        logger.info("Created %s generator", instance.__class__.__name__)
        return instance

    @classmethod
    def _bootstrap_registry(cls) -> None:
        from app.services.ai_engine.claude_linkedin import ClaudeLinkedInGenerator
        from app.services.ai_engine.openai_x import OpenAIXGenerator
        from app.services.ai_engine.gemini_instagram import GeminiInstagramGenerator

        cls.register(AIProvider.CLAUDE, ClaudeLinkedInGenerator)
        cls.register(AIProvider.OPENAI, OpenAIXGenerator)
        cls.register(AIProvider.GEMINI, GeminiInstagramGenerator)
