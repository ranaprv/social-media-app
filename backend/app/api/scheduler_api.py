from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/scheduler", tags=["scheduler"])

TIMEZONES = [
    "UTC", "US/Eastern", "US/Central", "US/Pacific", "Europe/London",
    "Europe/Paris", "Europe/Berlin", "Asia/Tokyo", "Asia/Shanghai",
    "Asia/Kolkata", "Australia/Sydney", "America/Sao_Paulo",
]

BEST_TIMES = {
    "linkedin": [
        {"day": 1, "hour": 8, "score": 0.95, "label": "Tuesday 8 AM"},
        {"day": 2, "hour": 10, "score": 0.92, "label": "Wednesday 10 AM"},
        {"day": 3, "hour": 9, "score": 0.88, "label": "Thursday 9 AM"},
        {"day": 1, "hour": 12, "score": 0.85, "label": "Tuesday 12 PM"},
        {"day": 4, "hour": 8, "score": 0.82, "label": "Friday 8 AM"},
    ],
    "x": [
        {"day": 1, "hour": 12, "score": 0.93, "label": "Tuesday 12 PM"},
        {"day": 2, "hour": 9, "score": 0.90, "label": "Wednesday 9 AM"},
        {"day": 3, "hour": 17, "score": 0.87, "label": "Thursday 5 PM"},
        {"day": 0, "hour": 10, "score": 0.84, "label": "Monday 10 AM"},
        {"day": 4, "hour": 14, "score": 0.80, "label": "Friday 2 PM"},
    ],
    "instagram": [
        {"day": 1, "hour": 11, "score": 0.94, "label": "Tuesday 11 AM"},
        {"day": 3, "hour": 14, "score": 0.91, "label": "Thursday 2 PM"},
        {"day": 5, "hour": 11, "score": 0.89, "label": "Saturday 11 AM"},
        {"day": 2, "hour": 19, "score": 0.86, "label": "Wednesday 7 PM"},
        {"day": 0, "hour": 20, "score": 0.83, "label": "Monday 8 PM"},
    ],
    "facebook": [
        {"day": 1, "hour": 13, "score": 0.92, "label": "Tuesday 1 PM"},
        {"day": 3, "hour": 15, "score": 0.89, "label": "Thursday 3 PM"},
        {"day": 2, "hour": 11, "score": 0.86, "label": "Wednesday 11 AM"},
        {"day": 4, "hour": 10, "score": 0.83, "label": "Friday 10 AM"},
        {"day": 0, "hour": 12, "score": 0.80, "label": "Monday 12 PM"},
    ],
    "youtube": [
        {"day": 5, "hour": 15, "score": 0.96, "label": "Saturday 3 PM"},
        {"day": 6, "hour": 9, "score": 0.93, "label": "Sunday 9 AM"},
        {"day": 3, "hour": 14, "score": 0.88, "label": "Thursday 2 PM"},
        {"day": 1, "hour": 16, "score": 0.85, "label": "Tuesday 4 PM"},
        {"day": 4, "hour": 17, "score": 0.82, "label": "Friday 5 PM"},
    ],
}


