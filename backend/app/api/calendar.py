from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.content import Post, ContentCalendar

router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("/events")
async def get_calendar_events(
    start_date: str = None,
    end_date: str = None,
    platform: str = None,
    status: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get calendar events within a date range."""
    # Return demo events for now
    base_date = datetime.utcnow()
    events = []
    statuses = ["draft", "review", "scheduled", "published", "failed"]
    platforms = ["linkedin", "x", "instagram", "facebook", "youtube"]
    titles = [
        "10 Tips for Content Creation",
        "Behind the Scenes: Our Process",
        "Industry Insights: Q3 Trends",
        "How We Grew 200% in 6 Months",
        "Product Update: New Features",
        "Weekly Motivation Monday",
        "Tutorial: Getting Started Guide",
        "Case Study: Client Success",
        "FAQ: Common Questions Answered",
        "Community Spotlight",
    ]

    for i in range(15):
        day_offset = (i % 7) - 3
        event_date = base_date + timedelta(days=day_offset)
        events.append({
            "id": f"cal-{i}",
            "post_id": f"post-{i}",
            "title": titles[i % len(titles)],
            "content": f"Content for {titles[i % len(titles)]}",
            "platform": platforms[i % len(platforms)],
            "status": statuses[i % len(statuses)],
            "date": event_date.strftime("%Y-%m-%d"),
            "time_slot": f"{9 + (i % 10)}:00",
            "campaign_id": f"camp-{i % 3}" if i % 3 == 0 else None,
            "is_recurring": i % 4 == 0,
            "recurring_pattern": "weekly" if i % 4 == 0 else None,
            "author_id": current_user.id,
            "author_name": current_user.name or "User",
            "media_urls": [],
        })

    return {"events": events}


@router.post("/events")
async def create_calendar_event(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new calendar event."""
    return {
        "id": str(uuid.uuid4()),
        "message": "Event created",
        "event": {
            "id": str(uuid.uuid4()),
            "title": request.get("title", "Untitled"),
            "platform": request.get("platform", "linkedin"),
            "status": "draft",
            "date": request.get("date", datetime.utcnow().strftime("%Y-%m-%d")),
            "time_slot": request.get("time_slot", "09:00"),
        },
    }


@router.put("/events/{event_id}")
async def update_calendar_event(
    event_id: str,
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a calendar event (drag & drop, status change)."""
    return {"id": event_id, "message": "Event updated", "updates": request}


@router.delete("/events/{event_id}")
async def delete_calendar_event(
    event_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a calendar event."""
    return {"id": event_id, "message": "Event deleted"}


@router.get("/campaigns")
async def get_campaigns(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all campaigns."""
    campaigns = [
        {
            "id": "camp-0",
            "name": "Product Launch Q3",
            "description": "Content campaign for Q3 product launch",
            "color": "#3b82f6",
            "start_date": "2026-07-01",
            "end_date": "2026-09-30",
            "event_count": 24,
        },
        {
            "id": "camp-1",
            "name": "Thought Leadership",
            "description": "Weekly thought leadership content series",
            "color": "#8b5cf6",
            "start_date": "2026-07-01",
            "end_date": "2026-12-31",
            "event_count": 52,
        },
        {
            "id": "camp-2",
            "name": "Summer Engagement",
            "description": "Community engagement campaign for summer",
            "color": "#06b6d4",
            "start_date": "2026-06-01",
            "end_date": "2026-08-31",
            "event_count": 18,
        },
    ]
    return {"campaigns": campaigns}


@router.post("/campaigns")
async def create_campaign(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new campaign."""
    return {
        "id": str(uuid.uuid4()),
        "message": "Campaign created",
        "campaign": {
            "id": str(uuid.uuid4()),
            "name": request.get("name", "New Campaign"),
            "description": request.get("description", ""),
            "color": request.get("color", "#3b82f6"),
            "start_date": request.get("start_date"),
            "end_date": request.get("end_date"),
            "event_count": 0,
        },
    }
