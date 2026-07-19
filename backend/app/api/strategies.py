"""Strategy CRUD + Wizard API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from typing import Any
from datetime import datetime
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.workspace import ensure_system_workspace
from app.models.user import User
from app.models.strategy import ContentStrategy, StrategyAuditLog

router = APIRouter(prefix="/strategies", tags=["strategies"])


class GoalCreate(BaseModel):
    type: str = "engagement_rate"
    target: float = 0
    platform: str = "all"
    period: str = "monthly"
    baseline: float = 0

class PillarCreate(BaseModel):
    name: str
    description: str = ""
    weight: float = 0.33
    platforms: list[str] = []
    tone: str = "professional"
    example_hooks: list[str] = []
    content_types: list[str] = ["text_post"]

class PersonaCreate(BaseModel):
    name: str
    demographics: dict[str, Any] = {}
    pain_points: list[str] = []
    content_preferences: list[str] = []

class FrequencyConfig(BaseModel):
    posts_per_week: int = 3
    preferred_days: list[int] = [1, 2, 3, 4, 5]
    preferred_hours: list[int] = [9, 12, 17]

class StrategyCreate(BaseModel):
    name: str = Field(min_length=3, max_length=200)
    goals: list[GoalCreate] = []
    content_pillars: list[PillarCreate] = []
    audience_personas: list[PersonaCreate] = []
    posting_frequency: dict[str, FrequencyConfig] = {}
    brand_voice_overrides: dict[str, Any] = {}
    auto_generate: bool = True
    generate_ahead_days: int = 7
    approval_required: bool = True
    auto_approve_threshold: float = 0.85

class StrategyUpdate(BaseModel):
    name: str | None = None
    goals: list[GoalCreate] | None = None
    content_pillars: list[PillarCreate] | None = None
    audience_personas: list[PersonaCreate] | None = None
    posting_frequency: dict[str, FrequencyConfig] | None = None
    brand_voice_overrides: dict[str, Any] | None = None
    auto_generate: bool | None = None
    generate_ahead_days: int | None = None
    approval_required: bool | None = None
    auto_approve_threshold: float | None = None


def normalize_pillars(pillars: list[dict]) -> list[dict]:
    if not pillars:
        return pillars
    total = sum(p.get("weight", 0.33) for p in pillars)
    if total > 0:
        for p in pillars:
            p["weight"] = round(p.get("weight", 0.33) / total, 2)
    for p in pillars:
        if p["weight"] < 0.05:
            p["weight"] = 0.05
    return pillars

def compute_stats(strategy: ContentStrategy) -> dict:
    pillars = strategy.content_pillars or []
    freq = strategy.posting_frequency or {}
    total_per_week = sum(f.get("posts_per_week", 0) for f in freq.values())
    platforms = [p for p in freq.keys() if freq[p].get("posts_per_week", 0) > 0]
    return {
        "total_posts_per_week": total_per_week,
        "total_posts_per_month": total_per_week * 4,
        "platforms_active": platforms,
        "pillar_balance": {p["name"]: p["weight"] for p in pillars},
    }

async def log_audit(db, strategy_id, workspace_id, user_id, action, changes=None):
    entry = StrategyAuditLog(
        id=str(uuid.uuid4()), strategy_id=strategy_id,
        workspace_id=workspace_id, user_id=user_id,
        action=action, changes=changes, created_at=datetime.utcnow(),
    )
    db.add(entry)


@router.post("/")
async def create_strategy(body: StrategyCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    workspace_id = await ensure_system_workspace(db)
    pillars = normalize_pillars([p.model_dump() for p in body.content_pillars])
    strategy = ContentStrategy(
        id=str(uuid.uuid4()), workspace_id=workspace_id, name=body.name,
        goals=[g.model_dump() for g in body.goals], content_pillars=pillars,
        audience_personas=[a.model_dump() for a in body.audience_personas],
        posting_frequency={k: v.model_dump() for k, v in body.posting_frequency.items()},
        brand_voice_overrides=body.brand_voice_overrides, status="draft",
        auto_generate=body.auto_generate, generate_ahead_days=body.generate_ahead_days,
        approval_required=body.approval_required, auto_approve_threshold=body.auto_approve_threshold,
        created_by=current_user.id, created_at=datetime.utcnow(), updated_at=datetime.utcnow(),
    )
    db.add(strategy)
    await log_audit(db, strategy.id, workspace_id, current_user.id, "created")
    await db.flush()
    return {"id": strategy.id, "name": strategy.name, "status": strategy.status, "computed_stats": compute_stats(strategy), "created_at": strategy.created_at.isoformat()}


@router.get("/")
async def list_strategies(status: str | None = Query(None), page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    workspace_id = await ensure_system_workspace(db)
    query = select(ContentStrategy).where(ContentStrategy.workspace_id == workspace_id)
    if status:
        query = query.where(ContentStrategy.status == status)
    query = query.order_by(ContentStrategy.created_at.desc()).offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    return [{"id": s.id, "name": s.name, "status": s.status, "computed_stats": compute_stats(s), "created_at": s.created_at.isoformat(), "updated_at": s.updated_at.isoformat()} for s in result.scalars().all()]


@router.get("/defaults")
async def get_defaults(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    workspace_id = await ensure_system_workspace(db)
    from app.models.content import PlatformConnection
    result = await db.execute(select(PlatformConnection).where(PlatformConnection.workspace_id == workspace_id))
    connected = [c.platform for c in result.scalars().all()]
    return {"connected_platforms": connected, "analytics_baseline": {}, "brand_voice_status": "not_configured", "default_frequency": {"linkedin": {"posts_per_week": 3, "preferred_days": [1, 2, 3], "preferred_hours": [9, 12, 17]}, "x": {"posts_per_week": 5, "preferred_days": [0, 1, 2, 3, 4], "preferred_hours": [8, 12, 17, 20]}, "instagram": {"posts_per_week": 3, "preferred_days": [1, 3, 5], "preferred_hours": [11, 19]}, "facebook": {"posts_per_week": 3, "preferred_days": [1, 3, 5], "preferred_hours": [9, 13, 17]}, "youtube": {"posts_per_week": 1, "preferred_days": [4], "preferred_hours": [15]}}}


@router.get("/{strategy_id}")
async def get_strategy(strategy_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    workspace_id = await ensure_system_workspace(db)
    result = await db.execute(select(ContentStrategy).where(ContentStrategy.id == strategy_id, ContentStrategy.workspace_id == workspace_id))
    strategy = result.scalar_one_or_none()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return {"id": strategy.id, "workspace_id": strategy.workspace_id, "name": strategy.name, "goals": strategy.goals, "content_pillars": strategy.content_pillars, "audience_personas": strategy.audience_personas, "posting_frequency": strategy.posting_frequency, "brand_voice_overrides": strategy.brand_voice_overrides, "status": strategy.status, "auto_generate": strategy.auto_generate, "generate_ahead_days": strategy.generate_ahead_days, "approval_required": strategy.approval_required, "auto_approve_threshold": strategy.auto_approve_threshold, "last_generated_at": strategy.last_generated_at.isoformat() if strategy.last_generated_at else None, "computed_stats": compute_stats(strategy), "created_by": strategy.created_by, "created_at": strategy.created_at.isoformat(), "updated_at": strategy.updated_at.isoformat()}


@router.put("/{strategy_id}")
async def update_strategy(strategy_id: str, body: StrategyUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    workspace_id = await ensure_system_workspace(db)
    result = await db.execute(select(ContentStrategy).where(ContentStrategy.id == strategy_id, ContentStrategy.workspace_id == workspace_id))
    strategy = result.scalar_one_or_none()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    updates = body.model_dump(exclude_unset=True)
    changes = {}
    for key, value in updates.items():
        if key == "content_pillars" and value is not None:
            value = normalize_pillars([p.model_dump() if hasattr(p, "model_dump") else p for p in value])
        old = getattr(strategy, key, None)
        if old != value:
            changes[key] = {"old": str(old)[:100], "new": str(value)[:100]}
            setattr(strategy, key, value)
    strategy.updated_at = datetime.utcnow()
    if changes:
        await log_audit(db, strategy.id, workspace_id, current_user.id, "updated", changes)
    await db.flush()
    return {"id": strategy.id, "name": strategy.name, "status": strategy.status, "computed_stats": compute_stats(strategy), "updated_at": strategy.updated_at.isoformat()}


@router.delete("/{strategy_id}")
async def archive_strategy(strategy_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    workspace_id = await ensure_system_workspace(db)
    result = await db.execute(select(ContentStrategy).where(ContentStrategy.id == strategy_id, ContentStrategy.workspace_id == workspace_id))
    strategy = result.scalar_one_or_none()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    strategy.status = "archived"
    strategy.updated_at = datetime.utcnow()
    await log_audit(db, strategy.id, workspace_id, current_user.id, "archived")
    await db.flush()
    return {"message": "Archived", "id": strategy_id}


@router.post("/{strategy_id}/activate")
async def activate_strategy(strategy_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    workspace_id = await ensure_system_workspace(db)
    result = await db.execute(select(ContentStrategy).where(ContentStrategy.id == strategy_id, ContentStrategy.workspace_id == workspace_id))
    strategy = result.scalar_one_or_none()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    if not strategy.content_pillars:
        raise HTTPException(status_code=400, detail="At least 1 pillar required")
    if not strategy.goals:
        raise HTTPException(status_code=400, detail="At least 1 goal required")
    if not any(f.get("posts_per_week", 0) > 0 for f in strategy.posting_frequency.values()):
        raise HTTPException(status_code=400, detail="At least 1 platform with frequency > 0 required")
    strategy.status = "active"
    strategy.updated_at = datetime.utcnow()
    await log_audit(db, strategy.id, workspace_id, current_user.id, "activated")
    await db.flush()
    return {"id": strategy.id, "name": strategy.name, "status": strategy.status, "message": "Strategy activated. Content generation will start shortly."}


@router.post("/{strategy_id}/pause")
async def pause_strategy(strategy_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    workspace_id = await ensure_system_workspace(db)
    result = await db.execute(select(ContentStrategy).where(ContentStrategy.id == strategy_id, ContentStrategy.workspace_id == workspace_id))
    strategy = result.scalar_one_or_none()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    strategy.status = "paused"
    strategy.updated_at = datetime.utcnow()
    await log_audit(db, strategy.id, workspace_id, current_user.id, "paused")
    await db.flush()
    return {"id": strategy.id, "status": strategy.status}


@router.get("/{strategy_id}/audit-log")
async def get_audit_log(strategy_id: str, limit: int = Query(50, ge=1, le=200), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(StrategyAuditLog).where(StrategyAuditLog.strategy_id == strategy_id).order_by(StrategyAuditLog.created_at.desc()).limit(limit))
    return [{"id": e.id, "action": e.action, "changes": e.changes, "user_id": e.user_id, "created_at": e.created_at.isoformat()} for e in result.scalars().all()]


@router.get("/{strategy_id}/goal-tracking")
async def get_goal_tracking(strategy_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Compare strategy goals against actual analytics performance.

    For each goal in the strategy, queries AnalyticsMetric for actual performance,
    calculates progress %, trend direction, and returns a structured status.
    """
    from sqlalchemy import func
    from datetime import timedelta
    from app.models.content import Post, AnalyticsMetric

    workspace_id = await ensure_system_workspace(db)
    result = await db.execute(select(ContentStrategy).where(ContentStrategy.id == strategy_id, ContentStrategy.workspace_id == workspace_id))
    strategy = result.scalar_one_or_none()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    goals = strategy.goals or []
    goal_results = []

    for goal in goals:
        goal_type = goal.get("type", "engagement_rate")
        target = goal.get("target", 0)
        baseline = goal.get("baseline", 0)
        platform_filter = goal.get("platform", "all")
        period = goal.get("period", "monthly")  # weekly, monthly, quarterly

        # Determine lookback window based on goal period
        period_days = {"weekly": 7, "monthly": 30, "quarterly": 90, "yearly": 365}
        lookback = period_days.get(period, 30)
        cutoff = datetime.utcnow() - timedelta(days=lookback)

        # Map goal type to metric field
        metric_map = {
            "engagement_rate": func.avg(AnalyticsMetric.engagement),
            "impressions": func.sum(AnalyticsMetric.impressions),
            "reach": func.sum(AnalyticsMetric.reach),
            "likes": func.sum(AnalyticsMetric.likes),
            "comments": func.sum(AnalyticsMetric.comments),
            "shares": func.sum(AnalyticsMetric.shares),
            "clicks": func.sum(AnalyticsMetric.clicks),
        }
        metric_col = metric_map.get(goal_type, func.avg(AnalyticsMetric.engagement))

        # Build query
        query = select(metric_col).join(Post, Post.id == AnalyticsMetric.post_id).where(
            Post.workspace_id == workspace_id,
            AnalyticsMetric.recorded_at >= cutoff,
        )
        if platform_filter != "all":
            query = query.where(AnalyticsMetric.platform == platform_filter)
            # Also filter posts for that platform
            if platform_filter in ("linkedin", "x", "instagram", "facebook", "youtube"):
                query = query.where(Post.platform == platform_filter)

        metric_result = await db.execute(query)
        actual_raw = metric_result.scalar() or 0
        actual = round(actual_raw, 2) if isinstance(actual_raw, float) else actual_raw

        # Calculate progress percentage
        progress_pct = 0.0
        if target > 0:
            progress_pct = round(min(actual / target, 2.0) * 100, 1)  # Cap at 200%

        # Determine trend by comparing to previous period
        prev_cutoff = cutoff - timedelta(days=lookback)
        prev_query = select(metric_col).join(Post, Post.id == AnalyticsMetric.post_id).where(
            Post.workspace_id == workspace_id,
            AnalyticsMetric.recorded_at >= prev_cutoff,
            AnalyticsMetric.recorded_at < cutoff,
        )
        if platform_filter != "all":
            prev_query = prev_query.where(AnalyticsMetric.platform == platform_filter)
            if platform_filter in ("linkedin", "x", "instagram", "facebook", "youtube"):
                prev_query = prev_query.where(Post.platform == platform_filter)

        prev_result = await db.execute(prev_query)
        prev_actual = prev_result.scalar() or 0
        prev_actual = round(prev_actual, 2) if isinstance(prev_actual, float) else prev_actual

        if prev_actual > 0:
            trend_dir = "up" if actual > prev_actual else "down" if actual < prev_actual else "flat"
            trend_pct = round((actual - prev_actual) / prev_actual * 100, 1)
        else:
            trend_dir = "flat"
            trend_pct = 0.0

        # Achievement status
        if actual >= target:
            status = "achieved"
        elif progress_pct >= 75:
            status = "near_target"
        elif progress_pct >= 50:
            status = "on_track"
        elif progress_pct >= 25:
            status = "behind"
        else:
            status = "at_risk"

        goal_results.append({
            "goal_type": goal_type,
            "target": target,
            "baseline": baseline,
            "platform": platform_filter,
            "period": period,
            "actual": actual,
            "progress_pct": progress_pct,
            "trend": {"direction": trend_dir, "change_pct": trend_pct, "previous_value": prev_actual},
            "status": status,
            "lookback_days": lookback,
            "metric_label": goal_type.replace("_", " ").title(),
        })

    # Overall strategy health score
    achieved = sum(1 for g in goal_results if g["status"] == "achieved")
    total_goals = len(goal_results) or 1
    health_score = round(achieved / total_goals * 100, 1) if goal_results else 0

    return {
        "strategy_id": strategy_id,
        "strategy_name": strategy.name,
        "total_goals": len(goal_results),
        "achieved_goals": achieved,
        "health_score": health_score,
        "goals": goal_results,
        "computed_at": datetime.utcnow().isoformat(),
    }


