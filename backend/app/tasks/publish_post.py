"""Celery task to publish a post to a social platform.

Uses PostPlatform rows to determine what/where to publish.
Handles token fetching, content validation, and platform dispatch.
"""
import logging
from app.tasks import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def publish_post(self, post_id: str, workspace_id: str, platform: str):
    """Publish a PostPlatform to the specified platform.

    Args:
        post_id: The PostPlatform row ID (not the parent Post ID).
        workspace_id: The workspace owning the post.
        platform: Target platform key (linkedin, x, etc.).
    """
    logger.info(f"Publishing PostPlatform {post_id} to {platform}")

    try:
        import asyncio
        from datetime import datetime
        from sqlalchemy import select
        from app.core.database import AsyncSessionLocal
        from app.models.content import Post, PostPlatform
        from app.tasks.publish_media import resolve_platform_media

        async def _publish():
            async with AsyncSessionLocal() as db:
                # 1. Fetch the PostPlatform row
                result = await db.execute(
                    select(PostPlatform).where(PostPlatform.id == post_id)
                )
                pp = result.scalar_one_or_none()
                if not pp:
                    logger.error(f"PostPlatform {post_id} not found")
                    return {"status": "failed", "error": "PostPlatform not found"}

                # 2. Fetch parent Post for content
                post_result = await db.execute(
                    select(Post).where(Post.id == pp.post_id)
                )
                post = post_result.scalar_one_or_none()
                if not post:
                    logger.error(f"Parent Post {pp.post_id} not found")
                    return {"status": "failed", "error": "Parent post not found"}

                # 3. Resolve media assets from platform directory
                media_assets = await resolve_platform_media(
                    db=db,
                    workspace_id=workspace_id,
                    platform=platform,
                )
                if media_assets:
                    logger.info(
                        f"Resolved {len(media_assets)} media assets for {platform}"
                    )

                # 4. Validate content before publishing
                caption = pp.caption or post.content
                from app.services.content_validator import validate_post
                errors = validate_post(caption, platform, media_assets)
                if errors:
                    pp.status = "failed"
                    pp.error_message = "; ".join(errors)
                    await db.commit()
                    return {"status": "failed", "error": "; ".join(errors)}

                # 5. Get a valid access token
                from app.services.token_refresh import get_fresh_token
                access_token = await get_fresh_token(workspace_id, platform)
                if not access_token:
                    pp.status = "failed"
                    pp.error_message = f"No valid token for {platform}"
                    await db.commit()
                    return {"status": "failed", "error": f"No valid token for {platform}"}

                # 6. Resolve platform-specific metadata (e.g., LinkedIn author_urn)
                author_urn = ""
                if platform == "linkedin":
                    from app.models.content import PlatformConnection
                    conn_result = await db.execute(
                        select(PlatformConnection).where(
                            PlatformConnection.workspace_id == workspace_id,
                            PlatformConnection.platform == "linkedin",
                        )
                    )
                    conn = conn_result.scalar_one_or_none()
                    if conn:
                        meta = conn.meta or {}
                        author_urn = meta.get("author_urn", "")
                        if not author_urn:
                            # Fallback: derive from LinkedIn userinfo API
                            try:
                                import httpx
                                async with httpx.AsyncClient(timeout=10) as client:
                                    r = await client.get(
                                        "https://api.linkedin.com/v2/userinfo",
                                        headers={"Authorization": f"Bearer {access_token}"},
                                    )
                                    if r.status_code == 200:
                                        sub = r.json().get("sub", "")
                                        author_urn = f"urn:li:person:{sub}"
                                        meta["author_urn"] = author_urn
                                        conn.meta = meta
                                        await db.flush()
                            except Exception as e:
                                logger.warning(f"Failed to derive LinkedIn author_urn: {e}")

                    if not author_urn:
                        pp.status = "failed"
                        pp.error_message = "LinkedIn: no author_urn available. Reconnect your LinkedIn account."
                        await db.commit()
                        return {"status": "failed", "error": "LinkedIn: missing author_urn"}

                # 7. Dispatch to platform publisher
                from app.services.publishers import get_publisher
                publisher = get_publisher(platform)
                if not publisher:
                    pp.status = "failed"
                    pp.error_message = f"Unsupported platform: {platform}"
                    await db.commit()
                    return {"status": "failed", "error": f"Unsupported platform: {platform}"}

                # 8. Call publish with platform-specific kwargs
                publish_kwargs = {
                    "post_id": post_id,
                    "workspace_id": workspace_id,
                    "media_assets": media_assets,
                    "caption": caption,
                    "title": pp.title or post.title,
                    "access_token": access_token,
                    "author_urn": author_urn,
                    "db": db,
                    "connection": conn if platform == "linkedin" else None,
                }

                loop = asyncio.new_event_loop()
                try:
                    pub_result = loop.run_until_complete(
                        publisher.publish(**publish_kwargs)
                    )
                finally:
                    loop.close()

                # 8. Update PostPlatform status
                if pub_result.success:
                    pp.status = "published"
                    pp.published_at = datetime.utcnow()
                    pp.platform_post_id = pub_result.platform_post_id
                    pp.error_message = None
                    logger.info(
                        f"PostPlatform {post_id} published to {platform}: "
                        f"{pub_result.platform_post_id}"
                    )
                else:
                    pp.retry_count = (pp.retry_count or 0) + 1
                    if pp.retry_count >= pp.max_retries:
                        pp.status = "failed"
                        pp.error_message = (
                            f"Failed after {pp.retry_count} retries: "
                            f"{pub_result.error_message}"
                        )
                        logger.error(
                            f"PostPlatform {post_id} permanently failed: "
                            f"{pub_result.error_message}"
                        )
                    else:
                        pp.status = "scheduled"  # Will be retried
                        pp.error_message = pub_result.error_message
                        logger.warning(
                            f"PostPlatform {post_id} failed (attempt {pp.retry_count}), "
                            f"will retry: {pub_result.error_message}"
                        )

                # 9. Also update parent Post status if all platforms done
                if pp.status in ("published", "failed"):
                    all_pp = await db.execute(
                        select(PostPlatform).where(PostPlatform.post_id == post.id)
                    )
                    all_platforms = all_pp.scalars().all()
                    all_done = all(
                        p.status in ("published", "failed", "cancelled")
                        for p in all_platforms
                    )
                    if all_done:
                        any_published = any(
                            p.status == "published" for p in all_platforms
                        )
                        post.status = "published" if any_published else "failed"
                        if any_published:
                            post.published_at = datetime.utcnow()

                await db.commit()
                return {
                    "status": pp.status,
                    "platform": platform,
                    "platform_post_id": pp.platform_post_id,
                }

        return asyncio.run(_publish())

    except Exception as exc:
        logger.error(f"Failed to publish post {post_id}: {exc}")
        self.retry(exc=exc)
