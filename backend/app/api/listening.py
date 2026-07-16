"""Social Listening API — alerts, mentions, trend discovery."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.llm import call_llm_json

router = APIRouter(prefix="/listening", tags=["listening"])


@router.get("/alerts")
async def list_alerts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all listening alerts for the workspace."""
    # Demo data — in production, query from listening_alerts table
    now = datetime.utcnow()
    alerts = [
        {"id": "alert-1", "keyword": "content marketing", "platforms": ["linkedin", "x"], "check_interval": "hourly", "last_checked": (now - timedelta(minutes=30)).isoformat(), "is_active": True, "mentions_count": 47, "sentiment_avg": 0.72},
        {"id": "alert-2", "keyword": "social media strategy", "platforms": ["instagram", "facebook"], "check_interval": "daily", "last_checked": (now - timedelta(hours=6)).isoformat(), "is_active": True, "mentions_count": 23, "sentiment_avg": 0.65},
        {"id": "alert-3", "keyword": "AI content tools", "platforms": ["linkedin", "x", "youtube"], "check_interval": "hourly", "last_checked": (now - timedelta(minutes=15)).isoformat(), "is_active": False, "mentions_count": 89, "sentiment_avg": 0.81},
    ]
    return {"alerts": alerts, "total": len(alerts)}


