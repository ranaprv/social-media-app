from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/team", tags=["team"])


@router.get("/members")
async def get_team_members(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all team members."""
    members = [
        {"id": "tm-1", "user_id": current_user.id, "name": current_user.name or "You", "email": current_user.email, "role": "owner", "joined_at": "2026-01-01"},
        {"id": "tm-2", "user_id": "user-2", "name": "Sarah Chen", "email": "sarah@example.com", "role": "admin", "joined_at": "2026-02-15"},
        {"id": "tm-3", "user_id": "user-3", "name": "Marcus Johnson", "email": "marcus@example.com", "role": "editor", "joined_at": "2026-03-10"},
        {"id": "tm-4", "user_id": "user-4", "name": "Priya Patel", "email": "priya@example.com", "role": "editor", "joined_at": "2026-04-20"},
        {"id": "tm-5", "user_id": "user-5", "name": "Alex Kim", "email": "alex@example.com", "role": "viewer", "joined_at": "2026-05-01"},
    ]
    return {"members": members}


@router.get("/comments")
async def get_comments(
    post_id: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get comments for a post."""
    comments = [
        {
            "id": "c-1",
            "post_id": post_id or "post-1",
            "author_id": "user-2",
            "author_name": "Sarah Chen",
            "content": "Love this angle! Maybe we could add a specific example from our Q2 campaign?",
            "created_at": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "replies": [
                {
                    "id": "c-1-1",
                    "post_id": post_id or "post-1",
                    "author_id": current_user.id,
                    "author_name": current_user.name or "You",
                    "content": "Great idea! I'll add the metrics from the product launch campaign.",
                    "created_at": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                }
            ],
        },
        {
            "id": "c-2",
            "post_id": post_id or "post-1",
            "author_id": "user-3",
            "author_name": "Marcus Johnson",
            "content": "The CTA at the end could be stronger. What about asking a specific question instead?",
            "created_at": (datetime.utcnow() - timedelta(hours=5)).isoformat(),
            "replies": [],
        },
        {
            "id": "c-3",
            "post_id": post_id or "post-1",
            "author_id": "user-4",
            "author_name": "Priya Patel",
            "content": "Approved from my side! Ready for scheduling.",
            "created_at": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
            "replies": [],
        },
    ]
    return {"comments": comments}


@router.post("/comments")
async def add_comment(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a comment to a post."""
    return {
        "id": str(uuid.uuid4()),
        "post_id": request.get("post_id"),
        "author_id": current_user.id,
        "author_name": current_user.name or "User",
        "content": request.get("content", ""),
        "created_at": datetime.utcnow().isoformat(),
    }


@router.get("/reviews")
async def get_reviews(
    status: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get review requests."""
    reviews = [
        {"id": "r-1", "post_id": "post-1", "post_title": "10 Tips for Content Creation", "requested_by": "user-2", "requested_by_name": "Sarah Chen", "assigned_to": current_user.id, "assigned_to_name": current_user.name or "You", "status": "pending", "requested_at": (datetime.utcnow() - timedelta(hours=3)).isoformat()},
        {"id": "r-2", "post_id": "post-2", "post_title": "Thread: Growth Strategies", "requested_by": current_user.id, "requested_by_name": current_user.name or "You", "assigned_to": "user-3", "assigned_to_name": "Marcus Johnson", "status": "approved", "feedback": "Looks great! Ship it.", "requested_at": (datetime.utcnow() - timedelta(days=1)).isoformat(), "completed_at": (datetime.utcnow() - timedelta(hours=12)).isoformat()},
        {"id": "r-3", "post_id": "post-3", "post_title": "Behind the Scenes Reel", "requested_by": "user-4", "requested_by_name": "Priya Patel", "assigned_to": current_user.id, "assigned_to_name": current_user.name or "You", "status": "changes-requested", "feedback": "Can we adjust the tone to be more casual? The hook needs work too.", "requested_at": (datetime.utcnow() - timedelta(hours=8)).isoformat()},
    ]
    if status:
        reviews = [r for r in reviews if r["status"] == status]
    return {"reviews": reviews}


@router.post("/reviews/{review_id}/approve")
async def approve_review(
    review_id: str,
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Approve a review."""
    return {"id": review_id, "status": "approved", "message": "Review approved"}


@router.post("/reviews/{review_id}/reject")
async def reject_review(
    review_id: str,
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Request changes or reject a review."""
    return {"id": review_id, "status": request.get("status", "changes-requested"), "message": "Review updated"}


@router.get("/version-history")
async def get_version_history(
    post_id: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get version history for a post."""
    versions = [
        {"id": "v-1", "post_id": post_id or "post-1", "post_title": "10 Tips for Content Creation", "version": 3, "content": "Final version with CTA improvements...", "author_id": current_user.id, "author_name": current_user.name or "You", "created_at": (datetime.utcnow() - timedelta(hours=1)).isoformat(), "change_note": "Improved CTA and added examples"},
        {"id": "v-2", "post_id": post_id or "post-1", "post_title": "10 Tips for Content Creation", "version": 2, "content": "Updated with team feedback...", "author_id": "user-2", "author_name": "Sarah Chen", "created_at": (datetime.utcnow() - timedelta(hours=4)).isoformat(), "change_note": "Added specific metrics from Q2 campaign"},
        {"id": "v-3", "post_id": post_id or "post-1", "post_title": "10 Tips for Content Creation", "version": 1, "content": "Initial draft...", "author_id": current_user.id, "author_name": current_user.name or "You", "created_at": (datetime.utcnow() - timedelta(hours=8)).isoformat(), "change_note": "Initial draft"},
    ]
    return {"versions": versions}


@router.get("/notifications")
async def get_notifications(
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user notifications."""
    notifications = [
        {"id": "n-1", "type": "review-request", "title": "Review Requested", "message": "Sarah Chen requested your review on '10 Tips for Content Creation'", "read": False, "post_id": "post-1", "actor_name": "Sarah Chen", "created_at": (datetime.utcnow() - timedelta(hours=3)).isoformat()},
        {"id": "n-2", "type": "comment", "title": "New Comment", "message": "Marcus Johnson commented on 'Thread: Growth Strategies'", "read": False, "post_id": "post-2", "actor_name": "Marcus Johnson", "created_at": (datetime.utcnow() - timedelta(hours=5)).isoformat()},
        {"id": "n-3", "type": "approval", "title": "Review Approved", "message": "Marcus Johnson approved 'Behind the Scenes Reel'", "read": True, "post_id": "post-3", "actor_name": "Marcus Johnson", "created_at": (datetime.utcnow() - timedelta(hours=12)).isoformat()},
        {"id": "n-4", "type": "mention", "title": "Mentioned", "message": "Priya Patel mentioned you in a comment on 'Weekly Motivation Post'", "read": True, "post_id": "post-4", "actor_name": "Priya Patel", "created_at": (datetime.utcnow() - timedelta(days=1)).isoformat()},
        {"id": "n-5", "type": "assignment", "title": "Assigned for Review", "message": "You've been assigned to review 'Product Update: New Features'", "read": False, "post_id": "post-5", "actor_name": "Sarah Chen", "created_at": (datetime.utcnow() - timedelta(hours=1)).isoformat()},
    ]
    if unread_only:
        notifications = [n for n in notifications if not n["read"]]
    return {"notifications": notifications, "unread_count": sum(1 for n in notifications if not n["read"])}


@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a notification as read."""
    return {"id": notification_id, "read": True}


@router.put("/notifications/read-all")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark all notifications as read."""
    return {"message": "All notifications marked as read"}
