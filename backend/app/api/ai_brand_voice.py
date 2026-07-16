from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
import json

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import get_settings
from app.models.user import User
from app.models.workspace import WorkspaceMember
from app.models.content import BrandVoice

router = APIRouter(prefix="/ai/brand-voice", tags=["ai-brand-voice"])


async def _call_ai(prompt: str, system_prompt: str = "") -> str:
    """Call OpenAI or return placeholder."""
    settings = get_settings()
    if settings.OPENAI_API_KEY:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.5,
                max_tokens=2000,
            )
            return response.choices[0].message.content or ""
        except Exception:
            pass
    return ""


async def _verify_workspace(workspace_id: str, user_id: str, db: AsyncSession) -> bool:
    """Verify user has access to workspace."""
    result = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
        )
    )
    return result.scalar_one_or_none() is not None


async def _get_or_create_brand_voice(workspace_id: str, db: AsyncSession) -> BrandVoice:
    """Get existing brand voice or create new one."""
    result = await db.execute(
        select(BrandVoice).where(BrandVoice.workspace_id == workspace_id)
    )
    bv = result.scalar_one_or_none()
    if not bv:
        bv = BrandVoice(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            training_sources=[],
            approval_history=[],
        )
        db.add(bv)
        await db.flush()
    return bv


