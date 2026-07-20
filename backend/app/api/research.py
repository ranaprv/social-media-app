"""Research API — 10 endpoints for Video SEO research with DB persistence.

Endpoints:
  POST /research/keywords        — Keyword research with Video SEO scoring
  POST /research/competitors     — Competitor analysis with gap detection
  POST /research/trends          — Trend analysis with direction tracking
  POST /research/thumbnails      — Thumbnail & title CTR testing
  POST /research/audience        — Audience analytics & demographics
  GET  /research/saved           — List saved research items (paginated)
  DELETE /research/saved/{id}    — Delete a saved research item
  GET  /research/by-pillar/{name} — Items linked to a content pillar (Strategy engine)
  GET  /research/rising           — Rising trends for scheduling (Scheduling engine)
  GET  /research/top-scoring      — Top items for content slots (Repurpose engine)
"""
import hashlib
import json
import time
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.research import ResearchItemResponse, ResearchItemList
from app.services.research_service import ResearchService

router = APIRouter(prefix="/research", tags=["research"])

# Simple in-memory TTL cache (5 minutes) to reduce duplicate LLM calls
_CACHE_TTL = 300
_cache: dict[str, tuple[float, dict]] = {}


def _cache_key(*args) -> str:
    return hashlib.md5(json.dumps(args, default=str).encode()).hexdigest()


def _get_cached(key: str):
    if key in _cache:
        ts, data = _cache[key]
        if time.time() - ts < _CACHE_TTL:
            return data
        del _cache[key]
    return None


def _set_cache(key: str, data: dict):
    _cache[key] = (time.time(), data)
    # Evict stale entries
    if len(_cache) > 100:
        stale = [k for k, (ts, _) in _cache.items() if time.time() - ts > _CACHE_TTL]
        for k in stale:
            del _cache[k]


def _service(db: AsyncSession, user: User) -> ResearchService:
    return ResearchService(db, user)


# ── 1. Keyword Research ───────────────────────────────────────────────────

