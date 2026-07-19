"""Employee Advocacy (Amplify) — share approved content on personal networks."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/advocacy", tags=["advocacy"])


@router.get("/shareable")
async def list_shareable():
    """List content available for employee sharing."""
    shareable = [
        {"id": "sh-1", "title": "10 Tips for Content Creation", "platform": "linkedin", "share_text": "Great insights from our team on content creation! Here are 10 tips that actually work.", "url": "https://socialmediamanager.ai/blog/10-tips", "shares_count": 12, "image_url": None},
        {"id": "sh-2", "title": "How We Grew 300% in 6 Months", "platform": "x", "share_text": "Thread: How our team grew 300% in 6 months. A playbook for SaaS growth.", "url": "https://socialmediamanager.ai/blog/growth-playbook", "shares_count": 8, "image_url": None},
        {"id": "sh-3", "title": "Behind the Scenes: Product Launch", "platform": "instagram", "share_text": "Proud to be part of this launch! Check out what we've been building.", "url": "https://socialmediamanager.ai/launch", "shares_count": 5, "image_url": None},
    ]
    return {"shareable": shareable, "total": len(shareable)}


@router.post("/share")
async def share_content(request: dict):
    """Share content to a personal social network."""
    post_id = request.get("post_id", "")
    platform = request.get("platform", "linkedin")
    custom_text = request.get("custom_text", "")

    return {
        "id": str(uuid.uuid4()),
        "post_id": post_id,
        "platform": platform,
        "shared_by": "Demo User",
        "shared_at": datetime.utcnow().isoformat(),
        "text": custom_text or "Check out this content!",
        "status": "shared",
    }


@router.get("/metrics")
async def get_advocacy_metrics():
    """Get advocacy program metrics."""
    return {
        "total_shares": 156,
        "total_reach_from_shares": 23400,
        "engagement_from_shares": 1890,
        "active_advocates": 12,
        "top_advocates": [
            {"name": "Sarah Chen", "shares": 28, "reach": 4500, "engagement": 340},
            {"name": "Marcus Johnson", "shares": 22, "reach": 3800, "engagement": 290},
            {"name": "Priya Patel", "shares": 18, "reach": 3200, "engagement": 245},
        ],
        "shares_by_platform": {"linkedin": 89, "x": 42, "facebook": 25},
        "shares_by_week": [
            {"week": "W28", "shares": 45},
            {"week": "W27", "shares": 38},
            {"week": "W26", "shares": 42},
            {"week": "W25", "shares": 31},
        ],
    }


@router.post("/invite")
async def invite_advocate(request: dict):
    """Invite employees to join advocacy program."""
    emails = request.get("emails", [])
    return {
        "invited": len(emails),
        "emails": emails,
        "message": f"Invitations sent to {len(emails)} employees",
    }
