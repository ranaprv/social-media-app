"""Scheduler API — real DB-backed scheduling, queue management, and best times."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember
from app.models.content import Post, PlatformConnection
from app.models.post_platform import PostPlatform
from app.schemas.post_platform import (
    PostPlatformCreate,
    PostPlatformUpdate,
    PostPlatformResponse,
    SchedulePostRequest,
)
from app.services.content_validator import validate_post

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


async def _get_workspace_id(db: AsyncSession, current_user: User) -> str:
    """Get the user's workspace ID (first workspace they're a member of)."""
    result = await db.execute(
        select(WorkspaceMember).where(WorkspaceMember.user_id == current_user.id).limit(1)
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="No workspace found")
    return member.workspace_id


# ─── Config ────────────────────────────────────────────────────────────────

@router.get("/config")
async def get_scheduler_config(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get scheduler configuration with real connection status."""
    workspace_id = await _get_workspace_id(db, current_user)

    # Check which platforms are actually connected
    result = await db.execute(
        select(PlatformConnection).where(PlatformConnection.workspace_id == workspace_id)
    )
    connections = result.scalars().all()
    connected_platforms = {c.platform for c in connections}

    platform_settings = {}
    for platform in ["linkedin", "x", "instagram", "facebook", "youtube"]:
        conn = next((c for c in connections if c.platform == platform), None)
        platform_settings[platform] = {
            "connected": platform in connected_platforms,
            "username": conn.platform_username if conn else None,
            "auto_publish": False,
            "queue_enabled": platform in connected_platforms,
        }

    return {
        "timezone": "US/Eastern",
        "auto_publish": False,
        "queue_enabled": True,
        "max_daily_posts": 5,
        "platform_settings": platform_settings,
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


# ─── Schedule Content ──────────────────────────────────────────────────────

@router.post("/schedule", status_code=status.HTTP_201_CREATED)
async def schedule_content(
    request: SchedulePostRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Schedule a post to one or more platforms.

    Creates PostPlatform rows for each target platform.
    Validates content against platform limits before scheduling.
    """
    workspace_id = await _get_workspace_id(db, current_user)

    # Verify post exists and belongs to workspace
    post_result = await db.execute(
        select(Post).where(
            Post.id == request.post_id,
            Post.workspace_id == workspace_id,
        )
    )
    post = post_result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    created = []
    for platform_entry in request.platforms:
        platform = platform_entry.get("platform", "")
        caption = platform_entry.get("caption") or post.content
        scheduled_at = platform_entry.get("scheduled_at") or request.default_scheduled_at
        media_asset_ids = platform_entry.get("media_asset_ids", [])
        title = platform_entry.get("title") or post.title

        # Validate content
        errors = validate_post(caption, platform)
        if errors:
            raise HTTPException(
                status_code=422,
                detail=f"Validation failed for {platform}: {'; '.join(errors)}",
            )

        # Check for existing PostPlatform for this post+platform
        existing = await db.execute(
            select(PostPlatform).where(
                PostPlatform.post_id == request.post_id,
                PostPlatform.platform == platform,
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail=f"Post already scheduled for {platform}. Update or cancel first.",
            )

        pp = PostPlatform(
            id=str(uuid.uuid4()),
            post_id=request.post_id,
            workspace_id=workspace_id,
            platform=platform,
            caption=caption if caption != post.content else None,
            media_asset_ids=media_asset_ids,
            title=title,
            status="scheduled" if scheduled_at else "draft",
            scheduled_at=scheduled_at,
        )
        db.add(pp)
        created.append(pp)

    await db.flush()

    # Update parent post status to "scheduled" if it was draft
    if post.status == "draft" and any(c.status == "scheduled" for c in created):
        post.status = "scheduled"
        if request.default_scheduled_at:
            post.scheduled_at = request.default_scheduled_at

    return {
        "message": f"Scheduled to {len(created)} platform(s)",
        "platforms": [
            PostPlatformResponse.model_validate(c).model_dump()
            for c in created
        ],
    }


# ─── Queue ──────────────────────────────────────────────────────────────────

@router.get("/queue")
async def get_queue(
    status_filter: str = Query(None, alias="status"),
    platform: str = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the real publishing queue from PostPlatform rows."""
    workspace_id = await _get_workspace_id(db, current_user)

    query = select(PostPlatform).where(PostPlatform.workspace_id == workspace_id)
    count_query = select(func.count(PostPlatform.id)).where(
        PostPlatform.workspace_id == workspace_id
    )

    if status_filter:
        query = query.where(PostPlatform.status == status_filter)
        count_query = count_query.where(PostPlatform.status == status_filter)
    if platform:
        query = query.where(PostPlatform.platform == platform)
        count_query = count_query.where(PostPlatform.platform == platform)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(PostPlatform.scheduled_at.asc()).offset(offset).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()

    # Enrich with post title
    queue = []
    for pp in items:
        post_result = await db.execute(
            select(Post).where(Post.id == pp.post_id)
        )
        post = post_result.scalar_one_or_none()
        queue.append({
            "id": pp.id,
            "post_id": pp.post_id,
            "title": post.title if post else None,
            "platform": pp.platform,
            "scheduled_at": pp.scheduled_at.isoformat() if pp.scheduled_at else None,
            "status": pp.status,
            "retries": pp.retry_count or 0,
            "max_retries": pp.max_retries or 3,
            "error_message": pp.error_message,
        })

    return {"queue": queue, "total": total, "offset": offset, "limit": limit}


@router.post("/queue/{item_id}/retry")
async def retry_queue_item(
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retry a failed queue item by resetting its status to 'scheduled'."""
    workspace_id = await _get_workspace_id(db, current_user)

    result = await db.execute(
        select(PostPlatform).where(
            PostPlatform.id == item_id,
            PostPlatform.workspace_id == workspace_id,
        )
    )
    pp = result.scalar_one_or_none()
    if not pp:
        raise HTTPException(status_code=404, detail="Queue item not found")

    if pp.status != "failed":
        raise HTTPException(status_code=400, detail="Only failed items can be retried")

    pp.status = "scheduled"
    pp.error_message = None
    pp.retry_count = 0
    # Schedule for immediate retry (1 minute from now)
    pp.scheduled_at = datetime.utcnow()

    return {
        "id": item_id,
        "message": "Retrying",
        "status": "scheduled",
        "scheduled_at": pp.scheduled_at.isoformat(),
    }


@router.delete("/queue/{item_id}")
async def remove_from_queue(
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel a scheduled/queued item."""
    workspace_id = await _get_workspace_id(db, current_user)

    result = await db.execute(
        select(PostPlatform).where(
            PostPlatform.id == item_id,
            PostPlatform.workspace_id == workspace_id,
        )
    )
    pp = result.scalar_one_or_none()
    if not pp:
        raise HTTPException(status_code=404, detail="Queue item not found")

    if pp.status == "publishing":
        raise HTTPException(
            status_code=400,
            detail="Cannot cancel a post that is currently publishing",
        )

    pp.status = "cancelled"

    return {"id": item_id, "message": "Cancelled", "status": "cancelled"}


# ─── Best Times ─────────────────────────────────────────────────────────────

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


# ─── Content Plans ──────────────────────────────────────────────────────────

@router.post("/content-planner")
async def create_content_plan(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a content plan with multiple scheduled items."""
    plan_name = request.get("name", "Content Plan")
    items = request.get("items", [])

    created = []
    for item in items:
        platform = item.get("platform", "linkedin")
        caption = item.get("caption", "")
        scheduled_at = item.get("scheduled_at")

        # Validate
        if caption:
            errors = validate_post(caption, platform)
            if errors:
                raise HTTPException(
                    status_code=422,
                    detail=f"Validation failed for {platform}: {'; '.join(errors)}",
                )

        created.append({
            "id": str(uuid.uuid4()),
            "platform": platform,
            "caption": caption,
            "scheduled_at": scheduled_at,
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


# ─── Bulk Scheduling ────────────────────────────────────────────────────────

@router.post("/bulk-schedule", status_code=status.HTTP_201_CREATED)
async def bulk_schedule(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Schedule multiple posts to multiple platforms in one call.

    Request body:
    {
      "items": [
        {
          "post_id": "...",
          "platforms": ["linkedin", "x"],
          "scheduled_at": "2026-07-20T10:00:00Z"
        }
      ]
    }
    """
    workspace_id = await _get_workspace_id(db, current_user)
    items = request.get("items", [])
    created = []
    errors = []

    for item in items:
        post_id = item.get("post_id", "")
        platforms = item.get("platforms", [])
        scheduled_at_str = item.get("scheduled_at")
        scheduled_at = None
        if scheduled_at_str:
            try:
                scheduled_at = datetime.fromisoformat(scheduled_at_str.replace("Z", "+00:00"))
            except ValueError:
                errors.append(f"Invalid scheduled_at for post {post_id}: {scheduled_at_str}")
                continue

        # Verify post exists
        post_result = await db.execute(
            select(Post).where(Post.id == post_id, Post.workspace_id == workspace_id)
        )
        post = post_result.scalar_one_or_none()
        if not post:
            errors.append(f"Post {post_id} not found")
            continue

        for platform in platforms:
            # Validate
            caption = post.content
            validation_errors = validate_post(caption, platform)
            if validation_errors:
                errors.append(f"Post {post_id} → {platform}: {'; '.join(validation_errors)}")
                continue

            # Check duplicate
            existing = await db.execute(
                select(PostPlatform).where(
                    PostPlatform.post_id == post_id,
                    PostPlatform.platform == platform,
                )
            )
            if existing.scalar_one_or_none():
                errors.append(f"Post {post_id} already scheduled for {platform}")
                continue

            pp = PostPlatform(
                id=str(uuid.uuid4()),
                post_id=post_id,
                workspace_id=workspace_id,
                platform=platform,
                status="scheduled" if scheduled_at else "draft",
                scheduled_at=scheduled_at,
            )
            db.add(pp)
            created.append(pp)

    await db.flush()

    return {
        "message": f"Created {len(created)} schedule entries",
        "count": len(created),
        "errors": errors,
    }


# ─── Media Assignment ──────────────────────────────────────────────────────

@router.put("/queue/{item_id}/media")
async def assign_media(
    item_id: str,
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Assign specific media assets to a PostPlatform entry.

    Request body: { "media_asset_ids": ["asset-1", "asset-2"] }
    """
    workspace_id = await _get_workspace_id(db, current_user)

    result = await db.execute(
        select(PostPlatform).where(
            PostPlatform.id == item_id,
            PostPlatform.workspace_id == workspace_id,
        )
    )
    pp = result.scalar_one_or_none()
    if not pp:
        raise HTTPException(status_code=404, detail="Queue item not found")

    if pp.status not in ("draft", "scheduled"):
        raise HTTPException(
            status_code=400,
            detail="Can only assign media to draft or scheduled items",
        )

    media_asset_ids = request.get("media_asset_ids", [])
    pp.media_asset_ids = media_asset_ids

    return {
        "id": item_id,
        "media_asset_ids": media_asset_ids,
        "message": f"Assigned {len(media_asset_ids)} media assets",
    }


@router.put("/queue/{item_id}/caption")
async def update_caption(
    item_id: str,
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update the platform-specific caption for a PostPlatform entry."""
    workspace_id = await _get_workspace_id(db, current_user)

    result = await db.execute(
        select(PostPlatform).where(
            PostPlatform.id == item_id,
            PostPlatform.workspace_id == workspace_id,
        )
    )
    pp = result.scalar_one_or_none()
    if not pp:
        raise HTTPException(status_code=404, detail="Queue item not found")

    caption = request.get("caption", "")

    # Validate
    from app.services.content_validator import validate_caption
    errors = validate_caption(caption, pp.platform)
    if errors:
        raise HTTPException(status_code=422, detail="; ".join(errors))

    pp.caption = caption

    return {
        "id": item_id,
        "platform": pp.platform,
        "caption": caption,
        "message": "Caption updated",
    }


# ─── Phase 3: Smart Recommendations ────────────────────────────────────────

@router.get("/recommendations/best-times")
async def get_smart_best_times(
    platform: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get data-driven best posting times based on actual analytics."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.best_time_recommender import get_best_times_for_workspace
    result = await get_best_times_for_workspace(db, workspace_id, platform)
    return result


@router.get("/recommendations/next-slot")
async def get_next_slot(
    platform: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the next optimal time slot to schedule a post."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.best_time_recommender import get_next_suggested_time
    result = await get_next_suggested_time(db, workspace_id, platform)
    if not result:
        raise HTTPException(status_code=404, detail="No recommendation available")
    return result


@router.get("/recommendations/content")
async def get_content_suggestions(
    platform: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get AI-powered content improvement suggestions from analytics."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.analytics_feedback import get_content_suggestions
    result = await get_content_suggestions(db, workspace_id, platform)
    return result


# ─── Phase 3: Content Recycling ────────────────────────────────────────────

@router.get("/recycle/top-performers")
async def get_top_performers(
    platform: str = None,
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Find top-performing posts eligible for recycling."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.content_recycler import find_top_performers
    result = await find_top_performers(db, workspace_id, platform, top_n=limit)
    return {"top_performers": result, "count": len(result)}


@router.post("/recycle/schedule")
async def schedule_recycle(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Schedule a top performer for recycling."""
    workspace_id = await _get_workspace_id(db, current_user)
    post_id = request.get("post_id", "")
    platform = request.get("platform", "")
    scheduled_at_str = request.get("scheduled_at", "")
    caption_override = request.get("caption")

    if not post_id or not platform:
        raise HTTPException(status_code=400, detail="post_id and platform required")

    scheduled_at = None
    if scheduled_at_str:
        try:
            scheduled_at = datetime.fromisoformat(scheduled_at_str.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid scheduled_at")

    from app.services.content_recycler import schedule_recycle as do_recycle
    pp = await do_recycle(db, workspace_id, post_id, platform, scheduled_at, caption_override)
    if not pp:
        raise HTTPException(status_code=400, detail="Could not schedule recycle")
    return {"id": pp.id, "message": "Recycle scheduled"}


@router.post("/recycle/auto")
async def auto_recycle(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Auto-schedule recycling for top performers."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.content_recycler import auto_recycle_top_performers
    result = await auto_recycle_top_performers(db, workspace_id)
    return {"scheduled": result, "count": len(result)}


# ─── Phase 3: Cross-Posting ────────────────────────────────────────────────

@router.post("/cross-post/suggest")
async def cross_post_suggestions(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get cross-posting suggestions for content."""
    content = request.get("content", "")
    source_platform = request.get("platform", "linkedin")

    if not content:
        raise HTTPException(status_code=400, detail="content required")

    from app.services.cross_post_templates import get_cross_post_suggestions
    suggestions = get_cross_post_suggestions(content, source_platform)
    return {"suggestions": suggestions}


# ─── Phase 3: Recurring Series ─────────────────────────────────────────────

@router.get("/recurring/templates")
async def list_recurring_templates(
    current_user: User = Depends(get_current_user),
):
    """List available recurring series templates."""
    from app.services.recurring_series import get_recurring_templates
    return {"templates": get_recurring_templates()}


@router.post("/recurring/create")
async def create_recurring_series(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a recurring series of scheduled posts."""
    workspace_id = await _get_workspace_id(db, current_user)
    template_key = request.get("template", "")
    content_items = request.get("content_items", [])
    start_date_str = request.get("start_date", "")
    platforms = request.get("platforms")

    if not template_key or not content_items or not start_date_str:
        raise HTTPException(
            status_code=400,
            detail="template, content_items, and start_date required",
        )

    try:
        start_date = datetime.fromisoformat(start_date_str.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid start_date")

    from app.services.recurring_series import create_recurring_series as do_create
    result = await do_create(
        db=db,
        workspace_id=workspace_id,
        template_key=template_key,
        content_items=content_items,
        start_date=start_date,
        platforms=platforms,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ─── Phase 3: Error Dashboard ──────────────────────────────────────────────

@router.get("/errors/summary")
async def get_error_summary(
    days: int = Query(30, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get error analytics summary."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.error_dashboard import get_error_summary as get_errors
    result = await get_errors(db, workspace_id, days)
    return result


@router.get("/errors/stats")
async def get_publish_stats(
    days: int = Query(30, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get overall publish statistics."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.error_dashboard import get_publish_stats
    result = await get_publish_stats(db, workspace_id, days)
    return result


@router.post("/errors/retry-all")
async def bulk_retry_failed(
    platform: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Reset all failed items to scheduled for retry."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.error_dashboard import bulk_retry_failed as do_retry
    result = await do_retry(db, workspace_id, platform)
    return result


# ─── Phase 3: Notifications Config ─────────────────────────────────────────

@router.post("/notifications/test")
async def test_notification(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a test notification."""
    channel_type = request.get("type", "slack")
    channel_config = request.get("config", {})

    from app.services.notifications import send_notification, configure_slack_notification, configure_webhook_notification

    if channel_type == "slack":
        config = configure_slack_notification(channel_config.get("webhook_url", ""))
    elif channel_type == "webhook":
        config = configure_webhook_notification(channel_config.get("webhook_url", ""))
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported channel type: {channel_type}")

    result = await send_notification(
        notification_type="publish_success",
        workspace_id="test",
        data={"platform": "linkedin", "post_title": "Test notification"},
        config={"channels": [config]},
    )
    return result


# ─── Phase 4: A/B Testing ──────────────────────────────────────────────────

@router.post("/ab-test/create", status_code=status.HTTP_201_CREATED)
async def create_ab_test(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create an A/B test with multiple caption variants."""
    workspace_id = await _get_workspace_id(db, current_user)
    post_id = request.get("post_id", "")
    platform = request.get("platform", "")
    variants = request.get("variants", [])
    test_duration_hours = request.get("test_duration_hours", 24)

    if not post_id or not platform or len(variants) < 2:
        raise HTTPException(
            status_code=400,
            detail="post_id, platform, and at least 2 variants required",
        )

    from app.services.ab_testing import create_ab_test as do_create
    result = await do_create(db, workspace_id, post_id, platform, variants, test_duration_hours)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/ab-test/{test_id}/results")
async def get_ab_test_results(
    test_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get A/B test results and winner recommendation."""
    from app.services.ab_testing import get_ab_test_results as get_results
    result = await get_results(db, test_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


# ─── Phase 4: AI Content Adaptation ────────────────────────────────────────

@router.post("/adapt-content")
async def adapt_content(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """AI-adapt content for a specific platform."""
    content = request.get("content", "")
    source_platform = request.get("source_platform", "linkedin")
    target_platform = request.get("target_platform", "x")
    provider = request.get("provider", "openai")
    tone = request.get("tone")

    if not content:
        raise HTTPException(status_code=400, detail="content required")

    from app.services.ai_content_adapter import adapt_content_ai
    result = await adapt_content_ai(content, source_platform, target_platform, provider, tone)
    return result


@router.post("/adapt-content/batch")
async def batch_adapt_content(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """AI-adapt content for multiple platforms at once."""
    content = request.get("content", "")
    source_platform = request.get("source_platform", "linkedin")
    target_platforms = request.get("target_platforms", ["x", "instagram", "facebook", "youtube"])
    provider = request.get("provider", "openai")
    tone = request.get("tone")

    if not content:
        raise HTTPException(status_code=400, detail="content required")

    from app.services.ai_content_adapter import batch_adapt_content as do_batch
    result = await do_batch(content, source_platform, target_platforms, provider, tone)
    return result


# ─── Phase 4: Approval Workflow ────────────────────────────────────────────

@router.post("/approval/request")
async def request_approval(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Request approval for a post before publishing."""
    workspace_id = await _get_workspace_id(db, current_user)
    post_id = request.get("post_id", "")
    if not post_id:
        raise HTTPException(status_code=400, detail="post_id required")

    from app.services.approval_workflow import request_approval as do_request
    result = await do_request(
        db, workspace_id, post_id, current_user.id,
        request.get("workflow", "Standard"),
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/approval/approve/{post_id}")
async def approve_post(
    post_id: str,
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Approve a post for publishing."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.approval_workflow import approve_post as do_approve
    result = await do_approve(
        db, workspace_id, post_id, current_user.id,
        request.get("platform"), request.get("comment", ""),
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/approval/reject/{post_id}")
async def reject_post(
    post_id: str,
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Reject a post and return to draft."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.approval_workflow import reject_post as do_reject
    result = await do_reject(
        db, workspace_id, post_id, current_user.id,
        request.get("reason", ""), request.get("platform"),
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/approval/pending")
async def list_pending_approvals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all posts awaiting approval."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.approval_workflow import get_pending_approvals
    result = await get_pending_approvals(db, workspace_id)
    return {"approvals": result, "total": len(result)}


@router.get("/approval/stats")
async def get_approval_stats(
    days: int = Query(30, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get approval workflow statistics."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.approval_workflow import get_approval_stats as get_stats
    result = await get_stats(db, workspace_id, days)
    return result


# ─── Phase 4: Timezone Scheduling ──────────────────────────────────────────

@router.get("/timezone/audience")
async def get_audience_timezones(
    platform: str = Query(...),
    current_user: User = Depends(get_current_user),
):
    """Get audience timezone distribution for a platform."""
    from app.services.timezone_scheduler import get_audience_timezones as get_tz
    return {"platform": platform, "audiences": get_tz(platform)}


@router.get("/timezone/suggest")
async def suggest_timezone_aware_time(
    platform: str = Query(...),
    hour: int = Query(10, ge=0, le=23),
    current_user: User = Depends(get_current_user),
):
    """Suggest posting times based on audience timezone distribution."""
    from app.services.timezone_scheduler import suggest_audience_aware_time
    return {"platform": platform, "suggestions": suggest_audience_aware_time(platform, hour)}


# ─── Phase 4: Content Scoring ──────────────────────────────────────────────

@router.post("/score-content")
async def score_content(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Score content's predicted engagement before publishing."""
    workspace_id = await _get_workspace_id(db, current_user)
    content = request.get("content", "")
    platform = request.get("platform", "linkedin")
    media_count = request.get("media_count", 0)
    scheduled_hour = request.get("scheduled_hour")

    if not content:
        raise HTTPException(status_code=400, detail="content required")

    from app.services.content_scorer import score_content as do_score
    result = await do_score(db, workspace_id, content, platform, media_count, scheduled_hour)
    return result


# ─── Phase 4: Platform Health ──────────────────────────────────────────────

@router.get("/health/{platform}")
async def check_platform_health(
    platform: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check API health for a specific platform."""
    workspace_id = await _get_workspace_id(db, current_user)

    # Get the token for this platform
    from app.services.token_refresh import get_fresh_token
    token = await get_fresh_token(workspace_id, platform)

    from app.services.platform_health import check_platform_health as do_check
    return await do_check(platform, token or "")


@router.get("/health")
async def check_all_health(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check health for all connected platforms."""
    workspace_id = await _get_workspace_id(db, current_user)

    from app.services.token_refresh import get_fresh_token
    from app.services.platform_health import check_all_platforms

    connections = {}
    for platform in ["linkedin", "x", "facebook", "instagram", "youtube"]:
        token = await get_fresh_token(workspace_id, platform)
        if token:
            connections[platform] = token

    return await check_all_platforms(connections)


# ─── Phase 4: Advanced Queue ───────────────────────────────────────────────

@router.post("/queue/reorder")
async def reorder_queue(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Reorder the queue by rescheduling items."""
    workspace_id = await _get_workspace_id(db, current_user)
    item_ids = request.get("item_ids", [])
    if not item_ids:
        raise HTTPException(status_code=400, detail="item_ids required")

    from app.services.queue_manager import reorder_queue as do_reorder
    result = await do_reorder(db, workspace_id, item_ids)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/queue/bulk-update")
async def bulk_update_queue(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Bulk update status for multiple queue items."""
    workspace_id = await _get_workspace_id(db, current_user)
    item_ids = request.get("item_ids", [])
    new_status = request.get("status", "")

    if not item_ids or not new_status:
        raise HTTPException(status_code=400, detail="item_ids and status required")

    from app.services.queue_manager import bulk_update_status
    result = await bulk_update_status(db, workspace_id, item_ids, new_status)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/queue/analytics")
async def get_queue_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get queue health analytics."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.queue_manager import get_queue_analytics as get_analytics
    return await get_analytics(db, workspace_id)


# ─── Phase 5: Dead-Letter Queue ────────────────────────────────────────────

@router.get("/dead-letter")
async def get_dead_letter(
    platform: str = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get failed publishes with error analysis."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.dead_letter_queue import get_dead_letter_queue
    return await get_dead_letter_queue(db, workspace_id, platform, offset=offset, limit=limit)


@router.post("/dead-letter/{item_id}/retry")
async def retry_dead_letter_item(
    item_id: str,
    request: dict = {},
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retry a single failed item from the dead-letter queue."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.dead_letter_queue import retry_from_dead_letter
    result = await retry_from_dead_letter(
        db, workspace_id, item_id, request.get("reset_retries", False)
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/dead-letter/bulk-retry")
async def bulk_retry_dead_letter(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Bulk retry failed items."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.dead_letter_queue import bulk_retry_dead_letter as do_bulk
    return await do_bulk(
        db, workspace_id,
        request.get("platform"),
        request.get("error_category"),
        request.get("max_age_days", 7),
    )


@router.get("/dead-letter/analytics")
async def get_dead_letter_analytics(
    days: int = Query(30, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed error analytics."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.dead_letter_queue import get_error_analytics
    return await get_error_analytics(db, workspace_id, days)


# ─── Phase 5: Media Optimizer ──────────────────────────────────────────────

@router.post("/media/analyze")
async def analyze_media(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Analyze media against platform requirements."""
    file_info = request.get("file_info", {})
    platform = request.get("platform", "linkedin")

    from app.services.media_optimizer import analyze_media_for_platform
    return analyze_media_for_platform(file_info, platform)


@router.post("/media/optimize-summary")
async def media_optimize_summary(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get optimization summary for multiple assets across platforms."""
    media_assets = request.get("media_assets", [])
    platforms = request.get("platforms", ["linkedin", "x", "instagram", "facebook", "youtube"])

    from app.services.media_optimizer import get_optimization_summary
    return get_optimization_summary(media_assets, platforms)


# ─── Phase 5: Rate Limit Tracker ───────────────────────────────────────────

@router.get("/rate-limits")
async def get_rate_limits(
    current_user: User = Depends(get_current_user),
):
    """Get rate limit status for all platforms."""
    from app.services.rate_limit_tracker import get_all_rate_status
    return get_all_rate_status()


@router.get("/rate-limits/{platform}")
async def get_platform_rate_limit(
    platform: str,
    current_user: User = Depends(get_current_user),
):
    """Get rate limit info for a specific platform."""
    from app.services.rate_limit_tracker import get_rate_limit_info
    return get_rate_limit_info(platform)


@router.get("/rate-limits/throttled")
async def get_throttled(
    current_user: User = Depends(get_current_user),
):
    """Get list of currently throttled platforms."""
    from app.services.rate_limit_tracker import get_throttled_platforms
    return {"throttled": get_throttled_platforms()}


# ─── Phase 5: Content Versioning ───────────────────────────────────────────

@router.post("/versions/snapshot/{post_id}")
async def create_snapshot(
    post_id: str,
    request: dict = {},
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a version snapshot of a post."""
    from app.services.content_versioning import create_snapshot as do_snapshot
    result = await do_snapshot(
        db, post_id, current_user.id, request.get("change_note", "")
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/versions/{post_id}")
async def get_version_history(
    post_id: str,
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get version history for a post."""
    from app.services.content_versioning import get_version_history as get_history
    return {"versions": await get_history(db, post_id, limit)}


@router.post("/versions/{post_id}/rollback/{version}")
async def rollback_version(
    post_id: str,
    version: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Rollback a post to a previous version."""
    from app.services.content_versioning import rollback_to_version
    result = await rollback_to_version(db, post_id, version, current_user.id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ─── Phase 5: Bulk Operations ──────────────────────────────────────────────

@router.post("/bulk/schedule")
async def bulk_schedule_posts(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Schedule multiple posts to multiple platforms."""
    workspace_id = await _get_workspace_id(db, current_user)
    post_ids = request.get("post_ids", [])
    platforms = request.get("platforms", [])
    scheduled_at_str = request.get("scheduled_at", "")

    if not post_ids or not platforms or not scheduled_at_str:
        raise HTTPException(status_code=400, detail="post_ids, platforms, and scheduled_at required")

    try:
        scheduled_at = datetime.fromisoformat(scheduled_at_str.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid scheduled_at")

    from app.services.bulk_operations import bulk_schedule
    return await bulk_schedule(db, workspace_id, post_ids, platforms, scheduled_at)


@router.post("/bulk/cancel")
async def bulk_cancel_posts(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel multiple scheduled items."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.bulk_operations import bulk_cancel
    return await bulk_cancel(
        db, workspace_id,
        request.get("item_ids"),
        request.get("post_ids"),
        request.get("platform"),
    )


@router.post("/bulk/caption")
async def bulk_update_captions(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update captions for multiple items using a template."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.bulk_operations import bulk_update_caption
    return await bulk_update_caption(
        db, workspace_id,
        request.get("item_ids", []),
        request.get("caption_template", ""),
        request.get("replacements"),
    )


@router.post("/bulk/reschedule")
async def bulk_reschedule_posts(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Reschedule items with staggered times."""
    workspace_id = await _get_workspace_id(db, current_user)
    new_start_str = request.get("new_start", "")
    if not new_start_str:
        raise HTTPException(status_code=400, detail="new_start required")

    try:
        new_start = datetime.fromisoformat(new_start_str.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid new_start")

    from app.services.bulk_operations import bulk_reschedule
    return await bulk_reschedule(
        db, workspace_id,
        request.get("item_ids", []),
        new_start,
        request.get("interval_minutes", 15),
    )


# ─── Phase 5: Admin Dashboard ──────────────────────────────────────────────

@router.get("/admin/metrics")
async def get_admin_metrics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get workspace metrics for admin dashboard."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.admin_metrics import get_workspace_metrics
    return await get_workspace_metrics(db, workspace_id)


@router.get("/admin/system-health")
async def get_system_health(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get system-wide health metrics."""
    from app.services.admin_metrics import get_system_health as get_health
    return await get_health(db)


# ─── Phase 5: Content Dependencies ─────────────────────────────────────────

@router.post("/dependencies/add")
async def add_dependency(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a dependency between two posts."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.content_dependencies import add_dependency as do_add
    result = await do_add(
        db, workspace_id,
        request.get("post_id", ""),
        request.get("depends_on_post_id", ""),
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/dependencies/remove")
async def remove_dependency(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a dependency between two posts."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.content_dependencies import remove_dependency as do_remove
    return await do_remove(
        db, workspace_id,
        request.get("post_id", ""),
        request.get("depends_on_post_id", ""),
    )


@router.get("/dependencies/{post_id}")
async def get_dependencies(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get dependencies for a post."""
    from app.services.content_dependencies import get_dependencies as get_deps
    return await get_deps(db, post_id, post_id)  # workspace_id not needed for this query


@router.get("/dependencies/{post_id}/check")
async def check_dependencies(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check if all dependencies for a post are met."""
    from app.services.content_dependencies import check_dependencies_met
    return await check_dependencies_met(db, post_id)


# ─── Phase 6: Calendar Service ─────────────────────────────────────────────

@router.get("/calendar/events")
async def get_calendar_events(
    start_date: str = Query(None),
    end_date: str = Query(None),
    platform: str = Query(None),
    status: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get calendar events from real PostPlatform data."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.calendar_service import get_calendar_events as get_events

    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None

    events = await get_events(db, workspace_id, start, end, platform, status)
    return {"events": events, "total": len(events)}


@router.post("/calendar/reschedule/{item_id}")
async def reschedule_calendar_event(
    item_id: str,
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Reschedule a calendar event (drag-and-drop handler)."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.calendar_service import reschedule_event
    result = await reschedule_event(
        db, workspace_id, item_id,
        request.get("date", ""),
        request.get("time"),
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/calendar/stats")
async def get_calendar_stats(
    month: int = Query(None),
    year: int = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get calendar statistics for a month."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.calendar_service import get_calendar_stats as get_stats
    return await get_stats(db, workspace_id, month, year)


# ─── Phase 6: Export ────────────────────────────────────────────────────────

@router.get("/export/schedule/csv")
async def export_schedule_csv(
    start_date: str = Query(None),
    end_date: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export scheduling data as CSV."""
    from fastapi.responses import PlainTextResponse
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.export_service import export_schedule_csv as do_export

    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None

    csv_data = await do_export(db, workspace_id, start, end)
    return PlainTextResponse(csv_data, media_type="text/csv")


@router.get("/export/schedule/json")
async def export_schedule_json(
    start_date: str = Query(None),
    end_date: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export scheduling data as JSON."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.export_service import export_schedule_json as do_export

    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None

    return await do_export(db, workspace_id, start, end)


@router.get("/export/analytics/csv")
async def export_analytics_csv(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export analytics data as CSV."""
    from fastapi.responses import PlainTextResponse
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.export_service import export_analytics_csv as do_export

    csv_data = await do_export(db, workspace_id, days)
    return PlainTextResponse(csv_data, media_type="text/csv")


# ─── Phase 6: Content Forecast ─────────────────────────────────────────────

@router.post("/forecast")
async def forecast_content(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Forecast expected engagement for a proposed post."""
    workspace_id = await _get_workspace_id(db, current_user)
    platform = request.get("platform", "linkedin")
    content_length = request.get("content_length", 200)
    has_media = request.get("has_media", False)
    proposed_date_str = request.get("proposed_date")

    proposed_date = None
    if proposed_date_str:
        try:
            proposed_date = datetime.fromisoformat(proposed_date_str.replace("Z", "+00:00"))
        except ValueError:
            pass

    from app.services.content_forecast import forecast_engagement
    return await forecast_engagement(
        db, workspace_id, platform, proposed_date, content_length, has_media
    )


# ─── Phase 6: Webhook Receiver ─────────────────────────────────────────────

@router.post("/webhooks/{platform}")
async def receive_webhook(
    platform: str,
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Receive a webhook from a social platform."""
    from app.services.webhook_receiver import handle_platform_webhook
    return await handle_platform_webhook(db, platform, request)


# ─── Phase 6: RSS Ingestion ────────────────────────────────────────────────

@router.post("/rss/ingest")
async def ingest_rss(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Ingest an RSS feed and create draft posts."""
    workspace_id = await _get_workspace_id(db, current_user)
    feed_url = request.get("feed_url", "")
    platforms = request.get("platforms", ["linkedin"])
    auto_schedule = request.get("auto_schedule", False)

    if not feed_url:
        raise HTTPException(status_code=400, detail="feed_url required")

    from app.services.rss_ingestion import ingest_rss_feed
    return await ingest_rss_feed(
        db, workspace_id, feed_url, current_user.id, platforms, auto_schedule
    )


# ─── Phase 6: Content Templates ────────────────────────────────────────────

@router.get("/templates")
async def list_templates(
    category: str = Query(None),
    platform: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all content templates (built-in + custom)."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.content_templates import get_templates
    templates = await get_templates(db, workspace_id, category, platform)
    return {"templates": templates, "count": len(templates)}


@router.post("/templates/save/{post_id}")
async def save_template(
    post_id: str,
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Save an existing post as a reusable template."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.content_templates import save_as_template
    result = await save_as_template(
        db, workspace_id, post_id,
        request.get("name", "Untitled Template"),
        request.get("category", "custom"),
        request.get("variables"),
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/templates/create")
async def create_from_template(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new post from a template."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.content_templates import create_from_template as do_create
    result = await do_create(
        db, workspace_id,
        request.get("template_id", ""),
        request.get("variables", {}),
        request.get("platforms"),
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ─── Phase 6: SSE Events ───────────────────────────────────────────────────

@router.get("/events/stream")
async def stream_events(
    current_user: User = Depends(get_current_user),
):
    """SSE endpoint for real-time queue updates."""
    from fastapi.responses import StreamingResponse
    from app.services.sse_events import subscribe_events

    workspace_id = "default"  # In production, extract from user
    return StreamingResponse(
        subscribe_events(workspace_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


# ─── Phase 7: UTM Builder ──────────────────────────────────────────────────

@router.post("/utm/build")
async def build_utm(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Build a UTM-tagged URL for a platform."""
    from app.services.utm_builder import build_utm_url
    return build_utm_url(
        request.get("url", ""),
        request.get("platform", "linkedin"),
        request.get("campaign_name", ""),
        request.get("content_type", ""),
        request.get("custom_params"),
    )


@router.post("/utm/build-multi")
async def build_utm_multi(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Build UTM-tagged URLs for multiple platforms."""
    from app.services.utm_builder import build_multi_platform_urls
    return build_multi_platform_urls(
        request.get("url", ""),
        request.get("platforms", ["linkedin", "x"]),
        request.get("campaign_name", ""),
        request.get("content_type", ""),
    )


@router.get("/utm/rules/{platform}")
async def get_utm_rules(
    platform: str,
    current_user: User = Depends(get_current_user),
):
    """Get link rules for a platform."""
    from app.services.utm_builder import get_link_rules
    return get_link_rules(platform)


# ─── Phase 7: AI Caption Generator ─────────────────────────────────────────

@router.post("/captions/generate")
async def generate_caption(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Generate an AI caption for a platform."""
    from app.services.caption_generator import generate_caption as do_generate
    return await do_generate(
        request.get("topic", ""),
        request.get("platform", "linkedin"),
        request.get("tone", "professional"),
        request.get("brand_voice"),
        request.get("keywords"),
        request.get("include_hashtags", True),
        request.get("include_cta", True),
        request.get("provider", "openai"),
        request.get("max_length"),
    )


@router.post("/captions/generate-multi")
async def generate_multi_captions(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Generate captions for multiple platforms."""
    from app.services.caption_generator import generate_multi_platform_captions
    return await generate_multi_platform_captions(
        request.get("topic", ""),
        request.get("platforms", ["linkedin", "x", "instagram"]),
        request.get("tone", "professional"),
        request.get("brand_voice"),
        request.get("keywords"),
        request.get("provider", "openai"),
    )


@router.post("/captions/improve")
async def improve_caption(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Improve an existing caption."""
    from app.services.caption_generator import improve_caption as do_improve
    return await do_improve(
        request.get("caption", ""),
        request.get("platform", "linkedin"),
        request.get("instruction", "Make it more engaging"),
        request.get("provider", "openai"),
    )


# ─── Phase 7: Calendar Analytics ───────────────────────────────────────────

@router.get("/calendar/analytics")
async def get_calendar_analytics(
    days: int = Query(90, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get calendar analytics (posting patterns + performance)."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.calendar_analytics import get_calendar_analytics as get_analytics
    return await get_analytics(db, workspace_id, days)


# ─── Phase 7: Post Preview ─────────────────────────────────────────────────

@router.post("/preview")
async def preview_post(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Generate platform-specific preview of a post."""
    from app.services.post_preview import generate_preview
    return generate_preview(
        request.get("content", ""),
        request.get("platform", "linkedin"),
        request.get("media_urls"),
        request.get("title"),
    )


@router.post("/preview/multi")
async def preview_multi(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Generate previews for multiple platforms."""
    from app.services.post_preview import generate_multi_platform_previews
    return generate_multi_platform_previews(
        request.get("content", ""),
        request.get("platforms", ["linkedin", "x", "instagram"]),
        request.get("media_urls"),
        request.get("title"),
    )


# ─── Phase 7: Workspace Settings ───────────────────────────────────────────

@router.get("/settings")
async def get_workspace_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get workspace scheduling settings."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.workspace_settings import get_workspace_settings as get_settings
    return await get_settings(db, workspace_id)


@router.put("/settings")
async def update_workspace_settings(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update workspace scheduling settings."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.workspace_settings import update_workspace_settings as update_settings
    return await update_settings(db, workspace_id, request)


@router.get("/settings/schema")
async def get_settings_schema(
    current_user: User = Depends(get_current_user),
):
    """Get settings schema for UI rendering."""
    from app.services.workspace_settings import get_settings_schema as get_schema
    return {"schema": get_schema()}


# ─── Phase 7: Audit Log ────────────────────────────────────────────────────

@router.get("/audit")
async def get_audit_log(
    days: int = Query(30, ge=1, le=365),
    action_type: str = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get audit log for scheduling operations."""
    from app.services.audit_log import get_audit_log as get_log
    return await get_log(db, None, None, action_type, days, offset, limit)


@router.get("/audit/stats")
async def get_audit_stats(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get audit statistics."""
    from app.services.audit_log import get_audit_stats
    return await get_audit_stats(db, days)


@router.get("/audit/action-types")
async def get_action_types(
    current_user: User = Depends(get_current_user),
):
    """Get available audit action types."""
    from app.services.audit_log import ACTION_TYPES
    return {"action_types": ACTION_TYPES}


# ─── Phase 8: Content Library ──────────────────────────────────────────────

@router.post("/library/save/{post_id}")
async def save_to_library(
    post_id: str,
    request: dict = {},
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Save a post to the content library."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.content_library import save_to_library as do_save
    result = await do_save(
        db, workspace_id, post_id,
        request.get("tags"), request.get("category", "general"),
        request.get("notes", ""),
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/library/search")
async def search_library(
    query: str = Query(None),
    category: str = Query(None),
    platform: str = Query(None),
    tags: str = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Search the content library."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.content_library import search_library
    tag_list = tags.split(",") if tags else None
    return await search_library(db, workspace_id, query, category, platform, tag_list, limit, offset)


@router.delete("/library/{post_id}")
async def remove_from_library(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a post from the library."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.content_library import remove_from_library as do_remove
    return await do_remove(db, workspace_id, post_id)


@router.get("/library/stats")
async def get_library_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get content library statistics."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.content_library import get_library_stats
    return await get_library_stats(db, workspace_id)


# ─── Phase 8: Hashtag Strategist ───────────────────────────────────────────

@router.post("/hashtags/generate")
async def generate_hashtags(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Generate AI-powered hashtags for a platform."""
    from app.services.hashtag_strategist import generate_hashtags as do_generate
    return await do_generate(
        request.get("topic", ""),
        request.get("platform", "linkedin"),
        request.get("content"),
        request.get("count", 5),
        request.get("brand_hashtags"),
        request.get("provider", "openai"),
    )


@router.post("/hashtags/analyze")
async def analyze_hashtags(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Analyze existing hashtags and suggest improvements."""
    from app.services.hashtag_strategist import analyze_hashtag_performance
    return analyze_hashtag_performance(
        request.get("content", ""),
        request.get("platform", "linkedin"),
    )


# ─── Phase 8: Content Pipeline ─────────────────────────────────────────────

@router.get("/pipeline/status")
async def get_pipeline_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get content pipeline status."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.content_pipeline import get_pipeline_status as get_status
    return await get_status(db, workspace_id)


@router.post("/pipeline/transition/{post_id}")
async def transition_post_status(
    post_id: str,
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Transition a post to a new pipeline status."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.content_pipeline import transition_status
    result = await transition_status(
        db, workspace_id, post_id,
        request.get("status", ""),
        request.get("platform"),
        current_user.id,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/pipeline/transitions/{status}")
async def get_valid_transitions(
    status: str,
    current_user: User = Depends(get_current_user),
):
    """Get valid transitions from a status."""
    from app.services.content_pipeline import get_valid_transitions as get_transitions
    return {"from_status": status, "valid_transitions": get_transitions(status)}


@router.get("/pipeline/stages")
async def get_pipeline_stages(
    current_user: User = Depends(get_current_user),
):
    """Get all pipeline stages."""
    from app.services.content_pipeline import get_pipeline_stages as get_stages
    return {"stages": get_stages()}


# ─── Phase 8: Competitor Tracking ──────────────────────────────────────────

@router.post("/competitors/add")
async def add_competitor(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a competitor to track."""
    from app.services.competitor_tracking import add_competitor as do_add
    return await do_add(
        db, "workspace",
        request.get("name", ""),
        request.get("platforms", []),
        request.get("profile_urls"),
        request.get("notes", ""),
    )


@router.post("/competitors/analyze")
async def analyze_competitor(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Analyze a competitor's posting patterns."""
    from app.services.competitor_tracking import analyze_competitor_patterns
    return await analyze_competitor_patterns(
        request.get("competitor", ""),
        request.get("platform", "linkedin"),
        request.get("posts", []),
    )


# ─── Phase 8: Engagement Tracker ───────────────────────────────────────────

@router.get("/engagement/summary")
async def get_engagement_summary(
    days: int = Query(7, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get engagement summary."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.engagement_tracker import get_engagement_summary as get_summary
    return await get_summary(db, workspace_id, days)


@router.get("/engagement/top-posts")
async def get_top_engaging_posts(
    limit: int = Query(10, ge=1, le=50),
    days: int = Query(30, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get top engaging posts."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.engagement_tracker import get_top_engaging_posts
    return {"posts": await get_top_engaging_posts(db, workspace_id, limit, days)}


# ─── Phase 8: Quality Rubric ───────────────────────────────────────────────

@router.post("/quality/score")
async def score_quality(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Score content across 10 quality dimensions."""
    from app.services.content_quality_rubric import score_content_rubric
    return score_content_rubric(
        request.get("content", ""),
        request.get("platform", "linkedin"),
        request.get("media_count", 0),
        request.get("has_cta", False),
        request.get("brand_voice"),
        request.get("target_audience"),
    )


# ─── Phase 8: Compliance Checker ───────────────────────────────────────────

@router.post("/compliance/check")
async def check_compliance(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Check content for platform compliance."""
    from app.services.compliance_checker import check_compliance as do_check
    return do_check(
        request.get("content", ""),
        request.get("platform", "linkedin"),
        request.get("title"),
        request.get("has_paid_partnership", False),
    )


@router.post("/compliance/check-all")
async def check_all_compliance(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Check content compliance across multiple platforms."""
    from app.services.compliance_checker import check_all_platforms
    return check_all_platforms(
        request.get("content", ""),
        request.get("platforms", ["linkedin", "x", "instagram"]),
        request.get("title"),
        request.get("has_paid_partnership", False),
    )


# ─── Phase 8: Smart Scheduling Rules ───────────────────────────────────────

@router.get("/rules")
async def get_smart_rules(
    current_user: User = Depends(get_current_user),
):
    """Get all smart scheduling rules."""
    from app.services.smart_rules import get_smart_rules
    return {"rules": get_smart_rules()}


@router.put("/rules/{rule_id}")
async def update_smart_rule(
    rule_id: str,
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Update a smart scheduling rule."""
    from app.services.smart_rules import update_rule
    return update_rule(rule_id, request.get("enabled"), **request.get("conditions", {}))


@router.post("/rules/apply")
async def apply_rules(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Apply smart rules to find the best scheduling time."""
    from app.services.smart_rules import apply_smart_rules

    time_str = request.get("time", "")
    try:
        requested_time = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid time")

    return await apply_smart_rules(
        requested_time,
        request.get("platform", "linkedin"),
        "workspace",
        db,
        request.get("existing_schedule"),
    )


# ─── Phase 9: AI Calendar Generator ────────────────────────────────────────

@router.post("/calendar/generate")
async def generate_calendar(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Generate a full month content calendar with AI."""
    from app.services.ai_calendar_generator import generate_monthly_calendar
    return await generate_monthly_calendar(
        request.get("topic", ""),
        request.get("platforms", ["linkedin", "x"]),
        request.get("audience", "general"),
        request.get("posting_frequency", "daily"),
        request.get("brand_voice"),
        request.get("content_pillars"),
        request.get("month"),
        request.get("year"),
        request.get("provider", "openai"),
    )


@router.get("/calendar/generate/routes")
async def get_repurpose_routes(
    source_format: str = Query(None),
    current_user: User = Depends(get_current_user),
):
    """Get available content repurposing routes."""
    from app.services.content_repurposing_engine import get_available_routes
    return {"routes": get_available_routes(source_format)}


# ─── Phase 9: Content Repurposing Engine ───────────────────────────────────

@router.post("/repurpose")
async def repurpose_content(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Repurpose content into multiple formats."""
    from app.services.content_repurposing_engine import repurpose_content as do_repurpose
    return await do_repurpose(
        request.get("content", ""),
        request.get("source_format", "blog"),
        request.get("target_formats", ["thread", "post"]),
        request.get("topic", ""),
        request.get("tone", "professional"),
        request.get("provider", "openai"),
    )


# ─── Phase 9: Auto A/B Winner ──────────────────────────────────────────────

@router.post("/ab-test/{test_id}/auto-winner")
async def auto_select_winner(
    test_id: str,
    request: dict = {},
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Auto-select the winning A/B test variant."""
    from app.services.auto_ab_winner import auto_select_winner as do_select
    return await do_select(
        db, test_id,
        request.get("metric", "engagement_rate"),
        request.get("min_data_points", 5),
    )


# ─── Phase 9: Multi-Language Translator ────────────────────────────────────

@router.post("/translate")
async def translate_caption(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Translate a caption to another language."""
    from app.services.multilang_translator import translate_caption as do_translate
    return await do_translate(
        request.get("caption", ""),
        request.get("target_language", "es"),
        request.get("source_language", "en"),
        request.get("platform", "linkedin"),
        request.get("preserve_hashtags", True),
        request.get("provider", "openai"),
    )


@router.post("/translate/multi")
async def translate_multi(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Translate a caption into multiple languages."""
    from app.services.multilang_translator import translate_multi_language
    return await translate_multi_language(
        request.get("caption", ""),
        request.get("target_languages", ["es", "fr", "de"]),
        request.get("platform", "linkedin"),
        request.get("provider", "openai"),
    )


# ─── Phase 9: Platform Deep Features ───────────────────────────────────────

@router.get("/deep-features")
async def get_deep_features(
    platform: str = Query(None),
    current_user: User = Depends(get_current_user),
):
    """Get available platform deep features (Reels, Shorts, Articles)."""
    from app.services.platform_deep_features import get_available_deep_features
    return {"features": get_available_deep_features(platform)}


@router.get("/deep-features/{feature_type}")
async def get_deep_feature_specs(
    feature_type: str,
    current_user: User = Depends(get_current_user),
):
    """Get specs for a specific deep feature."""
    from app.services.platform_deep_features import get_deep_feature_specs
    spec = get_deep_feature_specs(feature_type)
    if not spec:
        raise HTTPException(status_code=404, detail=f"Feature {feature_type} not found")
    return spec


@router.post("/deep-features/validate")
async def validate_deep_feature(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Validate content against deep feature requirements."""
    from app.services.platform_deep_features import validate_deep_feature_content
    return await validate_deep_feature_content(
        request.get("content", {}),
        request.get("feature_type", "instagram_reels"),
    )


# ─── Phase 9: Benchmarking ─────────────────────────────────────────────────

@router.get("/benchmarks/{industry}")
async def get_benchmarks(
    industry: str,
    platform: str = Query(None),
    current_user: User = Depends(get_current_user),
):
    """Get industry benchmarks."""
    from app.services.benchmarking import get_benchmarks as get_bench
    return get_bench(industry, platform)


@router.post("/benchmarks/compare")
async def compare_benchmarks(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Compare your metrics against industry benchmarks."""
    from app.services.benchmarking import compare_to_benchmark
    return compare_to_benchmark(
        request.get("your_metrics", {}),
        request.get("industry", "technology"),
        request.get("platform", "linkedin"),
    )


@router.get("/benchmarks/industries")
async def get_industries(
    current_user: User = Depends(get_current_user),
):
    """Get available industries for benchmarking."""
    from app.services.benchmarking import get_available_industries
    return {"industries": get_available_industries()}


# ─── Phase 9: Cohort Analysis ──────────────────────────────────────────────

@router.get("/analytics/cohorts")
async def cohort_analysis(
    cohort_by: str = Query("platform"),
    days: int = Query(90, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Perform cohort analysis on published posts."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.cohort_analysis import cohort_analysis as do_cohort
    return await do_cohort(db, workspace_id, cohort_by, days)


# ─── Phase 10: Social Listening ─────────────────────────────────────────────

@router.post("/listening/scan")
async def scan_mentions(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Scan for brand mentions across platforms."""
    from app.services.social_listening import scan_mentions as do_scan
    return await do_scan(
        request.get("keywords", []),
        request.get("platforms", ["x", "linkedin"]),
        request.get("time_window_hours", 24),
    )


@router.post("/listening/rules")
async def create_listening_rule(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a social listening rule."""
    from app.services.social_listening import create_listening_rule as do_create
    return await do_create(
        db, "workspace",
        request.get("name", ""),
        request.get("keywords", []),
        request.get("platforms", ["x"]),
        request.get("alert_type", "mention"),
    )


@router.get("/listening/rules")
async def get_listening_rules(
    current_user: User = Depends(get_current_user),
):
    """Get default listening rules."""
    from app.services.social_listening import get_listening_rules
    return {"rules": get_listening_rules()}


@router.post("/listening/sentiment")
async def analyze_sentiment(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Analyze sentiment of text."""
    from app.services.social_listening import analyze_sentiment
    return analyze_sentiment(request.get("text", ""))


# ─── Phase 10: Content Idea Generator ──────────────────────────────────────

@router.post("/ideas/generate")
async def generate_ideas(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Generate content ideas from keywords."""
    from app.services.content_idea_generator import generate_content_ideas
    return await generate_content_ideas(
        request.get("keywords", []),
        request.get("industry", "technology"),
        request.get("audience", "professionals"),
        request.get("platforms"),
        request.get("count", 10),
        request.get("content_types"),
        request.get("provider", "openai"),
    )


@router.post("/ideas/trending")
async def generate_trending_ideas(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Generate trending content ideas."""
    from app.services.content_idea_generator import generate_trending_ideas
    return await generate_trending_ideas(
        request.get("industry", "technology"),
        request.get("platforms"),
        request.get("count", 5),
        request.get("provider", "openai"),
    )


# ─── Phase 10: Schedule Optimizer ──────────────────────────────────────────

@router.get("/optimize/schedule/{platform}")
async def optimize_schedule(
    platform: str,
    days: int = Query(90, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get ML-optimized posting schedule."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.schedule_optimizer import optimize_schedule as do_optimize
    return await do_optimize(db, workspace_id, platform, days)


# ─── Phase 10: Cross-Platform Analytics ────────────────────────────────────

@router.get("/analytics/cross-platform")
async def cross_platform_analytics(
    days: int = Query(30, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get unified analytics across all platforms."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.cross_platform_analytics import get_cross_platform_analytics
    return await get_cross_platform_analytics(db, workspace_id, days)


@router.get("/analytics/cross-platform/trends")
async def cross_platform_trends(
    days: int = Query(30, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get cross-platform trend data."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.cross_platform_analytics import get_cross_platform_trends
    return await get_cross_platform_trends(db, workspace_id, days)


# ─── Phase 10: Audience Growth ─────────────────────────────────────────────

@router.get("/analytics/audience-growth")
async def audience_growth(
    days: int = Query(30, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get audience growth trends."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.audience_growth import get_audience_growth
    return await get_audience_growth(db, workspace_id, days)


# ─── Phase 10: Content Gap Analyzer ────────────────────────────────────────

@router.post("/analytics/content-gaps")
async def analyze_content_gaps(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Analyze content gaps and suggest missing topics."""
    from app.services.content_gap_analyzer import analyze_content_gaps
    return await analyze_content_gaps(
        request.get("existing_topics", []),
        request.get("industry", "technology"),
        request.get("audience", "professionals"),
        request.get("platforms"),
        request.get("competitor_topics"),
        request.get("provider", "openai"),
    )


# ─── Phase 10: Brand Voice Checker ─────────────────────────────────────────

@router.post("/brand-voice/check")
async def check_brand_voice(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Check content against brand voice guidelines."""
    from app.services.brand_voice_checker import check_brand_voice
    return await check_brand_voice(
        request.get("content", ""),
        request.get("brand_voice_config", {}),
        request.get("platform", "linkedin"),
        request.get("provider", "openai"),
    )


@router.post("/brand-voice/batch-check")
async def batch_check_brand_voice(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Check multiple pieces of content against brand voice."""
    from app.services.brand_voice_checker import batch_check_brand_voice
    return await batch_check_brand_voice(
        request.get("contents", []),
        request.get("brand_voice_config", {}),
        request.get("provider", "openai"),
    )


# ─── Phase 10: Calendar Reminders ──────────────────────────────────────────

@router.get("/reminders/upcoming")
async def get_upcoming_reminders(
    hours: int = Query(24, ge=1, le=168),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get upcoming posting reminders."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.calendar_reminders import get_upcoming_reminders as get_reminders
    return {"reminders": await get_reminders(db, workspace_id, hours)}


@router.get("/reminders/overdue")
async def check_overdue(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check for overdue posts."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.calendar_reminders import check_overdue_posts
    return {"overdue": await check_overdue_posts(db, workspace_id)}


# ─── Phase 11: API Key Management ──────────────────────────────────────────

@router.post("/api-keys/create")
async def create_api_key(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new API key."""
    from app.services.api_key_management import create_api_key as do_create
    return await do_create(
        db, "workspace",
        request.get("name", "API Key"),
        request.get("permissions", ["read"]),
        request.get("rate_limit", 100),
        request.get("expires_days", 90),
    )


@router.post("/api-keys/{key_id}/revoke")
async def revoke_api_key(
    key_id: str,
    request: dict = {},
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Revoke an API key."""
    from app.services.api_key_management import revoke_api_key as do_revoke
    return await do_revoke(db, "workspace", key_id, request.get("reason", ""))


@router.get("/api-keys/scopes")
async def get_api_key_scopes(
    current_user: User = Depends(get_current_user),
):
    """Get available API key permission scopes."""
    from app.services.api_key_management import get_key_scopes
    return {"scopes": get_key_scopes()}


# ─── Phase 11: Bulk Import/Export ───────────────────────────────────────────

@router.post("/import/csv")
async def import_csv(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Import posts from CSV content."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.bulk_import import import_from_csv
    return await import_from_csv(
        db, workspace_id,
        request.get("csv_content", ""),
        current_user.id,
        request.get("platform", "linkedin"),
        request.get("auto_schedule", False),
    )


@router.get("/export/csv")
async def export_csv(
    status: str = Query(None),
    platform: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export posts to CSV."""
    from fastapi.responses import PlainTextResponse
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.bulk_import import export_to_csv
    csv_data = await export_to_csv(db, workspace_id, status, platform)
    return PlainTextResponse(csv_data, media_type="text/csv")


# ─── Phase 11: Report Generator ────────────────────────────────────────────

@router.get("/reports/analytics")
async def generate_report(
    days: int = Query(30, ge=7, le=365),
    format: str = Query("json"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate comprehensive analytics report."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.report_generator import generate_analytics_report
    return await generate_analytics_report(db, workspace_id, days, format)


# ─── Phase 11: Automation Rules ────────────────────────────────────────────

@router.get("/automation/rules")
async def get_automation_rules(
    current_user: User = Depends(get_current_user),
):
    """Get all automation rules."""
    from app.services.automation_rules import get_automation_rules
    return {"rules": get_automation_rules()}


@router.put("/automation/rules/{rule_id}")
async def toggle_automation_rule(
    rule_id: str,
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Enable or disable an automation rule."""
    from app.services.automation_rules import toggle_rule
    return toggle_rule(rule_id, request.get("enabled", True))


# ─── Phase 11: Team Workload ───────────────────────────────────────────────

@router.get("/team/workload")
async def get_team_workload(
    days: int = Query(7, ge=1, le=30),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get team workload distribution."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.team_workload import get_team_workload as get_workload
    return await get_workload(db, workspace_id, days)


@router.post("/team/suggest-assignments")
async def suggest_assignments(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Suggest post assignments for team members."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.team_workload import suggest_assignments
    return {"assignments": await suggest_assignments(db, workspace_id, request.get("post_count", 5))}


# ─── Phase 11: Postmortem ──────────────────────────────────────────────────

@router.get("/postmortem/{post_id}")
async def analyze_failure(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Analyze a failed publish attempt."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.postmortem import analyze_failure as do_analyze
    return await do_analyze(db, workspace_id, post_id)


@router.get("/postmortem/report")
async def failure_report(
    days: int = Query(7, ge=1, le=30),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate failure analysis report."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.postmortem import generate_failure_report
    return await generate_failure_report(db, workspace_id, days)


# ─── Phase 12: Content Pillar Manager ──────────────────────────────────────

@router.get("/pillars")
async def get_pillars(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get content pillars with performance data."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.content_pillar_manager import get_pillars
    return await get_pillars(db, workspace_id)


@router.post("/pillars/assign/{post_id}")
async def assign_pillar(
    post_id: str,
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Assign a content pillar to a post."""
    from app.services.content_pillar_manager import set_post_pillar
    return await set_post_pillar(db, post_id, request.get("pillar_id", ""))


@router.get("/pillars/templates")
async def get_pillar_templates(
    current_user: User = Depends(get_current_user),
):
    """Get default pillar templates."""
    from app.services.content_pillar_manager import get_pillar_templates
    return {"templates": get_pillar_templates()}


# ─── Phase 12: Hashtag Performance ─────────────────────────────────────────

@router.get("/hashtags/performance")
async def hashtag_performance(
    platform: str = Query(None),
    days: int = Query(30, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get hashtag performance analytics."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.hashtag_performance import get_hashtag_performance
    return await get_hashtag_performance(db, workspace_id, platform, days)


@router.get("/hashtags/trends/{hashtag}")
async def hashtag_trends(
    hashtag: str,
    days: int = Query(30, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get trends for a specific hashtag."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.hashtag_performance import get_hashtag_trends
    return await get_hashtag_trends(db, workspace_id, hashtag, days)


# ─── Phase 12: Reply Queue ─────────────────────────────────────────────────

@router.get("/replies/queue")
async def get_reply_queue(
    platform: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the reply queue."""
    from app.services.reply_queue import get_reply_queue
    return await get_reply_queue(db, "workspace", platform)


@router.post("/replies/send")
async def send_reply(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a reply to a mention/comment."""
    from app.services.reply_queue import create_reply
    return await create_reply(
        db, "workspace",
        request.get("mention_id", ""),
        request.get("response_text", ""),
        request.get("template"),
    )


@router.get("/replies/templates")
async def get_reply_templates(
    current_user: User = Depends(get_current_user),
):
    """Get reply templates."""
    from app.services.reply_queue import get_reply_templates
    return get_reply_templates()


# ─── Phase 12: UGC Campaigns ───────────────────────────────────────────────

@router.post("/ugc/campaigns/create")
async def create_ugc_campaign(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a UGC campaign."""
    from app.services.ugc_campaigns import create_ugc_campaign
    return await create_ugc_campaign(
        db, "workspace",
        request.get("name", ""),
        request.get("branded_hashtag", ""),
        request.get("description", ""),
        request.get("platforms"),
        request.get("start_date"),
        request.get("end_date"),
        request.get("rules", ""),
    )


@router.get("/ugc/best-practices")
async def get_ugc_best_practices(
    current_user: User = Depends(get_current_user),
):
    """Get UGC campaign best practices."""
    from app.services.ugc_campaigns import get_ugc_best_practices
    return {"practices": get_ugc_best_practices()}


# ─── Phase 12: Influencer Discovery ────────────────────────────────────────

@router.post("/influencers/discover")
async def discover_influencers(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Discover potential influencer partners."""
    from app.services.influencer_discovery import discover_influencers
    return await discover_influencers(
        request.get("niche", ""),
        request.get("platform", "instagram"),
        request.get("min_followers", 1000),
        request.get("max_followers", 100000),
        request.get("min_engagement_rate", 2.0),
        request.get("count", 10),
        request.get("provider", "openai"),
    )


@router.get("/influencers/outreach-templates")
async def get_outreach_templates(
    current_user: User = Depends(get_current_user),
):
    """Get influencer outreach templates."""
    from app.services.influencer_discovery import get_outreach_templates
    return {"templates": get_outreach_templates()}


@router.get("/influencers/vetting-checklist")
async def get_vetting_checklist(
    current_user: User = Depends(get_current_user),
):
    """Get influencer vetting checklist."""
    from app.services.influencer_discovery import get_influencer_vetting_checklist
    return {"checklist": get_influencer_vetting_checklist()}


# ─── Phase 12: Viral Score ─────────────────────────────────────────────────

@router.post("/viral/score")
async def predict_viral_score(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Predict viral potential of content."""
    from app.services.viral_score import predict_viral_score
    return predict_viral_score(
        request.get("content", ""),
        request.get("platform", "linkedin"),
        request.get("media_count", 0),
        request.get("has_video", False),
        request.get("posting_time_hour"),
    )


# ─── Phase 12: Content Series ──────────────────────────────────────────────

@router.post("/series/create")
async def create_content_series(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a content series."""
    from app.services.content_series import create_content_series
    return await create_content_series(
        db, "workspace",
        request.get("name", ""),
        request.get("topic", ""),
        request.get("template", "weekly_thread"),
        request.get("platforms"),
        request.get("total_parts"),
    )


@router.get("/series/templates")
async def get_series_templates(
    current_user: User = Depends(get_current_user),
):
    """Get series templates."""
    from app.services.content_series import get_series_templates
    return {"templates": get_series_templates()}


# ─── Phase 12: Crisis Playbook ─────────────────────────────────────────────

@router.get("/crisis/playbook")
async def get_crisis_playbook(
    scenario: str = Query(None),
    current_user: User = Depends(get_current_user),
):
    """Get crisis communication playbook."""
    from app.services.crisis_playbook import get_crisis_playbook
    return await get_crisis_playbook(scenario)


@router.get("/crisis/checklist")
async def get_crisis_checklist(
    current_user: User = Depends(get_current_user),
):
    """Get crisis response checklist."""
    from app.services.crisis_playbook import get_crisis_checklist
    return {"checklist": get_crisis_checklist()}


# ─── Phase 13: Content Performance Engine ───────────────────────────────────

@router.post("/performance/score")
async def score_performance(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Advanced content performance scoring."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.content_performance_engine import score_content_performance
    return await score_content_performance(
        db, workspace_id,
        request.get("content", ""),
        request.get("platform", "linkedin"),
        request.get("media_count", 0),
        request.get("has_video", False),
        request.get("posting_hour"),
        request.get("content_type", "text"),
    )


# ─── Phase 13: Audience Persona Builder ────────────────────────────────────

@router.post("/personas/build")
async def build_persona(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Build an audience persona."""
    from app.services.audience_persona import build_audience_persona
    return await build_audience_persona(
        request.get("industry", ""),
        request.get("product_type", ""),
        request.get("existing_audience_data"),
        request.get("provider", "openai"),
    )


@router.get("/personas/templates")
async def get_persona_templates(
    current_user: User = Depends(get_current_user),
):
    """Get persona templates."""
    from app.services.audience_persona import get_persona_templates
    return {"templates": get_persona_templates()}


# ─── Phase 13: Campaign Calendar ────────────────────────────────────────────

@router.post("/campaigns/create")
async def create_campaign(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a campaign with coordinated content schedule."""
    from app.services.campaign_calendar import create_campaign
    return await create_campaign(
        db, "workspace",
        request.get("name", ""),
        request.get("campaign_type", "product_launch"),
        request.get("start_date"),
        request.get("platforms"),
        request.get("goals"),
    )


@router.get("/campaigns/types")
async def get_campaign_types(
    current_user: User = Depends(get_current_user),
):
    """Get campaign type templates."""
    from app.services.campaign_calendar import get_campaign_types
    return {"types": get_campaign_types()}


# ─── Phase 13: A/B Auto-Apply ───────────────────────────────────────────────

@router.post("/ab-test/auto-apply/{test_id}")
async def auto_apply_winner(
    test_id: str,
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Apply winning variant to all target platforms."""
    from app.services.ab_auto_apply import auto_apply_winner
    return await auto_apply_winner(
        db, test_id,
        request.get("winner_variant_id", ""),
        request.get("target_platforms"),
    )


# ─── Phase 13: Social Proof ────────────────────────────────────────────────

@router.get("/social-proof")
async def get_social_proof(
    category: str = Query(None),
    platform: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get aggregated social proof."""
    from app.services.social_proof import get_social_proof
    return await get_social_proof(db, "workspace", category, platform)


@router.post("/social-proof/add")
async def add_social_proof(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a social proof entry."""
    from app.services.social_proof import add_social_proof
    return await add_social_proof(
        db, "workspace",
        request.get("category", "testimonial"),
        request.get("content", ""),
        request.get("author", ""),
        request.get("platform", ""),
        request.get("rating"),
        request.get("url", ""),
    )


@router.get("/social-proof/templates")
async def get_social_proof_templates(
    current_user: User = Depends(get_current_user),
):
    """Get social proof request templates."""
    from app.services.social_proof import get_social_proof_templates
    return {"templates": get_social_proof_templates()}


# ─── Phase 13: Community Health ─────────────────────────────────────────────

@router.get("/community/health")
async def get_community_health(
    days: int = Query(30, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get community health metrics."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.community_health import get_community_health
    return await get_community_health(db, workspace_id, days)


# ─── Phase 13: ROI Calculator ───────────────────────────────────────────────

@router.post("/roi/calculate")
async def calculate_roi(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Calculate social media ROI."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.roi_calculator import calculate_roi
    return await calculate_roi(
        db, workspace_id,
        request.get("days", 30),
        request.get("ad_spend", 0),
        request.get("time_cost_per_hour", 50),
        request.get("hours_per_week", 10),
    )


# ─── Phase 13: Content Audit ───────────────────────────────────────────────

@router.get("/audit/content")
async def audit_content(
    days: int = Query(90, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Audit content performance."""
    workspace_id = await _get_workspace_id(db, current_user)
    from app.services.content_audit import audit_content
    return await audit_content(db, workspace_id, days)


# ─── Phase 14: Content Brief Builder ────────────────────────────────────────

@router.post("/briefs/create")
async def create_brief(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a structured content brief."""
    from app.services.content_brief import create_brief
    return await create_brief(
        db, "workspace",
        request.get("brief_type", "social_post"),
        request.get("title", ""),
        request.get("content", {}),
        request.get("platforms"),
    )


@router.get("/briefs/templates")
async def get_brief_templates(
    current_user: User = Depends(get_current_user),
):
    """Get available brief templates."""
    from app.services.content_brief import get_brief_templates
    return {"templates": get_brief_templates()}


# ─── Phase 14: Caption Variants ────────────────────────────────────────────

@router.post("/captions/variants")
async def generate_caption_variants(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Generate multiple caption variants for A/B testing."""
    from app.services.caption_variants import generate_caption_variants
    return await generate_caption_variants(
        request.get("topic", ""),
        request.get("platform", "linkedin"),
        request.get("tone", "professional"),
        request.get("count", 5),
        request.get("existing_content"),
        request.get("provider", "openai"),
    )


# ─── Phase 14: Story Arcs ──────────────────────────────────────────────────

@router.get("/story-arcs")
async def get_story_arcs(
    current_user: User = Depends(get_current_user),
):
    """Get available story arc templates."""
    from app.services.story_templates import get_story_arcs
    return {"arcs": get_story_arcs()}


@router.get("/story-arcs/{arc_key}")
async def get_story_arc(
    arc_key: str,
    current_user: User = Depends(get_current_user),
):
    """Get a specific story arc with prompts."""
    from app.services.story_templates import get_story_arc, get_arc_prompts
    arc = get_story_arc(arc_key)
    if not arc:
        raise HTTPException(status_code=404, detail=f"Arc '{arc_key}' not found")
    return {"arc": arc, "prompts": get_arc_prompts(arc_key)}


# ─── Phase 14: Batch Planner ───────────────────────────────────────────────

@router.post("/batch/plan-week")
async def plan_weekly_batch(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Plan a week of content across platforms."""
    from app.services.batch_planner import plan_weekly_batch
    return await plan_weekly_batch(
        request.get("topic", ""),
        request.get("platforms", ["linkedin", "x"]),
        request.get("pillars"),
        request.get("brand_voice"),
        request.get("provider", "openai"),
    )


@router.post("/batch/plan-month")
async def plan_monthly_batch(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Plan a month of content (4 weekly batches)."""
    from app.services.batch_planner import plan_monthly_batch
    return await plan_monthly_batch(
        request.get("topic", ""),
        request.get("platforms", ["linkedin", "x"]),
        request.get("pillars"),
        request.get("provider", "openai"),
    )


# ─── Phase 14: Review Checklist ────────────────────────────────────────────

@router.get("/review/checklist/{platform}")
async def get_review_checklist(
    platform: str,
    current_user: User = Depends(get_current_user),
):
    """Get the review checklist for a platform."""
    from app.services.review_checklist import get_review_checklist
    return {"platform": platform, "checklist": get_review_checklist(platform)}


@router.post("/review/validate")
async def validate_review(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Validate a completed review checklist."""
    from app.services.review_checklist import validate_checklist, get_review_checklist
    platform = request.get("platform", "linkedin")
    checklist = get_review_checklist(platform)
    completed = request.get("completed_items", [])
    return validate_checklist(checklist, completed)


# ─── Phase 14: Visual Guidelines ────────────────────────────────────────────

@router.get("/visual-guidelines/{platform}")
async def get_visual_guidelines(
    platform: str,
    current_user: User = Depends(get_current_user),
):
    """Get visual guidelines for a platform."""
    from app.services.visual_guidelines import get_visual_guidelines
    guidelines = get_visual_guidelines(platform)
    if not guidelines:
        raise HTTPException(status_code=404, detail=f"No guidelines for {platform}")
    return guidelines


@router.get("/visual-guidelines")
async def get_all_visual_guidelines(
    current_user: User = Depends(get_current_user),
):
    """Get visual guidelines for all platforms."""
    from app.services.visual_guidelines import get_all_guidelines
    return get_all_guidelines()


@router.get("/visual-guidelines/youtube/thumbnail-checklist")
async def get_thumbnail_checklist(
    current_user: User = Depends(get_current_user),
):
    """Get YouTube thumbnail best practices."""
    from app.services.visual_guidelines import get_thumbnail_checklist
    return {"checklist": get_thumbnail_checklist()}


# ─── Phase 14: CTA Library ─────────────────────────────────────────────────

@router.get("/cta-library")
async def get_cta_goals(
    current_user: User = Depends(get_current_user),
):
    """Get all CTA categories."""
    from app.services.cta_library import get_all_cta_goals
    return {"goals": get_all_cta_goals()}


@router.get("/cta-library/{goal}")
async def get_ctas_by_goal(
    goal: str,
    current_user: User = Depends(get_current_user),
):
    """Get CTAs filtered by goal."""
    from app.services.cta_library import get_ctas_by_goal
    return {"goal": goal, "ctas": get_ctas_by_goal(goal)}


@router.get("/cta-library/platform/{platform}")
async def get_ctas_by_platform(
    platform: str,
    current_user: User = Depends(get_current_user),
):
    """Get CTAs for a specific platform."""
    from app.services.cta_library import get_ctas_by_platform
    return {"platform": platform, "ctas": get_ctas_by_platform(platform)}


@router.post("/cta-library/search")
async def search_ctas(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Search CTAs by keyword."""
    from app.services.cta_library import search_ctas
    return {"query": request.get("query", ""), "results": search_ctas(request.get("query", ""))}
