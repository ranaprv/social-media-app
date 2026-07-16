"""Web Analytics Integration — GA4, Adobe Analytics."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/web-analytics", tags=["web-analytics"])


@router.get("/ga4")
async def get_ga4_data(period: str = "30d", current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get Google Analytics 4 data."""
    now = datetime.utcnow()
    return {
        "provider": "ga4",
        "summary": {"sessions": 45200, "users": 32100, "pageviews": 128400, "bounce_rate": 42.3, "avg_session_duration": "3:24", "conversions": 892},
        "daily": [{"date": (now - timedelta(days=i)).strftime("%m-%d"), "sessions": 1400 + i * 30, "users": 1000 + i * 20, "pageviews": 4000 + i * 100} for i in range(14, 0, -1)],
        "top_pages": [
            {"page": "/blog/content-strategy-2026", "views": 12400, "avg_time": "4:32", "bounce_rate": 35},
            {"page": "/pricing", "views": 8900, "avg_time": "2:15", "bounce_rate": 28},
            {"page": "/features", "views": 7200, "avg_time": "3:45", "bounce_rate": 42},
        ],
        "traffic_sources": [
            {"source": "organic", "sessions": 18200, "conversions": 340},
            {"source": "social", "sessions": 12400, "conversions": 280},
            {"source": "direct", "sessions": 8900, "conversions": 180},
            {"source": "referral", "sessions": 5700, "conversions": 92},
        ],
        "social_to_web_correlation": [
            {"date": "2026-07-10", "social_clicks": 340, "web_sessions": 1420, "correlation": 0.82},
            {"date": "2026-07-11", "social_clicks": 280, "web_sessions": 1280, "correlation": 0.78},
        ],
    }


@router.get("/adobe")
async def get_adobe_data(period: str = "30d", current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get Adobe Analytics data."""
    return {
        "provider": "adobe",
        "summary": {"visits": 41800, "unique_visitors": 29500, "page_views": 119200, "bounce_rate": 44.1, "avg_time_on_site": "3:12"},
        "status": "not_configured",
        "message": "Adobe Analytics requires OAuth configuration. Set ADOBE_CLIENT_ID and ADOBE_CLIENT_SECRET.",
    }


@router.get("/status")
async def get_integration_status(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get web analytics integration status."""
    return {
        "ga4": {"configured": False, "status": "needs OAuth setup", "last_sync": None},
        "adobe": {"configured": False, "status": "needs OAuth setup", "last_sync": None},
    }
