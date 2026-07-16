"""Abstract base class for all AI content generators."""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class GenerationResult:
    """Unified return type for all generators."""
    text: str
    provider: str
    model: str
    tokens_used: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class AIContentGenerator(ABC):
    """Abstract base that every platform-specific generator must implement.

    Contract:
        * ``generate_text``          → long/short-form copy
        * ``generate_media_prompts`` → image/video generation prompts
    """

    provider_name: str  # e.g. "claude", "openai", "gemini"
    default_model: str

    @abstractmethod
    async def generate_text(
        self,
        topic: str,
        *,
        target_audience: str | None = None,
        brand_voice: str | None = None,
        additional_context: str | None = None,
        max_tokens: int = 1500,
    ) -> GenerationResult:
        """Generate platform-optimised text content for *topic*."""

    @abstractmethod
    async def generate_media_prompts(
        self,
        text_content: str,
        *,
        style: str | None = None,
        aspect_ratio: str = "1:1",
        count: int = 1,
    ) -> list[dict[str, Any]]:
        """Return a list of image/video generation prompt dicts.

        Each dict must contain at minimum ``{"prompt": str, "style": str}``.
        """

    # ── helpers ─────────────────────────────────────────────────────────

    def _build_system_prompt(self, platform: str, brand_voice: str | None = None) -> str:
        """Build a system prompt with platform-specific tone guidelines."""
        base = (
            f"You are an expert social media content creator specialising in {platform}. "
            "Write engaging, platform-native content. "
        )
        if brand_voice:
            base += f"Adopt this brand voice: {brand_voice} "
        return base

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} provider={self.provider_name!r} model={self.default_model!r}>"
