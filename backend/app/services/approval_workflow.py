"""Approval workflow — DB-backed request → approve/reject → publish.

Replaces the mock approval endpoints with real DB operations.
Supports configurable multi-stage approval chains.
"""
import logging
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Post
from app.models.post_platform import PostPlatform
from app.models.user import User
from app.models.workspace import WorkspaceMember

logger = logging.getLogger(__name__)

# Approval states
STATUS_PENDING = "pending"
STATUS_APPROVED = "approved"
STATUS_REJECTED = "rejected"


async def request_approval(
    db: AsyncSession,
    workspace_id: str,
    post_id: str,
    requested_by: str,
    workflow_name: str = "Standard",
    assignee_id: str | None = None,
) -> dict[str, Any]:
    """Request approval for a post before it can be published.

    Sets all PostPlatform entries for this post to 'review' status.
    """
    # Get post
    post_result = await db.execute(
        select(Post).where(Post.id == post_id, Post.workspace_id == workspace_id)
    )
    post = post_result.scalar_one_none()
    if not post:
        return {"error": f"Post {post_id} not found"}

    # Get all platform entries
    pp_result = await db.execute(
        select(PostPlatform).where(PostPlatform.post_id == post_id)
    )
    platforms = pp_result.scalars().all()

    if not platforms:
        return {"error": "No platform entries found for this post"}

    # Set all to review status
    for pp in platforms:
        if pp.status in ("draft", "scheduled"):
            pp.status = "review"

    # Update parent post status
    post.status = "review"

    # Get requester name
    user_result = await db.execute(select(User).where(User.id == requested_by))
    user = user_result.scalar_one_or_none()
    requester_name = user.name or user.email if user else "Unknown"

    await db.flush()

    return {
        "post_id": post_id,
        "status": "review",
        "workflow": workflow_name,
        "requested_by": requester_name,
        "platforms": [pp.platform for pp in platforms],
        "message": f"Approval requested for {len(platforms)} platform(s)",
    }


async def approve_post(
    db: AsyncSession,
    workspace_id: str,
    post_id: str,
    approved_by: str,
    platform: str | None = None,
    comment: str = "",
) -> dict[str, Any]:
    """Approve a post (or specific platform entry) for publishing.

    If platform is None, approves all pending entries.
    If platform is specified, only approves that one.
    """
    # Get post
    post_result = await db.execute(
        select(Post).where(Post.id == post_id, Post.workspace_id == workspace_id)
    )
    post = post_result.scalar_one_none()
    if not post:
        return {"error": f"Post {post_id} not found"}

    # Get platform entries
    query = select(PostPlatform).where(PostPlatform.post_id == post_id)
    if platform:
        query = query.where(PostPlatform.platform == platform)

    pp_result = await db.execute(query)
    entries = pp_result.scalars().all()

    approved = []
    for pp in entries:
        if pp.status == "review":
            pp.status = "scheduled"
            approved.append(pp.platform)

    # Update parent post status if all entries are approved
    if approved:
        all_pp_result = await db.execute(
            select(PostPlatform).where(PostPlatform.post_id == post_id)
        )
        all_pp = all_pp_result.scalars().all()
        any_reviewing = any(p.status == "review" for p in all_pp)
        if not any_reviewing:
            post.status = "scheduled"

    # Get approver name
    user_result = await db.execute(select(User).where(User.id == approved_by))
    user = user_result.scalar_one_or_none()
    approver_name = user.name or user.email if user else "Unknown"

    await db.flush()

    return {
        "post_id": post_id,
        "approved_platforms": approved,
        "approved_by": approver_name,
        "comment": comment,
        "message": f"Approved {len(approved)} platform(s)",
    }


async def reject_post(
    db: AsyncSession,
    workspace_id: str,
    post_id: str,
    rejected_by: str,
    reason: str = "",
    platform: str | None = None,
) -> dict[str, Any]:
    """Reject a post and return it to draft status."""
    post_result = await db.execute(
        select(Post).where(Post.id == post_id, Post.workspace_id == workspace_id)
    )
    post = post_result.scalar_one_none()
    if not post:
        return {"error": f"Post {post_id} not found"}

    query = select(PostPlatform).where(PostPlatform.post_id == post_id)
    if platform:
        query = query.where(PostPlatform.platform == platform)

    pp_result = await db.execute(query)
    entries = pp_result.scalars().all()

    rejected = []
    for pp in entries:
        if pp.status in ("review", "scheduled"):
            pp.status = "draft"
            pp.error_message = f"Rejected: {reason}" if reason else None
            rejected.append(pp.platform)

    # Update parent post
    post.status = "draft"

    user_result = await db.execute(select(User).where(User.id == rejected_by))
    user = user_result.scalar_one_or_none()
    rejector_name = user.name or user.email if user else "Unknown"

    await db.flush()

    return {
        "post_id": post_id,
        "rejected_platforms": rejected,
        "rejected_by": rejector_name,
        "reason": reason,
        "message": f"Rejected {len(rejected)} platform(s)",
    }


async def get_pending_approvals(
    db: AsyncSession,
    workspace_id: str,
) -> list[dict[str, Any]]:
    """Get all posts awaiting approval in a workspace."""
    # Get posts in review status
    post_result = await db.execute(
        select(Post).where(
            Post.workspace_id == workspace_id,
            Post.status == "review",
        ).order_by(Post.updated_at.desc())
    )
    posts = post_result.scalars().all()

    results = []
    for post in posts:
        pp_result = await db.execute(
            select(PostPlatform).where(PostPlatform.post_id == post.id)
        )
        platforms = pp_result.scalars().all()

        results.append({
            "post_id": post.id,
            "title": post.title or post.content[:50],
            "content_preview": post.content[:200],
            "platforms": [
                {"platform": pp.platform, "status": pp.status}
                for pp in platforms
            ],
            "requested_at": post.updated_at.isoformat() if post.updated_at else None,
            "author_id": post.author_id,
        })

    return results


async def get_approval_stats(
    db: AsyncSession,
    workspace_id: str,
    days: int = 30,
) -> dict[str, Any]:
    """Get approval workflow statistics."""
    from datetime import timedelta
    cutoff = datetime.utcnow() - timedelta(days=days)

    # Count by status
    result = await db.execute(
        select(Post.status, func.count(Post.id))
        .where(
            Post.workspace_id == workspace_id,
            Post.updated_at >= cutoff,
        )
        .group_by(Post.status)
    )
    status_counts = {row[0]: row[1] for row in result.all()}

    total = sum(status_counts.values())
    review_count = status_counts.get("review", 0)
    published_count = status_counts.get("published", 0)
    draft_count = status_counts.get("draft", 0)

    return {
        "period_days": days,
        "total_posts": total,
        "awaiting_review": review_count,
        "published": published_count,
        "drafts": draft_count,
        "approval_rate": round(
            (published_count / max(total - draft_count, 1)) * 100, 1
        ) if total > 0 else 0,
    }
