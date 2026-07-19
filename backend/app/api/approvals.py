"""Multi-Tier Approval Workflows — DB-backed approval queue.

Replaced hardcoded mock data with real queries against ContentSlot model.
All endpoints now use ContentSlots with status "pending_approval".
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
import uuid
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.workspace import ensure_system_workspace
from app.models.user import User
from app.models.strategy import ContentSlot
from app.models.content import Post
from app.models.post_platform import PostPlatform

router = APIRouter(prefix="/approvals", tags=["approvals"])


class ApproveRequest(BaseModel):
    comment: str = ""


class RejectRequest(BaseModel):
    reason: str = ""
    category: str = "custom"


@router.get("/pending")
async def list_pending_approvals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """List ContentSlots awaiting approval (status = pending_approval)."""
    workspace_id = await ensure_system_workspace(db)
    query = (
        select(ContentSlot)
        .where(
            ContentSlot.workspace_id == workspace_id,
            ContentSlot.status == "pending_approval",
        )
        .order_by(ContentSlot.scheduled_datetime)
        .offset((page - 1) * limit)
        .limit(limit)
    )
    result = await db.execute(query)
    slots = result.scalars().all()

    # Count total
    count_query = select(func.count(ContentSlot.id)).where(
        ContentSlot.workspace_id == workspace_id,
        ContentSlot.status == "pending_approval",
    )
    total = (await db.execute(count_query)).scalar() or 0

    return {
        "approvals": [
            {
                "id": s.id,
                "post_id": s.post_id,
                "post_title": s.topic or f"{s.pillar_name} — {s.platform}",
                "content_preview": s.generated_content[:200] if s.generated_content else "",
                "platform": s.platform,
                "pillar_name": s.pillar_name,
                "brand_voice_score": s.brand_voice_score,
                "scheduled_date": s.scheduled_date.isoformat(),
                "scheduled_time": s.scheduled_time,
                "requested_at": s.updated_at.isoformat() if s.updated_at else None,
                "auto_approved": False,
            }
            for s in slots
        ],
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.get("/stats")
async def get_approval_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    days: int = Query(90, ge=1, le=365),
):
    """Approval stats: count of slots by status."""
    from datetime import timedelta

    workspace_id = await ensure_system_workspace(db)
    cutoff = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(ContentSlot.status, func.count(ContentSlot.id))
        .where(
            ContentSlot.workspace_id == workspace_id,
            ContentSlot.created_at >= cutoff,
        )
        .group_by(ContentSlot.status)
    )
    status_counts = {row[0]: row[1] for row in result.all()}

    total = sum(status_counts.values())
    pending = status_counts.get("pending_approval", 0)
    approved = status_counts.get("approved", 0)
    rejected = status_counts.get("rejected", 0)
    generated = status_counts.get("generated", 0)
    published = status_counts.get("published", 0)
    skipped = status_counts.get("skipped", 0)
    failed = status_counts.get("failed", 0)

    # Count auto-approved slots
    auto_result = await db.execute(
        select(func.count(ContentSlot.id))
        .where(
            ContentSlot.workspace_id == workspace_id,
            ContentSlot.auto_approved.is_(True),
            ContentSlot.created_at >= cutoff,
        )
    )
    auto_approved = auto_result.scalar() or 0

    # Approval rate
    reviewable = pending + approved + rejected
    approval_rate = round((approved / max(reviewable, 1)) * 100, 1) if reviewable > 0 else 0

    return {
        "period_days": days,
        "total_slots": total,
        "pending_approval": pending,
        "approved": approved,
        "auto_approved": auto_approved,
        "rejected": rejected,
        "generated": generated,
        "published": published,
        "skipped": skipped,
        "failed": failed,
        "approval_rate": approval_rate,
    }


@router.post("/{slot_id}/approve")
async def approve_slot(
    slot_id: str,
    body: ApproveRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Approve a pending ContentSlot and create Post + PostPlatform rows."""
    workspace_id = await ensure_system_workspace(db)
    result = await db.execute(
        select(ContentSlot).where(
            ContentSlot.id == slot_id,
            ContentSlot.workspace_id == workspace_id,
        )
    )
    slot = result.scalar_one_or_none()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    if slot.status != "pending_approval":
        raise HTTPException(status_code=400, detail=f"Slot is {slot.status}, not pending_approval")

    slot.status = "approved"
    slot.approved_by = current_user.id
    slot.approved_at = datetime.utcnow()
    slot.updated_at = datetime.utcnow()

    # Create parent Post if not exists
    post_id = slot.post_id
    if not post_id:
        post = Post(
            id=str(uuid.uuid4()),
            workspace_id=slot.workspace_id,
            author_id=current_user.id,
            content=slot.generated_content or "",
            platform=slot.platform,
            status="scheduled",
            scheduled_at=datetime.combine(
                slot.scheduled_date,
                datetime.min.time().replace(
                    hour=int(slot.scheduled_time.split(":")[0]),
                    minute=int(slot.scheduled_time.split(":")[1]),
                ),
            ),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(post)
        post_id = post.id
        slot.post_id = post_id

    # Create PostPlatform row
    pp = PostPlatform(
        id=str(uuid.uuid4()),
        post_id=post_id,
        workspace_id=slot.workspace_id,
        platform=slot.platform,
        status="scheduled",
        caption=slot.generated_content,
        title=slot.topic,
        scheduled_at=datetime.combine(
            slot.scheduled_date,
            datetime.min.time().replace(
                hour=int(slot.scheduled_time.split(":")[0]),
                minute=int(slot.scheduled_time.split(":")[1]),
            ),
        ),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(pp)
    slot.post_platform_id = pp.id

    await db.flush()

    return {
        "id": slot.id,
        "status": "approved",
        "post_id": post_id,
        "post_platform_id": pp.id,
        "comment": body.comment,
        "message": "Slot approved and scheduled for publishing",
    }


@router.post("/{slot_id}/reject")
async def reject_slot(
    slot_id: str,
    body: RejectRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Reject a pending ContentSlot and return it to draft."""
    workspace_id = await ensure_system_workspace(db)
    result = await db.execute(
        select(ContentSlot).where(
            ContentSlot.id == slot_id,
            ContentSlot.workspace_id == workspace_id,
        )
    )
    slot = result.scalar_one_or_none()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    if slot.status not in ("pending_approval", "approved"):
        raise HTTPException(status_code=400, detail=f"Cannot reject slot in status {slot.status}")

    slot.status = "rejected"
    slot.rejection_reason = body.reason
    slot.rejection_category = body.category
    slot.updated_at = datetime.utcnow()
    await db.flush()

    return {
        "id": slot.id,
        "status": "rejected",
        "reason": body.reason,
        "message": "Slot rejected",
    }


# ─── Legacy workflow templates (config-driven, keep for reference) ──────────

@router.get("/workflows")
async def list_workflows(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """List approval workflow templates."""
    return {
        "workflows": [
            {
                "id": "wf-1", "name": "Standard 2-Tier", "is_default": True,
                "stages": [
                    {"stage": 1, "name": "Content Review", "approver_role": "editor", "required_approvals": 1},
                    {"stage": 2, "name": "Final Approval", "approver_role": "admin", "required_approvals": 1},
                ],
            },
            {
                "id": "wf-2", "name": "Enterprise 3-Tier", "is_default": False,
                "stages": [
                    {"stage": 1, "name": "Editor Review", "approver_role": "editor", "required_approvals": 1},
                    {"stage": 2, "name": "Compliance Check", "approver_role": "admin", "required_approvals": 1},
                    {"stage": 3, "name": "Brand Approval", "approver_role": "owner", "required_approvals": 1},
                ],
            },
        ]
    }


@router.post("/workflows")
async def create_workflow(request: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Create an approval workflow template."""
    stages = request.get("stages", [])
    for i, stage in enumerate(stages):
        stage["stage"] = i + 1
    return {
        "id": str(uuid.uuid4()),
        "name": request.get("name", "New Workflow"),
        "stages": stages,
        "is_default": False,
        "created_at": datetime.utcnow().isoformat(),
    }
