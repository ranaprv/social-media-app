"""Webhook receiver — platform callbacks for publish confirmation.

Handles incoming webhooks from platforms to confirm publish status,
update metrics, and trigger follow-up actions.
"""
import hashlib
import hmac
import json
import logging
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Post, PlatformConnection, AnalyticsMetric
from app.models.post_platform import PostPlatform

logger = logging.getLogger(__name__)


async def handle_platform_webhook(
    db: AsyncSession,
    platform: str,
    payload: dict[str, Any],
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Process an incoming webhook from a social platform.

    Routes to the appropriate handler based on platform.
    """
    handlers = {
        "facebook": _handle_facebook_webhook,
        "instagram": _handle_instagram_webhook,
        "youtube": _handle_youtube_webhook,
    }

    handler = handlers.get(platform)
    if not handler:
        return {"status": "ignored", "message": f"No webhook handler for {platform}"}

    return await handler(db, payload, headers or {})


async def _handle_facebook_webhook(
    db: AsyncSession,
    payload: dict[str, Any],
    headers: dict[str, str],
) -> dict[str, Any]:
    """Handle Facebook Graph API webhook."""
    # Facebook sends page updates, comments, etc.
    entry = payload.get("entry", [{}])[0]
    changes = entry.get("changes", [])

    for change in changes:
        field = change.get("field", "")
        value = change.get("value", {})

        if field == "feed":
            item = value.get("item", "")
            post_id = value.get("post_id", "")
            verb = value.get("verb", "")

            if verb == "share" and post_id:
                logger.info(f"Facebook share detected for post {post_id}")
                # Update analytics if we have a matching post

    return {"status": "processed", "platform": "facebook"}


async def _handle_instagram_webhook(
    db: AsyncSession,
    payload: dict[str, Any],
    headers: dict[str, str],
) -> dict[str, Any]:
    """Handle Instagram Graph API webhook."""
    # Instagram sends media updates, comments, etc.
    entry = payload.get("entry", [{}])[0]
    changes = entry.get("changes", [])

    for change in changes:
        field = change.get("field", "")
        value = change.get("value", {})

        if field == "media":
            media_id = value.get("media_id", "")
            if media_id:
                logger.info(f"Instagram media update: {media_id}")

    return {"status": "processed", "platform": "instagram"}


async def _handle_youtube_webhook(
    db: AsyncSession,
    payload: dict[str, Any],
    headers: dict[str, str],
) -> dict[str, Any]:
    """Handle YouTube Data API webhook (PubSubHubbub)."""
    # YouTube sends video upload notifications
    video_id = payload.get("videoId", "")
    channel_id = payload.get("channelId", "")

    if video_id:
        # Find matching PostPlatform and update status
        result = await db.execute(
            select(PostPlatform).where(
                PostPlatform.platform_post_id == video_id,
                PostPlatform.platform == "youtube",
            )
        )
        pp = result.scalar_one_none()
        if pp:
            pp.status = "published"
            pp.published_at = datetime.utcnow()
            await db.flush()
            logger.info(f"YouTube video confirmed: {video_id}")

    return {"status": "processed", "platform": "youtube"}


def verify_webhook_signature(
    platform: str,
    payload: bytes,
    signature: str,
    secret: str,
) -> bool:
    """Verify webhook signature for security."""
    if platform == "facebook":
        # Facebook uses HMAC-SHA256
        expected = hmac.new(
            secret.encode(), payload, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(f"sha256={expected}", signature)
    elif platform == "youtube":
        # YouTube uses X-Hub-Signature
        expected = hmac.new(
            secret.encode(), payload, hashlib.sha1
        ).hexdigest()
        return hmac.compare_digest(f"sha1={expected}", signature)
    else:
        return True  # No verification for unknown platforms
