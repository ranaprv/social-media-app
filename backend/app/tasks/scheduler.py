"""Periodic scheduler task — checks for posts due to be published."""
import logging
from app.tasks import celery_app

logger = logging.getLogger(__name__)


@celery_app.task
def check_scheduled_posts():
    """Check for posts where scheduled_at <= now and enqueue publish tasks."""
    logger.info("Checking for scheduled posts to publish...")

    try:
        import asyncio
        from datetime import datetime
        from sqlalchemy import select
        from app.core.database import AsyncSessionLocal
        from app.models.content import Post

        async def _check():
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(Post).where(
                        Post.status == "scheduled",
                        Post.scheduled_at <= datetime.utcnow(),
                    )
                )
                posts = result.scalars().all()
                for post in posts:
                    from app.tasks.publish_post import publish_post
                    publish_post.delay(
                        post_id=post.id,
                        workspace_id=post.workspace_id,
                        platform=post.platform,
                    )
                    post.status = "publishing"
                await db.commit()
                return len(posts)

        count = asyncio.run(_check())
        logger.info(f"Enqueued {count} posts for publishing")
        return {"enqueued": count}

    except Exception as e:
        logger.error(f"Scheduler error: {e}")
        return {"error": str(e)}


# Schedule the periodic tasks
celery_app.conf.beat_schedule = {
    "check-scheduled-posts": {
        "task": "app.tasks.scheduler.check_scheduled_posts",
        "schedule": 60.0,  # every 60 seconds
    },
    "collect-analytics": {
        "task": "app.tasks.analytics.collect_all_analytics",
        "schedule": 21600.0,  # every 6 hours
    },
}
