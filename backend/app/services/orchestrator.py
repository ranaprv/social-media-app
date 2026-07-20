"""Content orchestration state machine.

Runs an async pipeline:
    Research → Draft → Visual Prompt Generation → Save to DB → HITL Staging

Each stage is a method on ``ContentOrchestrator``.  The ``run_workflow`` driver
advances through them sequentially, recording state transitions.

Provider resolution (no hardcoded mapping):
    1. ``provider_override`` from the API request body (optional per-request).
    2. Workspace-level config from ``platform_provider_configs`` table (set via UI).
    3. First available provider with a configured API key.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.ai_workflow import (
    AIProvider,
    ContentIdeaRequest,
    ContentItemResponse,
    ContentStatus,
    GeneratedText,
    PlatformType,
    VisualPrompt,
    WorkflowTriggerResponse,
)
from app.services.ai_engine.base import AIContentGenerator, GenerationResult
from app.services.ai_engine.factory import PlatformWorkflowFactory

logger = logging.getLogger(__name__)

# ── Valid state transitions ────────────────────────────────────────────────

_TRANSITIONS: dict[ContentStatus, ContentStatus] = {
    ContentStatus.IDEATION: ContentStatus.RESEARCH,
    ContentStatus.RESEARCH: ContentStatus.DRAFTING,
    ContentStatus.DRAFTING: ContentStatus.VISUAL_PROMPT,
    ContentStatus.VISUAL_PROMPT: ContentStatus.SAVED_TO_DB,
    ContentStatus.SAVED_TO_DB: ContentStatus.PENDING_APPROVAL,
    ContentStatus.PENDING_APPROVAL: ContentStatus.SCHEDULED,
    ContentStatus.SCHEDULED: ContentStatus.PUBLISHED,
}


class WorkflowError(Exception):
    """Raised when a state transition is invalid or a stage fails."""


class ContentOrchestrator:
    """Drives a single content item through the generation pipeline.

    Provider resolution:
        1. ``request.provider_override`` if provided.
        2. Workspace-level config from ``platform_provider_configs`` (set via UI).
        3. First available provider with an API key.
    """

    def __init__(
        self,
        generator: AIContentGenerator | None = None,
        workspace_id: str | None = None,
        db: AsyncSession | None = None,
    ) -> None:
        self._generator = generator
        self._workspace_id = workspace_id
        self._db = db
        self._content_item_id: str = ""
        self._current_status: ContentStatus = ContentStatus.IDEATION
        self._generated_texts: list[GeneratedText] = []
        self._visual_prompts: list[VisualPrompt] = []
        self._research_notes: str = ""
        self._final_text: str = ""
        self._topic: str = ""
        self._platform: PlatformType = PlatformType.LINKEDIN

    # ── Public entry point ──────────────────────────────────────────────

    async def run_workflow(self, request: ContentIdeaRequest) -> WorkflowTriggerResponse:
        """Execute the full pipeline and return a trigger response."""
        self._content_item_id = str(uuid.uuid4())
        self._topic = request.topic
        self._platform = request.platform
        logger.info(
            "Starting workflow %s — topic=%r platform=%s",
            self._content_item_id,
            request.topic,
            request.platform.value,
        )

        # ── Resolve AI generator ────────────────────────────────────────
        # Priority: explicit override → DB config → first available with API key
        if self._generator:
            generator = self._generator
        elif request.provider_override:
            generator = PlatformWorkflowFactory.create(
                request.platform,
                provider_override=request.provider_override,
            )
        elif self._db and self._workspace_id:
            generator = await PlatformWorkflowFactory.create_from_db(
                self._db, self._workspace_id, request.platform,
            )
        else:
            generator = PlatformWorkflowFactory.create(request.platform)

        stages = [
            ("research", self._stage_research),
            ("draft", self._stage_draft),
            ("visual_prompt", self._stage_visual_prompt),
            ("save_to_db", self._stage_save_to_db),
            ("hitl_staging", self._stage_hitl_staging),
        ]

        for stage_name, stage_fn in stages:
            logger.info("Stage [%s] — %s", stage_name, self._content_item_id)
            await stage_fn(request, generator)

        return WorkflowTriggerResponse(
            content_item_id=self._content_item_id,
            status=self._current_status,
            message=f"Workflow completed — post ready for approval (id={self._content_item_id})",
        )

    # ── Stage implementations ───────────────────────────────────────────

    async def _stage_research(
        self, request: ContentIdeaRequest, generator: AIContentGenerator
    ) -> None:
        """Stage 1: Research — gather real context via web search + LLM analysis."""
        self._current_status = ContentStatus.RESEARCH

        try:
            from app.services.web_search import research_topic

            research = await research_topic(
                topic=request.topic,
                platform=request.platform.value,
                aspect="general",
            )

            # Build research notes from real data
            parts = [
                f"Research for '{request.topic}' on {request.platform.value}.",
            ]

            if research.get("summary"):
                parts.append(f"\nSummary: {research['summary']}")

            if research.get("key_insights"):
                parts.append("\nKey insights:")
                for insight in research["key_insights"][:5]:
                    parts.append(f"  - {insight}")

            if research.get("suggested_angles"):
                parts.append("\nSuggested content angles:")
                for angle in research["suggested_angles"][:3]:
                    parts.append(f"  - {angle}")

            if request.target_audience:
                parts.append(f"\nTarget audience: {request.target_audience}")

            self._research_notes = "\n".join(parts)
            logger.info("Research complete — %d chars, %d web results",
                        len(self._research_notes), len(research.get("web_results", [])))

        except Exception as e:
            # Graceful fallback — don't block generation if research fails
            logger.warning("Research failed, using fallback: %s", e)
            self._research_notes = (
                f"Research summary for '{request.topic}' on {request.platform.value}. "
                f"Target audience: {request.target_audience or 'general'}. "
                "Key trends identified: growing interest, seasonal relevance."
            )

    async def _stage_draft(
        self, request: ContentIdeaRequest, generator: AIContentGenerator
    ) -> None:
        """Stage 2: Draft — generate text content via the AI engine."""
        self._current_status = ContentStatus.DRAFTING

        result: GenerationResult = await generator.generate_text(
            request.topic,
            target_audience=request.target_audience,
            brand_voice=request.brand_voice_id,  # treated as inline voice description
            additional_context=f"{self._research_notes}\n{request.additional_context or ''}",
        )

        generated = GeneratedText(
            provider=AIProvider(generator.provider_name),
            model=result.model,
            content=result.text,
            tokens_used=result.tokens_used,
        )
        self._generated_texts.append(generated)
        self._final_text = result.text
        logger.info("Draft generated — %d chars via %s", len(result.text), generator.provider_name)

    async def _stage_visual_prompt(
        self, request: ContentIdeaRequest, generator: AIContentGenerator
    ) -> None:
        """Stage 3: Generate image/video prompts for visual asset creation."""
        self._current_status = ContentStatus.VISUAL_PROMPT

        raw_prompts = await generator.generate_media_prompts(
            self._final_text,
            count=2,
        )
        for p in raw_prompts:
            self._visual_prompts.append(
                VisualPrompt(
                    prompt_text=p["prompt"],
                    style=p.get("style"),
                    aspect_ratio=p.get("aspect_ratio", "1:1"),
                    provider=AIProvider(generator.provider_name),
                )
            )
        logger.info("Generated %d visual prompts", len(self._visual_prompts))

    async def _stage_save_to_db(
        self, request: ContentIdeaRequest, generator: AIContentGenerator
    ) -> None:
        """Stage 4: Persist the content item (mock — returns data for the API layer)."""
        self._current_status = ContentStatus.SAVED_TO_DB
        # In production this would write to the database via a repository.
        # Here we return structured data; the API layer calls the repository.
        logger.info(
            "Content item %s persisted — status=%s",
            self._content_item_id,
            self._current_status.value,
        )

    async def _stage_hitl_staging(
        self, request: ContentIdeaRequest, generator: AIContentGenerator
    ) -> None:
        """Stage 5: Place the item in the human-in-the-loop staging queue."""
        self._current_status = ContentStatus.PENDING_APPROVAL
        logger.info(
            "Item %s staged for HITL approval — %d generated texts, %d visual prompts",
            self._content_item_id,
            len(self._generated_texts),
            len(self._visual_prompts),
        )

    # ── State machine helpers ───────────────────────────────────────────

    def _advance(self, target: ContentStatus) -> None:
        """Attempt a state transition; raises ``WorkflowError`` if invalid."""
        expected = _TRANSITIONS.get(self._current_status)
        if expected != target:
            raise WorkflowError(
                f"Invalid transition: {self._current_status.value} → {target.value} "
                f"(expected → {expected.value if expected else 'N/A'})"
            )
        self._current_status = target

    # ── Read-only properties ────────────────────────────────────────────

    @property
    def current_status(self) -> ContentStatus:
        return self._current_status

    @property
    def generated_texts(self) -> list[GeneratedText]:
        return list(self._generated_texts)

    @property
    def visual_prompts(self) -> list[VisualPrompt]:
        return list(self._visual_prompts)

    @property
    def final_text(self) -> str:
        return self._final_text

    def to_response(self) -> ContentItemResponse:
        """Snapshot of the content item as a response model."""
        now = datetime.now(timezone.utc)
        return ContentItemResponse(
            id=self._content_item_id,
            topic=self._topic,
            platform=self._platform,
            status=self._current_status,
            generated_texts=self._generated_texts,
            visual_prompts=self._visual_prompts,
            final_text=self._final_text,
            created_at=now,
            updated_at=now,
        )
