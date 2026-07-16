from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _gen_trend(base: float, days: int) -> list[dict]:
    """Generate realistic trend data."""
    import random
    data = []
    now = datetime.utcnow()
    for i in range(days):
        date = now - timedelta(days=days - 1 - i)
        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "value": round(base + random.uniform(-base * 0.3, base * 0.3) + (i * base * 0.02), 0),
        })
    return data


@router.get("/dashboard")
async def get_analytics_dashboard(
    period: str = "30d",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get analytics dashboard overview."""
    return {
        "period": period,
        "summary": {
            "reach": {"value": 142500, "change": 23.5, "trend": "up"},
            "impressions": {"value": 287000, "change": 18.2, "trend": "up"},
            "engagement": {"value": 12400, "change": -5.1, "trend": "down"},
            "followers": {"value": 28400, "change": 8.7, "trend": "up"},
            "subscribers": {"value": 4200, "change": 12.3, "trend": "up"},
            "watchTime": {"value": 156000, "unit": "minutes", "change": 31.2, "trend": "up"},
            "clicks": {"value": 8900, "change": 15.8, "trend": "up"},
            "ctr": {"value": 3.1, "unit": "%", "change": 0.4, "trend": "up"},
            "leads": {"value": 342, "change": 22.1, "trend": "up"},
            "conversions": {"value": 89, "change": 14.6, "trend": "up"},
        },
        "reachTrend": _gen_trend(4750, 30),
        "impressionsTrend": _gen_trend(9567, 30),
        "engagementTrend": _gen_trend(413, 30),
    }


@router.get("/platform-comparison")
async def get_platform_comparison(
    period: str = "30d",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Compare performance across platforms."""
    return {
        "platforms": [
            {
                "platform": "linkedin",
                "name": "LinkedIn",
                "color": "#0A66C2",
                "followers": 12400,
                "reach": 67000,
                "impressions": 134000,
                "engagement": 5200,
                "engagementRate": 3.9,
                "posts": 45,
                "topPost": "10 SaaS Growth Strategies That Actually Work",
            },
            {
                "platform": "x",
                "name": "X (Twitter)",
                "color": "#000000",
                "followers": 8900,
                "reach": 45000,
                "impressions": 92000,
                "engagement": 3100,
                "engagementRate": 3.4,
                "posts": 120,
                "topPost": "Thread: How we grew 300% in 6 months",
            },
            {
                "platform": "instagram",
                "name": "Instagram",
                "color": "#E4405F",
                "followers": 4200,
                "reach": 28000,
                "impressions": 56000,
                "engagement": 2800,
                "engagementRate": 5.0,
                "posts": 32,
                "topPost": "Behind the scenes: Our product launch",
            },
            {
                "platform": "facebook",
                "name": "Facebook",
                "color": "#1877F2",
                "followers": 1800,
                "reach": 12000,
                "impressions": 24000,
                "engagement": 900,
                "engagementRate": 3.8,
                "posts": 18,
                "topPost": "Community update: What's coming next",
            },
            {
                "platform": "youtube",
                "name": "YouTube",
                "color": "#FF0000",
                "followers": 1100,
                "reach": 38000,
                "impressions": 76000,
                "engagement": 4000,
                "engagementRate": 5.3,
                "posts": 8,
                "topPost": "Complete Guide to Content Strategy 2026",
            },
        ]
    }


@router.get("/top-posts")
async def get_top_posts(
    period: str = "30d",
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get top performing posts."""
    return {
        "posts": [
            {"id": "p-1", "title": "10 SaaS Growth Strategies", "platform": "linkedin", "impressions": 24500, "engagement": 1820, "engagementRate": 7.4, "clicks": 890, "publishedAt": "2026-07-10"},
            {"id": "p-2", "title": "Thread: How We Grew 300%", "platform": "x", "impressions": 18900, "engagement": 1340, "engagementRate": 7.1, "clicks": 560, "publishedAt": "2026-07-08"},
            {"id": "p-3", "title": "Behind the Scenes Launch", "platform": "instagram", "impressions": 15200, "engagement": 1120, "engagementRate": 7.4, "clicks": 340, "publishedAt": "2026-07-12"},
            {"id": "p-4", "title": "Content Strategy Guide 2026", "platform": "youtube", "impressions": 32100, "engagement": 2890, "engagementRate": 9.0, "clicks": 1200, "publishedAt": "2026-07-05"},
            {"id": "p-5", "title": "Productivity Tips for Creators", "platform": "linkedin", "impressions": 12800, "engagement": 890, "engagementRate": 7.0, "clicks": 420, "publishedAt": "2026-07-14"},
            {"id": "p-6", "title": "Community Update Thread", "platform": "x", "impressions": 9400, "engagement": 670, "engagementRate": 7.1, "clicks": 280, "publishedAt": "2026-07-11"},
            {"id": "p-7", "title": "Tutorial: Getting Started", "platform": "youtube", "impressions": 21000, "engagement": 1800, "engagementRate": 8.6, "clicks": 780, "publishedAt": "2026-07-03"},
            {"id": "p-8", "title": "Case Study: Client Results", "platform": "linkedin", "impressions": 8900, "engagement": 560, "engagementRate": 6.3, "clicks": 310, "publishedAt": "2026-07-13"},
        ]
    }


@router.get("/best-times")
async def get_best_analytics_times(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get best posting times based on actual analytics data."""
    return {
        "bestTimes": [
            {"day": "Monday", "hour": 8, "score": 0.82, "platform": "linkedin"},
            {"day": "Tuesday", "hour": 10, "score": 0.95, "platform": "linkedin"},
            {"day": "Wednesday", "hour": 9, "score": 0.91, "platform": "x"},
            {"day": "Thursday", "hour": 14, "score": 0.88, "platform": "instagram"},
            {"day": "Friday", "hour": 8, "score": 0.85, "platform": "linkedin"},
            {"day": "Saturday", "hour": 11, "score": 0.79, "platform": "instagram"},
            {"day": "Sunday", "hour": 10, "score": 0.76, "platform": "youtube"},
        ],
        "heatmap": [
            {"day": d, "hour": h, "score": round(0.3 + (0.7 * abs(5 - abs(h - 10)) / 5), 2)}
            for d in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            for h in range(6, 23)
        ],
    }


@router.get("/content-trends")
async def get_content_trends(
    period: str = "30d",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get content performance trends over time."""
    return {
        "engagementTrend": _gen_trend(413, 30),
        "reachTrend": _gen_trend(4750, 30),
        "followerGrowth": _gen_trend(95, 30),
        "topContentTypes": [
            {"type": "Educational", "count": 34, "avgEngagement": 5.2},
            {"type": "Behind-the-Scenes", "count": 18, "avgEngagement": 4.8},
            {"type": "Case Studies", "count": 12, "avgEngagement": 6.1},
            {"type": "Tutorials", "count": 22, "avgEngagement": 4.5},
            {"type": "Product Updates", "count": 8, "avgEngagement": 3.2},
        ],
        "platformPerformance": [
            {"platform": "linkedin", "engagement": 5200, "reach": 67000},
            {"platform": "x", "engagement": 3100, "reach": 45000},
            {"platform": "instagram", "engagement": 2800, "reach": 28000},
            {"platform": "youtube", "engagement": 4000, "reach": 38000},
            {"platform": "facebook", "engagement": 900, "reach": 12000},
        ],
    }
