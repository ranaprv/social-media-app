"""Content pipeline orchestrator — draft→approve→schedule→publish→track.

Manages the full content lifecycle with state transitions and hooks.
"""
import logging
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Post
from app.models.post_platform import PostPlatform

logger = logging.getLogger(__name__)

# Pipeline stages
PIPELINE_STAGES = [
    {"id": "draft", "name": "Draft", "description": "Content created, not yet finalized"},
    {"id": "review", "name": "In Review", "description": "Awaiting approval"},
    {"id": "scheduled", "name": "Scheduled", "description": "Approved and scheduled for publishing"},
    {"id": "publishing", "name": "Publishing", "description": "Currently being published to platforms"},
    {"id": "published", "name": "Published", "description": "Successfully published"},
    {"id": "tracking", "name": "Tracking", "description": "Collecting analytics and engagement data"},
]

# Valid transitions
VALID_TRANSITIONS = {
    "draft": ["review", "scheduled", "cancelled"],
    "review": ["draft", "scheduled", "cancelled"],
    "scheduled": ["draft", "publishing", "cancelled"],
    "publishing": ["published", "failed"],
    "published": ["tracking"],
    "failed": ["scheduled", "draft", "cancelled"],
    "cancelled": ["draft"],
    "tracking": [],
}


async def get_pipeline_status(
    db: AsyncSession,
    workspace_id: str,
) -> dict[str, Any]:
    """Get the current pipeline status for a workspace."""
    # Count posts in each stage
    result = await db.execute(
        select(Post.status, func.count(Post.id))
        .where(Post.workspace_id == workspace_id)
        .group_by(Post.status)
    )
    status_counts = {row[0]: row[1] for row in result.all()}

    # Count platform entries in each stage
    pp_result = await db.execute(
        select(PostPlatform.status, func.count(PostPlatform.id))
        .where(PostPlatform.workspace_id == workspace_id)
        .group_by(PostPlatform.status)
    )
    pp_status_counts = {row[0]: row[1] for row in pp_result.all()}

    # Build pipeline view
    stages = []
    for stage in PIPELINE_STAGES:
        sid = stage["id"]
        stages.append({
            **stage,
            "post_count": status_counts.get(sid, 0),
            "platform_entries": pp_status_counts.get(sid, 0),
        })

    # Bottleneck detection
    bottleneck = None
    for stage in stages:
        if stage["platform_entries"] > 10 and stage["id"] in ("review", "scheduled"):
            bottleneck = {
                "stage": stage["id"],
                "count": stage["platform_entries"],
                "suggestion": f"{stage['platform_entries']} items stuck in {stage['name']}. Consider approving or cancelling.",
            }
            break

    return {
        "stages": stages,
        "total_posts": sum(status_counts.values()),
        "total_entries": sum(pp_status_counts.values()),
        "bottleneck": bottleneck,
    }


async def transition_status(
    db: AsyncSession,
    workspace_id: str,
    post_id: str,
    new_status: str,
    platform: str | None = None,
    user_id: str | None = None,
) -> dict[str, Any]:
    """Transition a post or platform entry to a new status."""
    result = await db.execute(
        select(Post).where(Post.id == post_id, Post.workspace_id == workspace_id)
    )
    post = result.scalar_one_none()
    if not post:
        return {"error": f"Post {post_id} not found"}

    # Validate transition
    current = post.status
    valid = VALID_TRANSITIONS.get(current, [])
    if new_status not in valid:
        return {
            "error": f"Invalid transition: {current} → {new_status}. Valid: {valid}",
        }

    # Update post status
    post.status = new_status

    # Update platform entries if specified
    updated_platforms = []
    if platform:
        pp_result = await db.execute(
            select(PostPlatform).where(
                PostPlatform.post_id == post_id,
                PostPlatform.platform == platform,
            )
        )
        pp = pp_result.scalar_one_none()
        if pp:
            pp.status = new_status
            if new_status == "published":
                pp.published_at = datetime.utcnow()
            updated_platforms.append(platform)
    else:
        # Update all platform entries
        pp_result = await db.execute(
            select(PostPlatform).where(PostPlatform.post_id == post_id)
        )
        for pp in pp_result.scalars().all():
            pp.status = new_status
            if new_status == "published":
                pp.published_at = datetime.utcnow()
            updated_platforms.append(pp.platform)

    # Log activity
    from app.services.audit_log import log_scheduling_action
    await log_scheduling_action(
        db, user_id or "system", f"post_{new_status}",
        f"Post {post_id} transitioned to {new_status}",
        {"post_id": post_id, "platforms": updated_platforms},
    )

    await db.flush()

    return {
        "post_id": post_id,
        "from_status": current,
        "to_status": new_status,
        "platforms": updated_platforms,
    }


def get_valid_transitions(current_status: str) -> list[str]:
    """Get valid status transitions from current status."""
    return VALID_TRANSITIONS.get(current_status, [])


def get_pipeline_stages() -> list[dict[str, str]]:
    """Get all pipeline stages."""
    return PIPELINE_STAGES