@router.post("/keywords")
async def research_keywords(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Research keywords with Video SEO scoring and persistence."""
    topic = request.get("topic", "")
    platform = request.get("platform", "all")
    niche = request.get("niche", "")
    provider = request.get("provider", "openai")
    model = request.get("model")

    if not topic and not niche:
        raise HTTPException(status_code=400, detail="Topic or niche is required")

    # Check cache
    cache_key = _cache_key("keywords", topic, platform, niche, provider)
    cached = _get_cached(cache_key)
    if cached:
        return cached

    svc = _service(db, current_user)
    try:
        result = await svc.keyword_research(topic, platform, niche, provider, model)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Keyword research failed: {str(e)}")

    _set_cache(cache_key, result)
    return result


# ── 2. Competitor Analysis ────────────────────────────────────────────────

@router.post("/competitors")
async def analyze_competitors(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Analyze competitor content strategy with gap detection."""
    competitors = request.get("competitors", [])
    niche = request.get("niche", "")
    provider = request.get("provider", "openai")
    model = request.get("model")

    if not competitors and not niche:
        raise HTTPException(status_code=400, detail="Provide competitors list or niche")

    # Check cache
    cache_key = _cache_key("competitors", competitors, niche, provider)
    cached = _get_cached(cache_key)
    if cached:
        return cached

    svc = _service(db, current_user)
    try:
        result = await svc.competitor_analysis(competitors, niche, provider, model)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Competitor analysis failed: {str(e)}")

    _set_cache(cache_key, result)
    return result


# ── 3. Trend Analysis ─────────────────────────────────────────────────────

@router.post("/trends")
async def search_trends(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Search trends with direction tracking (rising/stable/declining)."""
    topic = request.get("topic", "")
    platform = request.get("platform", "all")
    provider = request.get("provider", "openai")
    model = request.get("model")

    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required")

    # Check cache
    cache_key = _cache_key("trends", topic, platform, provider)
    cached = _get_cached(cache_key)
    if cached:
        return cached

    svc = _service(db, current_user)
    try:
        result = await svc.trend_analysis(topic, platform, provider, model)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend analysis failed: {str(e)}")

    _set_cache(cache_key, result)
    return result


# ── 4. Thumbnail & Title Testing ──────────────────────────────────────────

@router.post("/thumbnails")
async def test_thumbnails(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate and score thumbnail/title variants by predicted CTR."""
    topic = request.get("topic", "")
    platform = request.get("platform", "youtube")
    provider = request.get("provider", "openai")
    model = request.get("model")
    variant_count = request.get("variant_count", 4)

    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required")

    # Check cache
    cache_key = _cache_key("thumbnails", topic, platform, provider, variant_count)
    cached = _get_cached(cache_key)
    if cached:
        return cached

    svc = _service(db, current_user)
    try:
        result = await svc.thumbnail_testing(topic, platform, provider, model, variant_count)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Thumbnail testing failed: {str(e)}")

    _set_cache(cache_key, result)
    return result


# ── 5. Audience Analytics ─────────────────────────────────────────────────

@router.post("/audience")
async def audience_analytics(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Analyze audience demographics, peak engagement, and content preferences."""
    platform = request.get("platform", "youtube")
    niche = request.get("niche", "")
    provider = request.get("provider", "openai")
    model = request.get("model")

    if not niche:
        raise HTTPException(status_code=400, detail="Niche is required")

    # Check cache
    cache_key = _cache_key("audience", platform, niche, provider)
    cached = _get_cached(cache_key)
    if cached:
        return cached

    svc = _service(db, current_user)
    try:
        result = await svc.audience_analytics(platform, niche, provider, model)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audience analytics failed: {str(e)}")

    _set_cache(cache_key, result)
    return result


# ── 6. List Saved Items ───────────────────────────────────────────────────

@router.get("/saved", response_model=ResearchItemList)
async def get_saved_research(
    category: Optional[str] = Query(None, description="Filter by category"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    pillar: Optional[str] = Query(None, description="Filter by content pillar"),
    limit: int = Query(20, ge=1, le=100, description="Page size"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List saved research items with optional filters."""
    svc = _service(db, current_user)
    try:
        result = await svc.get_saved(category, platform, pillar, limit, offset)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch saved items: {str(e)}")


# ── 7. Delete Saved Item ──────────────────────────────────────────────────

@router.delete("/saved/{item_id}")
async def delete_research_item(
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a saved research item by ID."""
    svc = _service(db, current_user)
    deleted = await svc.delete_item(item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")

    return {"deleted": True, "id": item_id}


# ── 8. Get by Pillar (Strategy Engine) ───────────────────────────────────

@router.get("/by-pillar/{pillar_name}")
async def get_by_pillar(
    pillar_name: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get research items linked to a content pillar. Used by Strategy engine."""
    svc = _service(db, current_user)
    try:
        items = await svc.get_by_pillar(pillar_name)
        return {"items": [{"id": str(i.id), "topic": i.topic, "category": i.category, "platform": i.platform, "video_seo_score": i.video_seo_score, "content_pillar": i.content_pillar, "data": i.data} for i in items], "count": len(items)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}")


# ── 9. Get Rising Trends (Scheduling Engine) ─────────────────────────────

@router.get("/rising")
async def get_rising(
    platform: str = Query("all", description="Platform filter"),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get rising trends for scheduling. Used by Scheduling engine."""
    svc = _service(db, current_user)
    try:
        items = await svc.get_rising(platform, limit)
        return {"items": [{"id": str(i.id), "topic": i.topic, "category": i.category, "platform": i.platform, "trend_direction": i.trend_direction, "trend_velocity": i.trend_velocity, "video_seo_score": i.video_seo_score, "data": i.data} for i in items], "count": len(items)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}")


# ── 10. Get Top Scoring (Content Slot Generation) ───────────────────────

@router.get("/top-scoring")
async def get_top_scoring(
    limit: int = Query(10, ge=1, le=50),
    category: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get top-scoring research items. Used for content slot generation."""
    svc = _service(db, current_user)
    try:
        items = await svc.get_top_scoring(limit, category)
        return {"items": [{"id": str(i.id), "topic": i.topic, "category": i.category, "platform": i.platform, "video_seo_score": i.video_seo_score, "content_pillar": i.content_pillar, "data": i.data} for i in items], "count": len(items)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}")
