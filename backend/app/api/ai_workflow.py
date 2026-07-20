"""FastAPI router for the autonomous AI content workflow pipeline.

Endpoints:
    POST /content/trigger-workflow       — kick off AI research + generation pipeline
    POST /content/approve-post/{id}      — HITL approval → schedule the post
    POST /analytics/ingest               — ingest platform stats + trigger feedback loop
    GET  /content/provider-config/{ws}   — list provider configs for a workspace
    PUT  /content/provider-config/{ws}   — upsert provider config for a platform
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.ai_workflow import (
    AIProvider,
    AnalyticsIngestRequest,
    ContentIdeaRequest,
    ContentStatus,
    PerformanceScoreResponse,
    PlatformType,
    PostApprovalRequest,
    ProviderConfigBulkResponse,
    ProviderConfigResponse,
    WorkflowTriggerResponse,
)
from app.services.analytics_feedback import AnalyticsFeedbackLoop
from app.services.orchestrator import ContentOrchestrator, WorkflowError

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ai-workflow"])


# ── POST /content/trigger-workflow ────────────────────────────────────────

@router.post(
    "/content/trigger-workflow",
    response_model=WorkflowTriggerResponse,
    summary="Trigger autonomous AI content generation pipeline",
)
async def trigger_workflow(
    request: ContentIdeaRequest,
    db: AsyncSession = Depends(get_db),
) -> WorkflowTriggerResponse:
    """Initiate the automated AI research and generation pipeline.

    Provider selection (in priority order):
        1. ``provider_override`` in the request body (optional per-request).
        2. Workspace-level config from ``platform_provider_configs`` (set via UI).
        3. First available provider with a configured API key.

    Pipeline stages:
        1. Research — gather context on the topic
        2. Draft    — generate platform-optimised text via the selected AI engine
        3. Visual Prompt — create image/video generation prompts
        4. Save to DB   — persist the content item
        5. HITL Staging — queue for human approval
    """
    logger.info("Workflow triggered — topic=%r platform=%s", request.topic, request.platform.value)

    # TODO: extract workspace_id from auth context / JWT
    workspace_id = "default"

    orchestrator = ContentOrchestrator(
        workspace_id=workspace_id,
        db=db,
    )

    try:
        response = await orchestrator.run_workflow(request)
    except WorkflowError as exc:
        raise HTTPException(status_code=422, detail=f"Workflow failed: {exc}") from exc
    except Exception as exc:
        logger.exception("Unexpected error in workflow")
        raise HTTPException(status_code=500, detail="Internal workflow error") from exc

    # ── Persist content item to database ────────────────────────────────
    try:
        from app.models.ai_workflow import ContentItem

        content_item = ContentItem(
            id=response.content_item_id,
            workspace_id=workspace_id,
            topic=request.topic,
            platform=request.platform.value,
            status=response.status.value,
            target_audience=request.target_audience,
            additional_context=request.additional_context,
            generated_texts=[t.model_dump() for t in orchestrator.generated_texts],
            visual_prompts=[p.model_dump() for p in orchestrator.visual_prompts],
            final_text=orchestrator.final_text,
        )
        db.add(content_item)
        await db.flush()
        logger.info("Content item %s persisted to database", response.content_item_id)
    except Exception:
        logger.exception("Failed to persist content item (non-blocking)")

    return response


# ── POST /content/approve-post/{post_id} ──────────────────────────────────

@router.post(
    "/content/approve-post/{post_id}",
    response_model=dict[str, Any],
    summary="Approve a post (HITL step) and move to SCHEDULED",
)
async def approve_post(
    post_id: str,
    request: PostApprovalRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Simulate the Human-In-The-Loop dashboard step.

    Moves a post from ``PENDING_APPROVAL`` → ``SCHEDULED``.
    """
    try:
        from app.models.ai_workflow import ContentItem, PlatformPost

        # Try ContentItem first
        result = await db.execute(
            select(ContentItem).where(ContentItem.id == post_id)
        )
        content_item = result.scalar_one_or_none()

        if content_item:
            if content_item.status != ContentStatus.PENDING_APPROVAL.value:
                raise HTTPException(
                    status_code=422,
                    detail=f"Content item is '{content_item.status}', expected 'pending_approval'",
                )
            content_item.status = ContentStatus.SCHEDULED.value
            content_item.scheduled_at = request.scheduled_at or datetime.now(timezone.utc)
            content_item.approved_at = datetime.now(timezone.utc)
            if request.override_text:
                content_item.final_text = request.override_text
            await db.flush()

            logger.info("Content item %s approved → scheduled", post_id)
            return {
                "id": post_id,
                "status": "scheduled",
                "scheduled_at": content_item.scheduled_at.isoformat(),
                "message": "Post approved and scheduled for publishing",
            }

        # Try PlatformPost
        result = await db.execute(
            select(PlatformPost).where(PlatformPost.id == post_id)
        )
        platform_post = result.scalar_one_or_none()

        if platform_post:
            if platform_post.status != "pending_approval":
                raise HTTPException(
                    status_code=422,
                    detail=f"Platform post is '{platform_post.status}', expected 'pending_approval'",
                )
            platform_post.status = "scheduled"
            platform_post.updated_at = datetime.now(timezone.utc)
            await db.flush()

            logger.info("Platform post %s approved → scheduled", post_id)
            return {
                "id": post_id,
                "status": "scheduled",
                "message": "Platform post approved and scheduled",
            }

        raise HTTPException(status_code=404, detail=f"Post {post_id} not found")

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error approving post %s", post_id)
        raise HTTPException(status_code=500, detail="Approval failed") from exc


# ── POST /analytics/ingest ────────────────────────────────────────────────

