"""Paid Campaign Tracking — Facebook Ads, LinkedIn Ads, paid vs organic."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/ads", tags=["ads"])


@router.get("/campaigns")
async def list_campaigns(platform: str = None, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """List ad campaigns."""
    campaigns = [
        {"id": "camp-1", "name": "Q3 Product Launch", "platform": "facebook", "status": "active", "budget": 5000, "spent": 2340, "impressions": 125000, "clicks": 3400, "conversions": 89, "ctr": 2.72, "cpc": 0.69, "roas": 4.2},
        {"id": "camp-2", "name": "Brand Awareness LinkedIn", "platform": "linkedin", "status": "active", "budget": 3000, "spent": 1800, "impressions": 89000, "clicks": 2100, "conversions": 45, "ctr": 2.36, "cpc": 0.86, "roas": 3.1},
        {"id": "camp-3", "name": "Instagram Reels Promo", "platform": "instagram", "status": "paused", "budget": 2000, "spent": 2000, "impressions": 67000, "clicks": 1800, "conversions": 32, "ctr": 2.69, "cpc": 1.11, "roas": 2.8},
    ]
    if platform:
        campaigns = [c for c in campaigns if c["platform"] == platform]
    return {"campaigns": campaigns, "total": len(campaigns)}


@router.get("/paid-vs-organic")
async def paid_vs_organic(period: str = "30d", current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Compare paid vs organic performance."""
    return {
        "organic": {"reach": 95000, "engagement": 8200, "clicks": 2100, "conversions": 45, "cost": 0},
        "paid": {"reach": 47500, "engagement": 4200, "clicks": 3400, "conversions": 89, "cost": 2340},
        "combined": {"reach": 142500, "engagement": 12400, "clicks": 5500, "conversions": 134, "cost": 2340},
        "insights": [
            "Paid campaigns drive 66% more conversions but cost $2,340",
            "Organic reach is 2x paid reach at zero cost",
            "Combined ROI: $12.40 per dollar spent on ads",
        ],
    }


@router.get("/campaigns/{campaign_id}")
async def get_campaign_details(campaign_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get detailed campaign metrics."""
    now = datetime.utcnow()
    return {
        "id": campaign_id,
        "daily_metrics": [
            {"date": (now - timedelta(days=i)).strftime("%m-%d"), "spend": 80 + (i % 3) * 20, "impressions": 4000 + i * 200, "clicks": 110 + i * 10, "conversions": 3 + (i % 4)}
            for i in range(14, 0, -1)
        ],
        "audience_breakdown": [
            {"segment": "25-34", "percentage": 35, "conversions": 31},
            {"segment": "35-44", "percentage": 28, "conversions": 25},
            {"segment": "18-24", "percentage": 20, "conversions": 18},
            {"segment": "45+", "percentage": 17, "conversions": 15},
        ],
        "top_ads": [
            {"id": "ad-1", "name": "Carousel - Product Features", "ctr": 3.2, "conversions": 34, "spend": 890},
            {"id": "ad-2", "name": "Video - Customer Testimonial", "ctr": 2.8, "conversions": 28, "spend": 780},
        ],
    }