@router.post("/alerts")
async def create_alert(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new listening alert."""
    keyword = request.get("keyword", "")
    platforms = request.get("platforms", ["x"])
    check_interval = request.get("check_interval", "hourly")

    if not keyword:
        raise HTTPException(status_code=400, detail="Keyword is required")

    return {
        "id": str(uuid.uuid4()),
        "keyword": keyword,
        "platforms": platforms,
        "check_interval": check_interval,
        "last_checked": None,
        "is_active": True,
        "mentions_count": 0,
        "sentiment_avg": 0,
        "created_at": datetime.utcnow().isoformat(),
    }


@router.delete("/alerts/{alert_id}")
async def delete_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a listening alert."""
    return {"id": alert_id, "message": "Alert deleted"}


@router.put("/alerts/{alert_id}/toggle")
async def toggle_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Toggle alert active status."""
    return {"id": alert_id, "is_active": True, "message": "Alert toggled"}


@router.get("/mentions")
async def list_mentions(
    keyword: str = None,
    platform: str = None,
    sentiment: str = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List mentions from listening alerts."""
    now = datetime.utcnow()
    mentions = [
        {"id": "m-1", "keyword": "content marketing", "platform": "x", "author": "@marketingpro", "content": "Just discovered an amazing content marketing framework. Game changer for our strategy!", "sentiment": "positive", "sentiment_score": 0.89, "url": "https://x.com/marketingpro/status/123", "found_at": (now - timedelta(hours=1)).isoformat(), "engagement": 45},
        {"id": "m-2", "keyword": "content marketing", "platform": "linkedin", "author": "Sarah Johnson", "content": "Content marketing is evolving fast. AI tools are changing the game for small teams.", "sentiment": "positive", "sentiment_score": 0.75, "url": "https://linkedin.com/posts/123", "found_at": (now - timedelta(hours=3)).isoformat(), "engagement": 128},
        {"id": "m-3", "keyword": "social media strategy", "platform": "instagram", "author": "@digitalnomad", "content": "Honestly struggling with my social media strategy. Anyone else feel overwhelmed?", "sentiment": "negative", "sentiment_score": 0.25, "url": "https://instagram.com/p/123", "found_at": (now - timedelta(hours=5)).isoformat(), "engagement": 23},
        {"id": "m-4", "keyword": "AI content tools", "platform": "x", "author": "@techreview", "content": "New AI content tools are impressive but I worry about authenticity in brand voice.", "sentiment": "neutral", "sentiment_score": 0.52, "url": "https://x.com/techreview/status/456", "found_at": (now - timedelta(hours=8)).isoformat(), "engagement": 67},
        {"id": "m-5", "keyword": "content marketing", "platform": "youtube", "author": "Content Academy", "content": "Complete guide to content marketing in 2026. Timestamps in description.", "sentiment": "positive", "sentiment_score": 0.82, "url": "https://youtube.com/watch?v=123", "found_at": (now - timedelta(hours=12)).isoformat(), "engagement": 342},
        {"id": "m-6", "keyword": "social media strategy", "platform": "facebook", "author": "Marketing Today", "content": "5 social media strategy mistakes that are killing your reach in 2026.", "sentiment": "negative", "sentiment_score": 0.35, "url": "https://facebook.com/posts/789", "found_at": (now - timedelta(hours=15)).isoformat(), "engagement": 89},
    ]

    # Apply filters
    if keyword:
        mentions = [m for m in mentions if keyword.lower() in m["keyword"].lower()]
    if platform:
        mentions = [m for m in mentions if m["platform"] == platform]
    if sentiment:
        mentions = [m for m in mentions if m["sentiment"] == sentiment]

    total = len(mentions)
    mentions = mentions[offset:offset + limit]

    return {
        "mentions": mentions,
        "total": total,
        "offset": offset,
        "limit": limit,
    }


@router.get("/trends")
async def get_trends(
    period: str = "7d",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get trend summary — mentions over time, sentiment distribution, keyword cloud."""
    now = datetime.utcnow()

    # Mentions over time (daily)
    daily = []
    for i in range(7):
        day = now - timedelta(days=6 - i)
        daily.append({
            "date": day.strftime("%m-%d"),
            "mentions": 15 + i * 5 + (i % 3) * 3,
            "positive": 8 + i * 3,
            "neutral": 4 + i,
            "negative": 3 + (i % 2),
        })

    # Sentiment distribution
    sentiment_dist = {"positive": 42, "neutral": 28, "negative": 15}

    # Keyword cloud
    keyword_cloud = [
        {"keyword": "content marketing", "count": 47, "sentiment": 0.72},
        {"keyword": "social media strategy", "count": 34, "sentiment": 0.58},
        {"keyword": "AI content tools", "count": 28, "sentiment": 0.81},
        {"keyword": "brand voice", "count": 21, "sentiment": 0.65},
        {"keyword": "engagement rate", "count": 18, "sentiment": 0.45},
        {"keyword": "content calendar", "count": 15, "sentiment": 0.70},
        {"keyword": "hashtag strategy", "count": 12, "sentiment": 0.60},
        {"keyword": "video content", "count": 19, "sentiment": 0.75},
        {"keyword": "influencer marketing", "count": 11, "sentiment": 0.55},
        {"keyword": "analytics dashboard", "count": 9, "sentiment": 0.68},
    ]

    # Trending up/down
    trending_up = [
        {"keyword": "AI content tools", "change": +45, "period": "7d"},
        {"keyword": "video content", "change": +28, "period": "7d"},
        {"keyword": "brand voice", "change": +15, "period": "7d"},
    ]
    trending_down = [
        {"keyword": "hashtag strategy", "change": -12, "period": "7d"},
        {"keyword": "influencer marketing", "change": -8, "period": "7d"},
    ]

    return {
        "period": period,
        "daily_trends": daily,
        "sentiment_distribution": sentiment_dist,
        "keyword_cloud": keyword_cloud,
        "trending_up": trending_up,
        "trending_down": trending_down,
        "total_mentions": sum(d["mentions"] for d in daily),
        "avg_sentiment": 0.63,
    }


@router.post("/scan")
async def trigger_scan(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Manually trigger a scan for a specific keyword."""
    keyword = request.get("keyword", "")
    platforms = request.get("platforms", ["x"])

    if not keyword:
        raise HTTPException(status_code=400, detail="Keyword is required")

    # In production, this would trigger a Celery task
    return {
        "status": "scan_triggered",
        "keyword": keyword,
        "platforms": platforms,
        "message": f"Scan triggered for '{keyword}' on {', '.join(platforms)}",
    }
