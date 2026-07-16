"""Celery task to publish a post to a social platform."""
import logging
from app.tasks import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def publish_post(self, post_id: str, workspace_id: str, platform: str):
    """Publish a post to the specified platform."""
    logger.info(f"Publishing post {post_id} to {platform}")

    try:
        # Import here to avoid circular imports at module load time
        import asyncio
        from app.services.publishers import get_publisher

        publisher = get_publisher(platform)
        if not publisher:
            logger.error(f"No publisher for platform: {platform}")
            return {"status": "failed", "error": f"Unsupported platform: {platform}"}

        # Run async publisher in sync context
        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(
                publisher.publish(post_id=post_id, workspace_id=workspace_id)
            )
        finally:
            loop.close()

        logger.info(f"Post {post_id} published to {platform}: {result}")
        return {"status": "published", "platform": platform, "result": result}

    except Exception as exc:
        logger.error(f"Failed to publish post {post_id}: {exc}")
        self.retry(exc=exc)
