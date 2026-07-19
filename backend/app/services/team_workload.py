"""Team workload balancer — distribute posts across team members.

Analyzes team capacity and distributes scheduling workload evenly.
"""
import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Post
from app.models.workspace import WorkspaceMember

logger = logging.getLogger(__name__)


async def get_team_workload(
    db: AsyncSession,
    workspace_id: str,
    days: int = 7,
) -> dict[str, Any]:
    """Get current workload distribution across team members."""
    cutoff = datetime.utcnow() - timedelta(days=days)

    # Get team members
    members_result = await db.execute(
        select(WorkspaceMember).where(WorkspaceMember.workspace_id == workspace_id)
    )
    members = members_result.scalars().all()

    # Count posts per member
    workload: dict[str, dict[str, Any]] = {}
    for member in members:
        post_result = await db.execute(
            select(
                Post.status,
                func.count(Post.id),
            ).where(
                Post.author_id == member.user_id,
                Post.workspace_id == workspace_id,
                Post.created_at >= cutoff,
            ).group_by(Post.status)
        )
        status_counts = {row[0]: row[1] for row in post_result.all()}
        total = sum(status_counts.values())

        workload[member.user_id] = {
            "user_id": member.user_id,
            "role": member.role,
            "total_posts": total,
            "drafts": status_counts.get("draft", 0),
            "scheduled": status_counts.get("scheduled", 0),
            "published": status_counts.get("published", 0),
            "posts_per_day": round(total / max(days, 1), 1),
        }

    # Calculate imbalance
    if workload:
        totals = [w["total_posts"] for w in workload.values()]
        avg = sum(totals) / len(totals) if totals else 0
        max_val = max(totals) if totals else 0
        min_val = min(totals) if totals else 0
        imbalance = (max_val - min_val) / max(avg, 1) if avg > 0 else 0
    else:
        imbalance = 0

    return {
        "period_days": days,
        "members": list(workload.values()),
        "total_posts": sum(w["total_posts"] for w in workload.values()),
        "avg_posts_per_member": round(sum(w["total_posts"] for w in workload.values()) / max(len(workload), 1), 1),
        "imbalance_score": round(imbalance, 2),
        "recommendation": (
            "Workload is balanced" if imbalance < 0.3
            else "Consider redistributing posts — some members are overloaded"
        ),
    }


async def suggest_assignments(
    db: AsyncSession,
    workspace_id: str,
    post_count: int,
) -> list[dict[str, Any]]:
    """Suggest how to distribute new posts across team members."""
    workload = await get_team_workload(db, workspace_id)
    members = workload["members"]

    if not members:
        return []

    # Sort by current workload (ascending)
    members_sorted = sorted(members, key=lambda m: m["total_posts"])

    # Round-robin assignment with preference for less loaded members
    assignments = []
    for i in range(post_count):
        member = members_sorted[i % len(members_sorted)]
        assignments.append({
            "post_index": i + 1,
            "assigned_to": member["user_id"],
            "current_workload": member["total_posts"],
            "reason": f"Least loaded ({member['total_posts']} posts)",
        })

    return assignments
