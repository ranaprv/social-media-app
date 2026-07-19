"""Periodic scheduler — checks PostPlatform rows for posts due to publish.

Runs every 60 seconds via Celery beat. Also schedules:
  - Token refresh (every 5 minutes)
  - Analytics collection (every 6 hours)
  - Auto-recycling of top performers (weekly)
"""
import logging
from app.tasks import celery_app

logger = logging.getLogger(__name__)


@celery_app.task
def check_scheduled_posts():
    """Find PostPlatform rows where scheduled_at <= now and status == 'scheduled',
    then enqueue a publish task for each."""
    logger.info("Checking for scheduled posts to publish...")

    try:
        import asyncio
        from datetime import datetime
        from sqlalchemy import select
        from app.core.database import AsyncSessionLocal
        from app.models.post_platform import PostPlatform

        async def _check():
            async with AsyncSessionLocal() as db:
                now = datetime.utcnow()
                result = await db.execute(
                    select(PostPlatform).where(
                        PostPlatform.status == "scheduled",
                        PostPlatform.scheduled_at.isnot(None),
                        PostPlatform.scheduled_at <= now,
                    )
                )
                posts = result.scalars().all()
                enqueued = 0

                for pp in posts:
                    # Skip if retries exhausted
                    if (pp.retry_count or 0) >= (pp.max_retries or 3):
                        pp.status = "failed"
                        pp.error_message = "Max retries exceeded before publish attempt"
                        continue

                    from app.tasks.publish_post import publish_post
                    publish_post.delay(
                        post_id=pp.id,
                        workspace_id=pp.workspace_id,
                        platform=pp.platform,
                    )
                    pp.status = "publishing"
                    enqueued += 1

                    logger.info(
                        f"Enqueued publish: PostPlatform {pp.id} → {pp.platform}"
                    )

                await db.commit()
                return enqueued

        count = asyncio.run(_check())
        logger.info(f"Enqueued {count} posts for publishing")
        return {"enqueued": count}

    except Exception as e:
        logger.error(f"Scheduler error: {e}")
        return {"error": str(e)}


@celery_app.task
def refresh_platform_tokens():
    """Periodic task to refresh expiring platform OAuth tokens."""
    try:
        import asyncio
        from app.services.token_refresh import refresh_expiring_tokens
        return asyncio.run(refresh_expiring_tokens())
    except Exception as e:
        logger.error(f"Token refresh task error: {e}")
        return {"error": str(e)}


# Schedule the periodic tasks
celery_app.conf.beat_schedule = {
    "check-scheduled-posts": {
        "task": "app.tasks.scheduler.check_scheduled_posts",
        "schedule": 60.0,  # every 60 seconds
    },
    "refresh-platform-tokens": {
        "task": "app.tasks.scheduler.refresh_platform_tokens",
        "schedule": 300.0,  # every 5 minutes
    },
    "collect-analytics": {
        "task": "app.tasks.analytics.collect_all_analytics",
        "schedule": 21600.0,  # every 6 hours
    },
    "auto-recycle-posts": {
        "task": "app.tasks.recycle.auto_recycle_posts",
        "schedule": 604800.0,  # every 7 days
    },
}