@router.get("/config")
async def get_scheduler_config(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get scheduler configuration."""
    return {
        "timezone": "US/Eastern",
        "auto_publish": False,
        "queue_enabled": True,
        "max_daily_posts": 5,
        "platform_settings": {
            "linkedin": {"connected": True, "username": "socialmediamanager", "auto_publish": False, "queue_enabled": True},
            "x": {"connected": True, "username": "@socialmediamanager", "auto_publish": True, "queue_enabled": True},
            "instagram": {"connected": False, "username": None, "auto_publish": False, "queue_enabled": False},
            "facebook": {"connected": True, "username": "Social Media Manager Page", "auto_publish": False, "queue_enabled": True},
            "youtube": {"connected": False, "username": None, "auto_publish": False, "queue_enabled": False},
        },
        "timezones": TIMEZONES,
    }


@router.put("/config")
async def update_scheduler_config(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update scheduler configuration."""
    return {"message": "Config updated", "config": request}


@router.post("/schedule")
async def schedule_content(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Schedule content for publishing. Supports content types and Google Drive sources."""
    content_type = request.get("content_type", "linkedin_post")
    platform = request.get("platform", "linkedin")
    title = request.get("title", "")
    content = request.get("content", "")
    drive_file_id = request.get("drive_file_id", None)
    drive_file_url = request.get("drive_file_url", None)
    scheduled_at = request.get("scheduled_at", "")
    media_urls = request.get("media_urls", [])

    # If content is on Drive, fetch it
    if drive_file_id and not content:
        from app.services.google_drive import drive_service
        url = await drive_service.get_file_url(drive_file_id)
        if url:
            drive_file_url = url

    return {
        "id": str(uuid.uuid4()),
        "content_type": content_type,
        "platform": platform,
        "title": title,
        "scheduled_at": scheduled_at,
        "drive_file_url": drive_file_url,
        "media_urls": media_urls,
        "status": "queued",
        "message": f"Content scheduled for {platform} at {scheduled_at}",
    }


@router.post("/content-planner")
async def create_content_plan(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a content plan: what content type, for which platform, at what time."""
    plan_name = request.get("name", "Content Plan")
    items = request.get("items", [])
    # Each item: {content_type, platform, scheduled_at, drive_file_id, title, media_urls}

    created = []
    for item in items:
        created.append({
            "id": str(uuid.uuid4()),
            "content_type": item.get("content_type", "linkedin_post"),
            "platform": item.get("platform", "linkedin"),
            "title": item.get("title", ""),
            "scheduled_at": item.get("scheduled_at", ""),
            "drive_file_id": item.get("drive_file_id"),
            "media_urls": item.get("media_urls", []),
            "status": "planned",
        })

    return {
        "id": str(uuid.uuid4()),
        "name": plan_name,
        "items": created,
        "total_items": len(created),
        "message": f"Content plan '{plan_name}' created with {len(created)} items",
    }


@router.get("/content-plans")
async def list_content_plans(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all content plans."""
    return {"plans": []}


@router.get("/drive-files")
async def list_drive_files(
    folder_id: str = None,
    query: str = "",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List files from Google Drive for content selection."""
    from app.services.google_drive import drive_service
    files = await drive_service.list_files(folder_id=folder_id, query=query)
    return {"files": files, "count": len(files)}


@router.get("/queue")
async def get_queue(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the publishing queue."""
    queue = [
        {
            "id": "q-1",
            "post_id": "post-1",
            "title": "10 Tips for Content Creation",
            "platform": "linkedin",
            "scheduled_at": "2026-07-16T09:00:00",
            "status": "queued",
            "retries": 0,
            "max_retries": 3,
        },
        {
            "id": "q-2",
            "post_id": "post-2",
            "title": "Thread: Growth Strategies",
            "platform": "x",
            "scheduled_at": "2026-07-16T12:00:00",
            "status": "queued",
            "retries": 0,
            "max_retries": 3,
        },
        {
            "id": "q-3",
            "post_id": "post-3",
            "title": "Behind the Scenes Reel",
            "platform": "instagram",
            "scheduled_at": "2026-07-16T14:00:00",
            "status": "publishing",
            "retries": 0,
            "max_retries": 3,
        },
        {
            "id": "q-4",
            "post_id": "post-4",
            "title": "Weekly Motivation Post",
            "platform": "facebook",
            "scheduled_at": "2026-07-17T10:00:00",
            "status": "failed",
            "retries": 2,
            "max_retries": 3,
        },
    ]
    return {"queue": queue}


@router.get("/best-times")
async def get_best_times(
    platform: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get best posting times for platforms."""
    if platform and platform in BEST_TIMES:
        return {"platform": platform, "times": BEST_TIMES[platform]}
    return {"best_times": BEST_TIMES}


@router.post("/queue/{item_id}/retry")
async def retry_queue_item(
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retry a failed queue item."""
    return {"id": item_id, "message": "Retrying", "status": "queued"}


@router.delete("/queue/{item_id}")
async def remove_from_queue(
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove item from queue."""
    return {"id": item_id, "message": "Removed from queue"}