@router.post("/quick-start")
async def quick_start(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    workspace_id = await ensure_system_workspace(db)
    from app.models.content import PlatformConnection
    result = await db.execute(select(PlatformConnection).where(PlatformConnection.workspace_id == workspace_id))
    connected = [c.platform for c in result.scalars().all()]
    pillars = [
        {"name": "Industry Insights", "description": "Trends, analysis, professional opinions", "weight": 0.4, "platforms": connected[:3], "tone": "authoritative", "example_hooks": ["Here's what most people get wrong about..."], "content_types": ["text_post"]},
        {"name": "Educational Tips", "description": "How-to guides, tutorials, best practices", "weight": 0.35, "platforms": connected[:3], "tone": "friendly", "example_hooks": ["3 things I wish I knew before..."], "content_types": ["text_post", "thread"]},
        {"name": "Behind the Scenes", "description": "Company culture, team stories, day-in-the-life", "weight": 0.25, "platforms": connected[:3], "tone": "casual", "example_hooks": ["What our mornings look like..."], "content_types": ["text_post"]},
    ]
    goals = [{"type": "engagement_rate", "target": 4.5, "platform": "all", "period": "quarterly", "baseline": 2.0}]
    frequency = {"linkedin": {"posts_per_week": 3, "preferred_days": [1, 2, 3], "preferred_hours": [9, 12, 17]}, "x": {"posts_per_week": 5, "preferred_days": [0, 1, 2, 3, 4], "preferred_hours": [8, 12, 17, 20]}}
    strategy = ContentStrategy(
        id=str(uuid.uuid4()), workspace_id=workspace_id, name="Quick Start Strategy",
        goals=goals, content_pillars=normalize_pillars(pillars),
        audience_personas=[{"name": "General Audience", "demographics": {}, "pain_points": [], "content_preferences": []}],
        posting_frequency=frequency, status="draft", auto_generate=True,
        generate_ahead_days=7, approval_required=True, auto_approve_threshold=0.85,
        created_by=current_user.id, created_at=datetime.utcnow(), updated_at=datetime.utcnow(),
    )
    db.add(strategy)
    await log_audit(db, strategy.id, workspace_id, current_user.id, "created")
    await db.flush()
    return {"id": strategy.id, "name": strategy.name, "status": strategy.status, "computed_stats": compute_stats(strategy), "created_at": strategy.created_at.isoformat()}
