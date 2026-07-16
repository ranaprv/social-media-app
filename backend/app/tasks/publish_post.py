"""Celery task to publish a post to a social platform.

Automatically resolves media assets from the platform-specific directory
before publishing. The media library stores assets by platform + content_type,
and this task pulls the right ones for each platform.
"""
import logging
from app.tasks import celery_app

logger = logging.getLogger(__name__)

# Map platform to the content_type it expects for media
PLATFORM_MEDIA_TYPES: dict[str, list[str]] = {
    "youtube": ["video", "image"],
    "instagram": ["reel", "carousel", "vertical_video", "image"],
    "linkedin": ["post", "carousel", "video", "document"],
    "facebook": ["image", "video"],
}


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def publish_post(self, post_id: str, workspace_id: str, platform: str):
    """Publish a post to the specified platform.

    Resolves media assets from the platform directory in the media library
    before handing off to the platform-specific publisher.
    """
    logger.info(f"Publishing post {post_id} to {platform}")

    try:
        import asyncio
        from datetime import datetime
        from sqlalchemy import select
        from app.core.database import AsyncSessionLocal
        from app.models.content import Post, Asset
        from app.tasks.publish_media import resolve_platform_media

        async def _publish():
            async with AsyncSessionLocal() as db:
                # 1. Fetch the post
                result = await db.execute(select(Post).where(Post.id == post_id))
                post = result.scalar_one_or_none()
                if not post:
                    logger.error(f"Post {post_id} not found")
                    return {"status": "failed", "error": "Post not found"}

                # 2. Resolve media assets from platform directory
                media_assets = await resolve_platform_media(
                    db=db,
                    workspace_id=workspace_id,
                    platform=platform,
                )
                if media_assets:
                    logger.info(
                        f"Resolved {len(media_assets)} media assets for {platform}: "
                        f"{[a['name'] for a in media_assets]}"
                    )

                # 3. Publish via platform publisher
                from app.services.publishers import get_publisher
                publisher = get_publisher(platform)
                if not publisher:
                    logger.error(f"No publisher for platform: {platform}")
                    return {"status": "failed", "error": f"Unsupported platform: {platform}"}

                loop = asyncio.new_event_loop()
                try:
                    pub_result = loop.run_until_complete(
                        publisher.publish(
                            post_id=post_id,
                            workspace_id=workspace_id,
                            media_assets=media_assets,
                        )
                    )
                finally:
                    loop.close()

                # 4. Update post status
                post.status = "published"
                post.published_at = datetime.utcnow()
                post.platform_post_id = pub_result.get("platform_post_id")
                await db.commit()

                logger.info(f"Post {post_id} published to {platform}: {pub_result}")
                return {"status": "published", "platform": platform, "result": pub_result}

        return asyncio.run(_publish())

    except Exception as exc:
        logger.error(f"Failed to publish post {post_id}: {exc}")
        self.retry(exc=exc)
