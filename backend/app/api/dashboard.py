from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.workspace import WorkspaceMember
from app.models.content import Post, AnalyticsMetric
from app.schemas import DashboardStats

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/{workspace_id}/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify access
    result = await db.execute(
        select(WorkspaceMember)
        .where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id,
        )
    )
    if not result.scalar_one_or_none():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # Count posts by status
    total_result = await db.execute(
        select(func.count(Post.id)).where(Post.workspace_id == workspace_id)
    )
    total_posts = total_result.scalar() or 0
    
    scheduled_result = await db.execute(
        select(func.count(Post.id)).where(
            Post.workspace_id == workspace_id,
            Post.status == "scheduled",
        )
    )
    scheduled_posts = scheduled_result.scalar() or 0
    
    published_result = await db.execute(
        select(func.count(Post.id)).where(
            Post.workspace_id == workspace_id,
            Post.status == "published",
        )
    )
    published_posts = published_result.scalar() or 0
    
    # Get analytics totals
    analytics_result = await db.execute(
        select(
            func.coalesce(func.sum(AnalyticsMetric.impressions), 0),
            func.coalesce(func.sum(AnalyticsMetric.engagement), 0),
        )
        .join(Post, AnalyticsMetric.post_id == Post.id)
        .where(Post.workspace_id == workspace_id)
    )
    analytics_row = analytics_result.one()
    total_impressions = analytics_row[0] or 0
    total_engagement = analytics_row[1] or 0
    
    return DashboardStats(
        total_posts=total_posts,
        scheduled_posts=scheduled_posts,
        published_posts=published_posts,
        total_impressions=total_impressions,
        total_engagement=total_engagement,
        followers_growth=0,  # TODO: Calculate from platform APIs
    )