@router.get("/{workspace_id}")
async def get_brand_voice(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get brand voice configuration for a workspace."""
    if not await _verify_workspace(workspace_id, current_user.id, db):
        raise HTTPException(status_code=404, detail="Workspace not found")

    bv = await _get_or_create_brand_voice(workspace_id, db)

    return {
        "id": bv.id,
        "workspace_id": bv.workspace_id,
        "tone": bv.tone or "",
        "writing_style": bv.writing_style or "",
        "cta_style": bv.cta_style or "",
        "emoji_usage": bv.emoji_usage or "",
        "formatting": bv.formatting or "",
        "vocabulary": bv.vocabulary or "",
        "technical_depth": getattr(bv, "technical_depth", "") or "",
        "sample_posts": bv.sample_posts or [],
        "training_sources": getattr(bv, "training_sources", []) or [],
        "approval_history": getattr(bv, "approval_history", []) or [],
        "created_at": bv.created_at.isoformat() if bv.created_at else None,
        "updated_at": bv.updated_at.isoformat() if bv.updated_at else None,
    }


@router.post("/{workspace_id}")
async def update_brand_voice(
    workspace_id: str,
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create or update brand voice configuration."""
    if not await _verify_workspace(workspace_id, current_user.id, db):
        raise HTTPException(status_code=404, detail="Workspace not found")

    bv = await _get_or_create_brand_voice(workspace_id, db)

    # Update fields
    updatable = [
        "tone", "writing_style", "cta_style", "emoji_usage",
        "formatting", "vocabulary", "sample_posts", "technical_depth",
    ]
    for field in updatable:
        if field in request and request[field] is not None:
            setattr(bv, field, request[field])

    await db.flush()

    return {
        "id": bv.id,
        "message": "Brand voice updated successfully",
    }


@router.post("/{workspace_id}/sources")
async def add_training_source(
    workspace_id: str,
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a training source (URL, PDF, website, posts, newsletter)."""
    if not await _verify_workspace(workspace_id, current_user.id, db):
        raise HTTPException(status_code=404, detail="Workspace not found")

    source_type = request.get("type", "")
    value = request.get("value", "")
    label = request.get("label", "")

    if not source_type or not value:
        raise HTTPException(status_code=400, detail="Type and value are required")

    valid_types = ["url", "pdf", "document", "website", "posts", "newsletter"]
    if source_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid source type. Must be one of: {', '.join(valid_types)}")

    bv = await _get_or_create_brand_voice(workspace_id, db)
    sources = list(getattr(bv, "training_sources", []) or [])

    new_source = {
        "id": str(uuid.uuid4()),
        "type": source_type,
        "value": value,
        "label": label or value[:50],
        "status": "pending",
    }
    sources.append(new_source)
    bv.training_sources = sources
    await db.flush()

    return new_source


@router.delete("/{workspace_id}/sources/{source_id}")
async def remove_training_source(
    workspace_id: str,
    source_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a training source."""
    if not await _verify_workspace(workspace_id, current_user.id, db):
        raise HTTPException(status_code=404, detail="Workspace not found")

    bv = await _get_or_create_brand_voice(workspace_id, db)
    sources = list(getattr(bv, "training_sources", []) or [])
    sources = [s for s in sources if s.get("id") != source_id]
    bv.training_sources = sources
    await db.flush()

    return {"message": "Source removed"}


@router.post("/{workspace_id}/analyze")
async def analyze_sources(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Analyze training sources and extract brand voice profile."""
    if not await _verify_workspace(workspace_id, current_user.id, db):
        raise HTTPException(status_code=404, detail="Workspace not found")

    bv = await _get_or_create_brand_voice(workspace_id, db)
    sources = getattr(bv, "training_sources", []) or []

    if not sources:
        raise HTTPException(status_code=400, detail="No training sources to analyze")

    # Build analysis prompt
    source_descriptions = []
    for s in sources:
        source_descriptions.append(f"- [{s.get('type', 'unknown')}] {s.get('label', s.get('value', ''))}")

    system_prompt = """Analyze brand voice sources and extract a detailed profile.
Return JSON with: tone, writing_style, cta_style, emoji_usage, formatting, vocabulary, technical_depth.
Be specific and descriptive for each field."""

    prompt = f"""Analyze these brand voice training sources and extract the brand profile:

Sources:
{chr(10).join(source_descriptions)}

Also consider any sample posts already provided.

Return a JSON object with keys: tone, writing_style, cta_style, emoji_usage, formatting, vocabulary, technical_depth"""

    ai_result = await _call_ai(prompt, system_prompt)

    if ai_result:
        try:
            cleaned = ai_result.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned.rsplit("```", 1)[0]
            parsed = json.loads(cleaned.strip())
            # Update brand voice with analysis
            for field in ["tone", "writing_style", "cta_style", "emoji_usage", "formatting", "vocabulary", "technical_depth"]:
                if field in parsed:
                    setattr(bv, field, parsed[field])
            # Mark sources as processed
            for s in sources:
                s["status"] = "completed"
            bv.training_sources = sources
            await db.flush()
            return {"message": "Analysis complete", "profile": parsed}
        except (json.JSONDecodeError, IndexError):
            pass

    # Placeholder analysis
    placeholder = {
        "tone": "Professional yet approachable",
        "writing_style": "Conversational with industry expertise",
        "cta_style": "Direct and action-oriented",
        "emoji_usage": "Minimal, strategic use of 1-2 emojis per post",
        "formatting": "Short paragraphs, bullet points, clear headers",
        "vocabulary": "Industry-standard terminology with accessible explanations",
        "technical_depth": "Medium — explains concepts without oversimplifying",
    }
    for field, value in placeholder.items():
        setattr(bv, field, value)
    for s in sources:
        s["status"] = "completed"
    bv.training_sources = sources
    await db.flush()

    return {"message": "Analysis complete (placeholder — add OPENAI_API_KEY for AI analysis)", "profile": placeholder}


@router.post("/{workspace_id}/train")
async def train_from_approvals(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Refine brand voice from approval/edit history."""
    if not await _verify_workspace(workspace_id, current_user.id, db):
        raise HTTPException(status_code=404, detail="Workspace not found")

    bv = await _get_or_create_brand_voice(workspace_id, db)
    history = getattr(bv, "approval_history", []) or []

    if len(history) < 3:
        return {
            "message": f"Need at least 3 approval entries to train. Currently have {len(history)}.",
            "current_profile": {
                "tone": bv.tone,
                "writing_style": bv.writing_style,
            },
        }

    # Analyze patterns in approvals
    system_prompt = """Analyze content approval patterns to refine brand voice.
Look at what was approved vs what was edited, and extract patterns.
Return JSON with updated brand voice fields."""

    approval_text = "\n---\n".join([
        f"Original: {a.get('original_content', '')[:200]}\nApproved: {a.get('approved_content', '')[:200]}\nEdits: {a.get('edits', 'none')}"
        for a in history[-10:]
    ])

    prompt = f"""Based on these content approvals and edits, refine the brand voice:

{approval_text}

Current brand voice:
- Tone: {bv.tone}
- Style: {bv.writing_style}
- CTA: {bv.cta_style}

Return JSON with refined: tone, writing_style, cta_style, emoji_usage, formatting, vocabulary"""

    ai_result = await _call_ai(prompt, system_prompt)

    if ai_result:
        try:
            cleaned = ai_result.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned.rsplit("```", 1)[0]
            parsed = json.loads(cleaned.strip())
            for field in ["tone", "writing_style", "cta_style", "emoji_usage", "formatting", "vocabulary"]:
                if field in parsed:
                    setattr(bv, field, parsed[field])
            await db.flush()
            return {"message": "Brand voice refined from approval history", "updated_profile": parsed}
        except (json.JSONDecodeError, IndexError):
            pass

    return {"message": "Training complete (placeholder — add OPENAI_API_KEY for AI training)"}
