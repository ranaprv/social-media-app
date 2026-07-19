"""Content Generation, Scheduling, and Approval API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, Field
from typing import Any
from datetime import datetime, date, timedelta
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.workspace import ensure_system_workspace
from app.models.user import User
from app.models.strategy import ContentStrategy, ContentPlan, ContentSlot

router = APIRouter(tags=["content-generation"])


class SlotUpdate(BaseModel):
    generated_content: str | None = None
    topic: str | None = None

class SlotApprove(BaseModel):
    comment: str = ""

class SlotReject(BaseModel):
    reason: str = ""
    category: str = "custom"

class BulkApprove(BaseModel):
    slot_ids: list[str]
    comment: str = ""

class BulkReject(BaseModel):
    slot_ids: list[str]
    reason: str = ""
    category: str = "custom"

class GenerateRequest(BaseModel):
    days_ahead: int = 7
    platforms: list[str] | None = None


# ─── Content Plans ──────────────────────────────────────────────────────────

@router.get("/strategies/{strategy_id}/plans")
async def list_plans(strategy_id: str, status: str | None = Query(None), page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    workspace_id = await ensure_system_workspace(db)
    query = select(ContentPlan).where(ContentPlan.strategy_id == strategy_id, ContentPlan.workspace_id == workspace_id)
    if status:
        query = query.where(ContentPlan.status == status)
    query = query.order_by(ContentPlan.week_start.desc()).offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    plans = result.scalars().all()
    return [{"id": p.id, "week_start": p.week_start.isoformat(), "status": p.status, "slot_count": p.slot_count, "approved_count": p.approved_count, "published_count": p.published_count, "rejected_count": p.rejected_count, "created_at": p.created_at.isoformat()} for p in plans]


@router.get("/strategies/{strategy_id}/plans/{plan_id}")
async def get_plan(strategy_id: str, plan_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    workspace_id = await ensure_system_workspace(db)
    result = await db.execute(select(ContentPlan).where(ContentPlan.id == plan_id, ContentPlan.workspace_id == workspace_id))
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    slots_result = await db.execute(select(ContentSlot).where(ContentSlot.plan_id == plan_id).order_by(ContentSlot.scheduled_datetime))
    slots = slots_result.scalars().all()
    return {
        "id": plan.id, "strategy_id": plan.strategy_id, "week_start": plan.week_start.isoformat(),
        "status": plan.status, "slot_count": plan.slot_count, "approved_count": plan.approved_count,
        "published_count": plan.published_count, "rejected_count": plan.rejected_count,
        "generated_at": plan.generated_at.isoformat() if plan.generated_at else None,
        "slots": [{"id": s.id, "pillar_name": s.pillar_name, "platform": s.platform, "scheduled_date": s.scheduled_date.isoformat(), "scheduled_time": s.scheduled_time, "status": s.status, "topic": s.topic, "generated_content": s.generated_content, "brand_voice_score": s.brand_voice_score, "auto_approved": s.auto_approved} for s in slots],
    }


@router.get("/strategies/{strategy_id}/plans/{plan_id}/progress")
async def get_plan_progress(strategy_id: str, plan_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    workspace_id = await ensure_system_workspace(db)
    result = await db.execute(select(ContentPlan).where(ContentPlan.id == plan_id, ContentPlan.workspace_id == workspace_id))
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"status": plan.status, "progress": plan.generation_progress, "slot_count": plan.slot_count, "approved_count": plan.approved_count}


# ─── Content Generation ────────────────────────────────────────────────────

@router.post("/strategies/{strategy_id}/generate")
async def generate_content(strategy_id: str, body: GenerateRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    workspace_id = await ensure_system_workspace(db)
    result = await db.execute(select(ContentStrategy).where(ContentStrategy.id == strategy_id, ContentStrategy.workspace_id == workspace_id))
    strategy = result.scalar_one_or_none()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    today = date.today()
    week_start = today + timedelta(days=(7 - today.weekday()))
    plan = ContentPlan(
        id=str(uuid.uuid4()), strategy_id=strategy_id, workspace_id=workspace_id,
        week_start=datetime.combine(week_start, datetime.min.time()),
        status="generating", generation_progress={"total_slots": 0, "completed": 0, "current_step": "planning"},
        created_at=datetime.utcnow(), updated_at=datetime.utcnow(),
    )
    db.add(plan)

    pillars = strategy.content_pillars or []
    freq = strategy.posting_frequency or {}
    platforms = body.platforms or [p for p, f in freq.items() if f.get("posts_per_week", 0) > 0]
    slots = []
    pillar_idx = 0

    # Fetch data-driven best times per platform using analytics
    from app.services.best_time_recommender import get_best_times_for_workspace
    best_times_data = await get_best_times_for_workspace(db, workspace_id)
    platform_best_times = best_times_data.get("platforms", {})

    for platform in platforms:
        platform_freq = freq.get(platform, {})
        posts_per_week = platform_freq.get("posts_per_week", 3)
        preferred_days = platform_freq.get("preferred_days", [1, 2, 3])
        preferred_hours = platform_freq.get("preferred_hours", [9, 12, 17])

        # Override preferred_hours with data-driven optimal times if analytics available
        platform_best = platform_best_times.get(platform)
        if platform_best:
            data_hours = sorted(set(s["hour"] for s in platform_best if s.get("score", 0) > 0.5))
            if data_hours:
                preferred_hours = data_hours[:5]  # Top 5 best hours from analytics
                # Also override preferred_days with top-performing days
                data_days = sorted(set(s["day"] for s in platform_best if s.get("score", 0) > 0.5))
                if data_days:
                    preferred_days = data_days[:5]

        for day_offset in range(body.days_ahead):
            current_date = today + timedelta(days=day_offset)
            if current_date.weekday() not in preferred_days:
                continue
            posts_today = min(2, max(1, posts_per_week // max(1, len(preferred_days))))
            for hour_idx in range(posts_today):
                hour = preferred_hours[hour_idx % len(preferred_hours)]
                pillar = pillars[pillar_idx % len(pillars)] if pillars else {"name": "General", "tone": "professional"}
                pillar_idx += 1
                slot = ContentSlot(
                    id=str(uuid.uuid4()), plan_id=plan.id, workspace_id=workspace_id,
                    strategy_id=strategy_id, pillar_name=pillar.get("name", "General"),
                    platform=platform, scheduled_date=current_date,
                    scheduled_time=f"{hour:02d}:00",
                    scheduled_datetime=datetime.combine(current_date, datetime.min.time().replace(hour=hour)),
                    status="empty", created_at=datetime.utcnow(), updated_at=datetime.utcnow(),
                )
                db.add(slot)
                slots.append(slot)

    plan.slot_count = len(slots)
    plan.generation_progress = {"total_slots": len(slots), "completed": 0, "current_step": "planning"}
    strategy.last_generated_at = datetime.utcnow()

    await db.flush()

    # Dispatch Celery task for async generation
    from app.tasks.content_generation import generate_content_for_plan
    task = generate_content_for_plan.delay(plan.id, workspace_id)

    # Store task ID on plan
    plan.generation_task_id = task.id
    await db.commit()

    return {"plan_id": plan.id, "task_id": task.id, "status": "generating", "slot_count": len(slots), "message": f"Generation started for {len(slots)} slots. Use /plans/{plan.id}/progress to track."}


# ─── Slot Management ───────────────────────────────────────────────────────

@router.get("/slots/{slot_id}")
async def get_slot(slot_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ContentSlot).where(ContentSlot.id == slot_id))
    slot = result.scalar_one_or_none()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    return {"id": slot.id, "plan_id": slot.plan_id, "pillar_name": slot.pillar_name, "platform": slot.platform, "scheduled_date": slot.scheduled_date.isoformat(), "scheduled_time": slot.scheduled_time, "status": slot.status, "topic": slot.topic, "generated_content": slot.generated_content, "generated_variants": slot.generated_variants, "brand_voice_score": slot.brand_voice_score, "platform_metadata": slot.platform_metadata, "post_id": slot.post_id, "approved_by": slot.approved_by, "approved_at": slot.approved_at.isoformat() if slot.approved_at else None, "rejection_reason": slot.rejection_reason, "rejection_category": slot.rejection_category, "auto_approved": slot.auto_approved, "user_edit_history": slot.user_edit_history}


@router.put("/slots/{slot_id}")
async def update_slot(slot_id: str, body: SlotUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ContentSlot).where(ContentSlot.id == slot_id))
    slot = result.scalar_one_or_none()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    if body.generated_content is not None:
        slot.user_edit_history = slot.user_edit_history or []
        slot.user_edit_history.append({"before": slot.generated_content, "after": body.generated_content, "edited_by": current_user.id, "timestamp": datetime.utcnow().isoformat()})
        slot.generated_content = body.generated_content
    if body.topic is not None:
        slot.topic = body.topic
    slot.updated_at = datetime.utcnow()
    await db.flush()
    return {"id": slot.id, "status": slot.status, "generated_content": slot.generated_content}


@router.post("/slots/{slot_id}/approve")
async def approve_slot(slot_id: str, body: SlotApprove, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ContentSlot).where(ContentSlot.id == slot_id))
    slot = result.scalar_one_or_none()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    
    slot.status = "approved"
    slot.approved_by = current_user.id
    slot.approved_at = datetime.utcnow()
    slot.updated_at = datetime.utcnow()
    
    # Create PostPlatform row for the scheduler to pick up
    from app.models.post_platform import PostPlatform
    from app.models.content import Post
    
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
            scheduled_at=datetime.combine(slot.scheduled_date, datetime.min.time().replace(hour=int(slot.scheduled_time.split(":")[0]), minute=int(slot.scheduled_time.split(":")[1]))),
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
        scheduled_at=datetime.combine(slot.scheduled_date, datetime.min.time().replace(hour=int(slot.scheduled_time.split(":")[0]), minute=int(slot.scheduled_time.split(":")[1]))),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(pp)
    slot.post_platform_id = pp.id
    
    await db.flush()
    return {"id": slot.id, "status": "approved", "post_platform_id": pp.id, "message": "Slot approved and scheduled for publishing"}


@router.post("/slots/{slot_id}/reject")
async def reject_slot(slot_id: str, body: SlotReject, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ContentSlot).where(ContentSlot.id == slot_id))
    slot = result.scalar_one_or_none()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    slot.status = "rejected"
    slot.rejection_reason = body.reason
    slot.rejection_category = body.category
    slot.updated_at = datetime.utcnow()
    await db.flush()
    return {"id": slot.id, "status": "rejected"}


@router.post("/slots/{slot_id}/skip")
async def skip_slot(slot_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ContentSlot).where(ContentSlot.id == slot_id))
    slot = result.scalar_one_or_none()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    slot.status = "skipped"
    slot.updated_at = datetime.utcnow()
    await db.flush()
    return {"id": slot.id, "status": "skipped"}


# ─── Bulk Operations ───────────────────────────────────────────────────────

@router.post("/slots/bulk-approve")
async def bulk_approve(body: BulkApprove, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    approved = 0
    for slot_id in body.slot_ids:
        result = await db.execute(select(ContentSlot).where(ContentSlot.id == slot_id))
        slot = result.scalar_one_or_none()
        if slot:
            slot.status = "approved"
            slot.approved_by = current_user.id
            slot.approved_at = datetime.utcnow()
            slot.updated_at = datetime.utcnow()
            approved += 1
    await db.flush()
    return {"approved": approved, "failed": len(body.slot_ids) - approved}


@router.post("/slots/bulk-reject")
async def bulk_reject(body: BulkReject, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    rejected = 0
    for slot_id in body.slot_ids:
        result = await db.execute(select(ContentSlot).where(ContentSlot.id == slot_id))
        slot = result.scalar_one_or_none()
        if slot:
            slot.status = "rejected"
            slot.rejection_reason = body.reason
            slot.rejection_category = body.category
            slot.updated_at = datetime.utcnow()
            rejected += 1
    await db.flush()
    return {"rejected": rejected}


# ─── Adherence Dashboard ──────────────────────────────────────────────────

@router.get("/strategies/{strategy_id}/adherence")
async def get_adherence(strategy_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    workspace_id = await ensure_system_workspace(db)
    result = await db.execute(select(ContentStrategy).where(ContentStrategy.id == strategy_id, ContentStrategy.workspace_id == workspace_id))
    strategy = result.scalar_one_or_none()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    plans_result = await db.execute(select(ContentPlan).where(ContentPlan.strategy_id == strategy_id))
    plans = plans_result.scalars().all()
    total_plans = len(plans)
    completed_plans = sum(1 for p in plans if p.status == "completed")

    slots_result = await db.execute(select(ContentSlot).where(ContentSlot.strategy_id == strategy_id))
    slots = slots_result.scalars().all()
    total_slots = len(slots)
    published = sum(1 for s in slots if s.status == "published")
    approved = sum(1 for s in slots if s.status == "approved")
    rejected = sum(1 for s in slots if s.status == "rejected")

    pillar_counts = {}
    platform_counts = {}
    for s in slots:
        pillar_counts[s.pillar_name] = pillar_counts.get(s.pillar_name, 0) + 1
        platform_counts[s.platform] = platform_counts.get(s.platform, 0) + 1

    adherence_score = 0
    if total_slots > 0:
        published_ratio = published / total_slots
        pillars = strategy.content_pillars or []
        pillar_balance_score = 1.0
        if pillars and pillar_counts:
            for p in pillars:
                expected = p.get("weight", 0.33)
                actual = pillar_counts.get(p["name"], 0) / total_slots
                pillar_balance_score -= abs(expected - actual) * 0.5
        adherence_score = min(100, max(0, int((published_ratio * 60 + pillar_balance_score * 40) * 100)))

    return {
        "adherence_score": adherence_score, "total_plans": total_plans, "completed_plans": completed_plans,
        "total_slots": total_slots, "published": published, "approved": approved, "rejected": rejected,
        "pillar_distribution": pillar_counts, "platform_distribution": platform_counts,
        "recommendations": _generate_recommendations(strategy, pillar_counts, platform_counts, total_slots),
    }


def _generate_recommendations(strategy, pillar_counts, platform_counts, total_slots):
    recs = []
    pillars = strategy.content_pillars or []
    for p in pillars:
        expected = p.get("weight", 0.33)
        actual = pillar_counts.get(p["name"], 0) / max(1, total_slots)
        if actual < expected * 0.7:
            recs.append(f"Under-represent pillar '{p['name']}' — {actual:.0%} vs target {expected:.0%}")
    freq = strategy.posting_frequency or {}
    for platform, config in freq.items():
        if platform_counts.get(platform, 0) == 0 and config.get("posts_per_week", 0) > 0:
            recs.append(f"No content generated for {platform} — check scheduling config")
    if total_slots == 0:
        recs.append("No content slots yet — activate strategy and run generation")
    return recs
