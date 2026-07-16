"""Competitor Benchmarking — track competitors, compare performance."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/competitors", tags=["competitors"])


@router.get("")
async def list_competitors(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """List tracked competitors."""
    competitors = [
        {"id": "comp-1", "name": "Buffer", "platforms": ["linkedin", "x", "instagram"], "profile_urls": {"linkedin": "bufferapp", "x": "buffer"}, "tracking_enabled": True, "followers": 142000, "avg_engagement_rate": 2.8, "posts_per_week": 12, "top_content_type": "educational", "last_checked": (datetime.utcnow() - timedelta(hours=6)).isoformat()},
        {"id": "comp-2", "name": "Hootsuite", "platforms": ["linkedin", "x", "youtube"], "profile_urls": {"linkedin": "hootsuite", "x": "hootsuite"}, "tracking_enabled": True, "followers": 98000, "avg_engagement_rate": 2.1, "posts_per_week": 15, "top_content_type": "tutorials", "last_checked": (datetime.utcnow() - timedelta(hours=4)).isoformat()},
        {"id": "comp-3", "name": "Sprout Social", "platforms": ["linkedin", "instagram", "x"], "profile_urls": {"linkedin": "sproutsocial"}, "tracking_enabled": True, "followers": 67000, "avg_engagement_rate": 3.2, "posts_per_week": 8, "top_content_type": "case-studies", "last_checked": (datetime.utcnow() - timedelta(hours=12)).isoformat()},
    ]
    return {"competitors": competitors, "total": len(competitors)}


@router.post("")
async def add_competitor(request: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Add a competitor to track."""
    name = request.get("name", "")
    if not name:
        raise HTTPException(status_code=400, detail="Name is required")
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "platforms": request.get("platforms", ["x"]),
        "profile_urls": request.get("profile_urls", {}),
        "tracking_enabled": True,
        "followers": 0,
        "avg_engagement_rate": 0,
        "posts_per_week": 0,
        "top_content_type": "unknown",
        "last_checked": None,
    }


@router.delete("/{competitor_id}")
async def remove_competitor(competitor_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Remove a competitor."""
    return {"id": competitor_id, "message": "Competitor removed"}


@router.get("/compare")
async def compare_performance(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Compare own performance vs competitors."""
    return {
        "own": {"followers": 28400, "engagement_rate": 3.5, "posts_per_week": 10, "avg_reach": 4500},
        "competitors_avg": {"followers": 102333, "engagement_rate": 2.7, "posts_per_week": 11.7, "avg_reach": 3800},
        "verdict": "Your engagement rate (3.5%) exceeds the competitor average (2.7%). Focus on growing follower count through consistent posting.",
        "strengths": ["Higher engagement rate than competitors", "Consistent posting schedule"],
        "gaps": ["Lower follower count", "Fewer content types used"],
    }


@router.get("/{competitor_id}/metrics")
async def get_competitor_metrics(competitor_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get detailed metrics for a competitor."""
    now = datetime.utcnow()
    return {
        "competitor_id": competitor_id,
        "followers_growth": [{"date": (now - timedelta(days=i)).strftime("%m-%d"), "followers": 100000 + i * 200} for i in range(30, 0, -1)],
        "engagement_trend": [{"date": (now - timedelta(days=i)).strftime("%m-%d"), "rate": 2.5 + (i % 5) * 0.2} for i in range(30, 0, -1)],
        "top_posts": [
            {"title": "Top performing post", "platform": "linkedin", "engagement_rate": 5.2, "impressions": 45000},
            {"title": "Best tutorial content", "platform": "youtube", "engagement_rate": 4.8, "impressions": 32000},
        ],
    }
