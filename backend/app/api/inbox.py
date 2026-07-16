"""Unified Inbox — messages, comments, mentions across platforms."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/inbox", tags=["inbox"])

PLATFORMS = ["linkedin", "x", "instagram", "facebook", "youtube"]
MESSAGE_TYPES = ["dm", "comment", "mention", "story_reply", "review"]


@router.get("/messages")
async def list_messages(
    platform: str = None,
    message_type: str = None,
    status: str = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List inbox messages with filtering and pagination."""
    # Demo messages — in production, query from messages table
    now = datetime.utcnow()
    messages = [
        {"id": str(uuid.uuid4()), "platform": "linkedin", "message_type": "comment", "sender_name": "Sarah Chen", "sender_avatar": "", "content": "Great insights on SaaS growth! Would love to collaborate.", "status": "unread", "received_at": (now - timedelta(hours=2)).isoformat()},
        {"id": str(uuid.uuid4()), "platform": "x", "message_type": "mention", "sender_name": "@techguru", "sender_avatar": "", "content": "Check out this thread about AI in content creation", "status": "unread", "received_at": (now - timedelta(hours=5)).isoformat()},
        {"id": str(uuid.uuid4()), "platform": "instagram", "message_type": "dm", "sender_name": "mike_designs", "sender_avatar": "", "content": "Love your content! Can you share the template?", "status": "read", "received_at": (now - timedelta(hours=8)).isoformat()},
        {"id": str(uuid.uuid4()), "platform": "facebook", "message_type": "comment", "sender_name": "Alex Kim", "sender_avatar": "", "content": "This is exactly what I needed. Thanks for sharing!", "status": "replied", "received_at": (now - timedelta(days=1)).isoformat()},
        {"id": str(uuid.uuid4()), "platform": "linkedin", "message_type": "dm", "sender_name": "Priya Patel", "sender_avatar": "", "content": "Would you be interested in a guest post collaboration?", "status": "unread", "received_at": (now - timedelta(hours=1)).isoformat()},
    ]

    # Apply filters
    if platform:
        messages = [m for m in messages if m["platform"] == platform]
    if message_type:
        messages = [m for m in messages if m["message_type"] == message_type]
    if status:
        messages = [m for m in messages if m["status"] == status]

    total = len(messages)
    messages = messages[offset:offset + limit]

    unread_by_platform = {}
    for m in messages:
        if m["status"] == "unread":
            unread_by_platform[m["platform"]] = unread_by_platform.get(m["platform"], 0) + 1

    return {
        "messages": messages,
        "total": total,
        "offset": offset,
        "limit": limit,
        "unread_count": sum(1 for m in messages if m["status"] == "unread"),
        "unread_by_platform": unread_by_platform,
    }


@router.put("/messages/{message_id}/read")
async def mark_read(
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a message as read."""
    return {"id": message_id, "status": "read", "message": "Marked as read"}


@router.put("/messages/read-all")
async def mark_all_read(
    platform: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark all messages as read."""
    return {"message": "All messages marked as read", "platform": platform}


@router.post("/messages/{message_id}/reply")
async def reply_message(
    message_id: str,
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Reply to a message."""
    content = request.get("content", "")
    saved_reply_id = request.get("saved_reply_id")

    return {
        "id": str(uuid.uuid4()),
        "message_id": message_id,
        "content": content,
        "author": current_user.name or current_user.email,
        "created_at": datetime.utcnow().isoformat(),
        "status": "sent",
    }


@router.get("/saved-replies")
async def list_saved_replies(
    search: str = "",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List saved reply templates."""
    replies = [
        {"id": "sr-1", "title": "Thank You", "content": "Thank you for your comment! We appreciate your feedback.", "category": "engagement", "shortcut": "/thanks"},
        {"id": "sr-2", "title": "DM Response", "content": "Thanks for reaching out! We'll get back to you within 24 hours.", "category": "support", "shortcut": "/dm"},
        {"id": "sr-3", "title": "Follow Back", "content": "Thanks for the follow! Check out our latest content for more insights.", "category": "engagement", "shortcut": "/follow"},
        {"id": "sr-4", "title": "Collaboration Inquiry", "content": "Thanks for your interest! We'd love to explore collaboration opportunities. Could you share more details?", "category": "business", "shortcut": "/collab"},
        {"id": "sr-5", "title": "Generic Positive", "content": "Glad you found this helpful! Let us know if you have any questions.", "category": "engagement", "shortcut": "/glad"},
    ]

    if search:
        q = search.lower()
        replies = [r for r in replies if q in r["title"].lower() or q in r["content"].lower() or q in r["shortcut"]]

    return {"replies": replies}


@router.post("/saved-replies")
async def create_saved_reply(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a saved reply template."""
    return {
        "id": str(uuid.uuid4()),
        "title": request.get("title", ""),
        "content": request.get("content", ""),
        "category": request.get("category", "general"),
        "shortcut": request.get("shortcut", ""),
        "created_at": datetime.utcnow().isoformat(),
    }


@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get total unread message count."""
    return {"unread_count": 3, "by_platform": {"linkedin": 2, "x": 1, "instagram": 0, "facebook": 0, "youtube": 0}}
