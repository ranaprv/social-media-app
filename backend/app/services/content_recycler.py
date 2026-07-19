"""Content recycling — reshare top performers.

Finds posts with high engagement, creates new PostPlatform entries
to reshare them at optimal times.
"""
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Post, AnalyticsMetric
from app.models.post_platform import PostPlatform

logger = logging.getLogger(__name__)


async def find_top_performers(
    db: AsyncSession,
    workspace_id: str,
    platform: str | None = None,
    top_n: int = 5,
    min_age_days: int = 14,
    lookback_days: int = 90,
) -> list[dict[str, Any]]:
    """Find top-performing posts eligible for recycling.

    Criteria:
      - Published at least min_age_days ago (avoid reshares too soon)
      - Within lookback_days window
      - Not already scheduled for reshare

    Returns list of posts ranked by engagement rate.
    """
    cutoff = datetime.utcnow() - timedelta(days=lookback_days)
    min_age = datetime.utcnow() - timedelta(days=min_age_days)

    # Get published posts with their analytics
    query = (
        select(
            Post.id,
            Post.title,
            Post.content,
            Post.platform,
            Post.published_at,
            Post.media_urls,
            func.sum(AnalyticsMetric.engagement).label("total_engagement"),
            func.sum(AnalyticsMetric.impressions).label("total_impressions"),
            func.sum(AnalyticsMetric.reach).label("total_reach"),
            func.sum(AnalyticsMetric.clicks).label("total_clicks"),
            func.count(AnalyticsMetric.id).label("metric_count"),
        )
        .join(AnalyticsMetric, Post.id == AnalyticsMetric.post_id)
        .where(
            Post.workspace_id == workspace_id,
            Post.status == "published",
            Post.published_at <= min_age,
            Post.published_at >= cutoff,
        )
    )

    if platform:
        query = query.where(Post.platform == platform)

    query = (
        query.group_by(Post.id)
        .order_by(desc("total_engagement"))
        .limit(top_n * 2)  # Get extra to filter
    )

    rows = (await db.execute(query)).all()

    # Filter out posts already scheduled for reshare
    result = []
    for row in rows:
        post_id = row[0]
        existing = await db.execute(
            select(PostPlatform).where(
                PostPlatform.post_id == post_id,
                PostPlatform.status.in_(["scheduled", "publishing"]),
            )
        )
        if existing.scalar_one_none():
            continue  # Already scheduled, skip

        total_engagement = row[6] or 0
        total_impressions = row[7] or 0
        eng_rate = (total_engagement / total_impressions * 100) if total_impressions > 0 else 0

        result.append({
            "post_id": post_id,
            "title": row[1],
            "content": row[2][:200] + "..." if len(row[2] or "") > 200 else row[2],
            "platform": row[3],
            "published_at": row[4].isoformat() if row[4] else None,
            "media_urls": row[5] or [],
            "total_engagement": total_engagement,
            "total_impressions": total_impressions,
            "total_reach": row[8] or 0,
            "total_clicks": row[9] or 0,
            "engagement_rate": round(eng_rate, 2),
            "days_since_published": (
                (datetime.utcnow() - row[4]).days if row[4] else 0
            ),
        })

        if len(result) >= top_n:
            break

    return result


async def schedule_recycle(
    db: AsyncSession,
    workspace_id: str,
    post_id: str,
    platform: str,
    scheduled_at: datetime,
    caption_override: str | None = None,
) -> PostPlatform | None:
    """Create a new PostPlatform entry to reshare a top performer.

    The new entry gets its own ID — it doesn't modify the original Post.
    """
    # Verify the post exists and is published
    post_result = await db.execute(
        select(Post).where(Post.id == post_id, Post.status == "published")
    )
    post = post_result.scalar_one_none()
    if not post:
        logger.warning(f"Post {post_id} not found or not published")
        return None

    # Check not already scheduled
    existing = await db.execute(
        select(PostPlatform).where(
            PostPlatform.post_id == post_id,
            PostPlatform.platform == platform,
            PostPlatform.status.in_(["scheduled", "publishing"]),
        )
    )
    if existing.scalar_one_none():
        logger.warning(f"Post {post_id} already scheduled for {platform}")
        return None

    pp = PostPlatform(
        id=str(uuid.uuid4()),
        post_id=post_id,
        workspace_id=workspace_id,
        platform=platform,
        caption=caption_override,
        status="scheduled",
        scheduled_at=scheduled_at,
    )
    db.add(pp)
    await db.flush()

    logger.info(f"Scheduled recycle: Post {post_id} → {platform} at {scheduled_at}")
    return pp


async def auto_recycle_top_performers(
    db: AsyncSession,
    workspace_id: str,
    max_recycles_per_week: int = 3,
) -> list[dict[str, Any]]:
    """Automatically schedule recycling for top performers.

    Finds the best posts and schedules them for the next available
    optimal time slots. Limits to max_recycles_per_week per workspace.
    """
    from app.services.best_time_recommender import get_next_suggested_time

    # Find top performers
    top_posts = await find_top_performers(db, workspace_id, top_n=max_recycles_per_week)
    if not top_posts:
        return []

    # Check how many recycles are already scheduled this week
    week_start = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
    week_end = week_start + timedelta(days=7)

    scheduled_count_result = await db.execute(
        select(func.count(PostPlatform.id)).where(
            PostPlatform.workspace_id == workspace_id,
            PostPlatform.status.in_(["scheduled", "publishing"]),
            PostPlatform.scheduled_at >= week_start,
            PostPlatform.scheduled_at <= week_end,
        )
    )
    already_scheduled = scheduled_count_result.scalar() or 0
    slots_remaining = max(0, max_recycles_per_week - already_scheduled)

    if slots_remaining == 0:
        logger.info(f"Workspace {workspace_id} already at max recycles for the week")
        return []

    scheduled = []
    for post in top_posts[:slots_remaining]:
        platform = post["platform"]
        suggestion = await get_next_suggested_time(db, workspace_id, platform)
        if suggestion:
            pp = await schedule_recycle(
                db=db,
                workspace_id=workspace_id,
                post_id=post["post_id"],
                platform=platform,
                scheduled_at=datetime.fromisoformat(suggestion["suggested_at"]),
            )
            if pp:
                scheduled.append({
                    "post_id": post["post_id"],
                    "title": post["title"],
                    "platform": platform,
                    "scheduled_at": suggestion["suggested_at"],
                    "score": post["engagement_rate"],
                    "reason": suggestion.get("reason", "Top performer"),
                })

    return scheduled