@router.post(
    "/analytics/ingest",
    response_model=PerformanceScoreResponse,
    summary="Ingest platform analytics and trigger feedback loop",
)
async def ingest_analytics(
    request: AnalyticsIngestRequest,
    db: AsyncSession = Depends(get_db),
) -> PerformanceScoreResponse:
    """Ingest raw daily platform stats and trigger the analytics feedback loop.

    1. Store raw metrics in ``platform_analytics`` table.
    2. Compute normalised performance score.
    3. If score > 7.5, embed post text and store in vector store for RAG.
    """
    # ── Look up the PlatformPost to get its text ────────────────────────
    post_text = ""
    try:
        from app.models.ai_workflow import PlatformPost

        result = await db.execute(
            select(PlatformPost).where(PlatformPost.platform_post_id == request.platform_post_id)
        )
        platform_post = result.scalar_one_or_none()
        if platform_post:
            post_text = platform_post.post_text
    except Exception:
        logger.warning("Could not look up PlatformPost for %s", request.platform_post_id)

    if not post_text:
        post_text = f"[Post {request.platform_post_id}]"

    # ── Run the feedback loop ───────────────────────────────────────────
    feedback = AnalyticsFeedbackLoop()
    score_response = await feedback.process_performance_and_store_rag(
        platform_post_id=request.platform_post_id,
        post_text=post_text,
        impressions=request.impressions,
        engagements=request.engagements,
        shares=request.shares,
        clicks=request.clicks,
        platform=request.platform.value,
        recorded_at=request.recorded_at,
    )

    # ── Persist raw analytics ───────────────────────────────────────────
    try:
        from app.models.ai_workflow import PlatformAnalytics

        analytics_record = PlatformAnalytics(
            id=str(uuid.uuid4()),
            platform_post_id=platform_post.id if platform_post else request.platform_post_id,
            platform=request.platform.value,
            impressions=request.impressions,
            engagements=request.engagements,
            shares=request.shares,
            clicks=request.clicks,
            likes=request.likes,
            comments=request.comments,
            reach=request.reach,
            performance_score=score_response.performance_score,
            stored_as_embedding=1 if score_response.stored_as_embedding else 0,
            recorded_at=request.recorded_at,
        )
        db.add(analytics_record)
        await db.flush()
    except Exception:
        logger.exception("Failed to persist analytics record (non-blocking)")

    # ── Update prompt performance scores (self-improving loop) ─────────
    try:
        from app.services.prompt_evolution import update_prompt_performance
        total_eng = request.engagements + request.shares + request.clicks
        eng_rate = (total_eng / request.impressions * 100) if request.impressions > 0 else 0.0
        # Find the post_id linked to this platform_post and update its prompt score
        if platform_post and platform_post.content_item_id:
            await update_prompt_performance(db, platform_post.id, eng_rate)
    except Exception:
        logger.exception("Failed to update prompt performance (non-blocking)")

    return score_response


# ── Provider Config CRUD (UI settings) ───────────────────────────────────

@router.get(
    "/content/provider-config/{workspace_id}",
    response_model=ProviderConfigBulkResponse,
    summary="List AI provider configs for a workspace",
)
async def list_provider_configs(
    workspace_id: str,
    db: AsyncSession = Depends(get_db),
) -> ProviderConfigBulkResponse:
    """Return all provider configs for a workspace — one row per platform.

    The UI settings page calls this to show dropdowns for each platform.
    """
    from app.models.ai_workflow import PlatformProviderConfig

    result = await db.execute(
        select(PlatformProviderConfig).where(
            PlatformProviderConfig.workspace_id == workspace_id,
        )
    )
    configs = result.scalars().all()

    return ProviderConfigBulkResponse(
        workspace_id=workspace_id,
        configs=[
            ProviderConfigResponse(
                id=c.id,
                workspace_id=c.workspace_id,
                platform=PlatformType(c.platform),
                provider=AIProvider(c.provider),
                model=c.model,
                is_active=bool(c.is_active),
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
            for c in configs
        ],
    )


class _UpsertBody(BaseModel):
    """Body for upserting a provider config."""
    provider: AIProvider
    model: str | None = None
    is_active: bool = True


@router.put(
    "/content/provider-config/{workspace_id}/{platform}",
    response_model=ProviderConfigResponse,
    summary="Set (upsert) the AI provider for a specific platform",
)
async def upsert_provider_config(
    workspace_id: str,
    platform: PlatformType,
    body: _UpsertBody,
    db: AsyncSession = Depends(get_db),
) -> ProviderConfigResponse:
    """Create or update the AI provider for a platform within a workspace.

    Called by the UI settings page when the user picks a provider from the dropdown.
    """
    from app.models.ai_workflow import PlatformProviderConfig

    result = await db.execute(
        select(PlatformProviderConfig).where(
            PlatformProviderConfig.workspace_id == workspace_id,
            PlatformProviderConfig.platform == platform.value,
        )
    )
    config = result.scalar_one_or_none()

    now = datetime.now(timezone.utc)

    if config:
        config.provider = body.provider.value
        config.model = body.model
        config.is_active = 1 if body.is_active else 0
        config.updated_at = now
    else:
        config = PlatformProviderConfig(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            platform=platform.value,
            provider=body.provider.value,
            model=body.model,
            is_active=1 if body.is_active else 0,
            created_at=now,
            updated_at=now,
        )
        db.add(config)

    await db.flush()
    logger.info("Provider config upserted — ws=%s platform=%s provider=%s", workspace_id, platform.value, body.provider.value)

    return ProviderConfigResponse(
        id=config.id,
        workspace_id=config.workspace_id,
        platform=PlatformType(config.platform),
        provider=AIProvider(config.provider),
        model=config.model,
        is_active=bool(config.is_active),
        created_at=config.created_at,
        updated_at=config.updated_at,
    )
