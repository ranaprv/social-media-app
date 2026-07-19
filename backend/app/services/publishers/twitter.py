"""X (Twitter) Publisher — real API integration via Twitter API v2.

Endpoints used:
  POST https://api.twitter.com/2/tweets                    — create tweet
  POST https://api.twitter.com/1.1/media/upload.json       — upload media (v1.1)
  GET  https://api.twitter.com/2/tweets/:id                — verify tweet exists

Docs: https://developer.x.com/en/docs/twitter-api/tweets/manage-tweets/api-reference
"""
import httpx
import logging
import json
from typing import Any

from app.services.publishers.base import PlatformPublisher, ContentLimits, PublishResult

logger = logging.getLogger(__name__)

TWITTER_API_V2_BASE = "https://api.twitter.com/2"
TWITTER_API_V1_1_BASE = "https://api.twitter.com/1.1"


class TwitterPublisher(PlatformPublisher):

    @property
    def platform_name(self) -> str:
        return "x"

    def content_limits(self) -> ContentLimits:
        return ContentLimits(
            max_caption_length=280,       # Free tier; enterprise gets 25,000
            max_media_count=4,
            supported_media_types=["image", "gif", "video"],
            supported_image_formats=["jpg", "jpeg", "png", "gif", "webp"],
            supported_video_formats=["mp4"],
            max_video_duration_seconds=140,  # Free: 140s; paid: up to 10min
            max_video_size_mb=512,
        )

    def supports_scheduling(self) -> bool:
        # X has native scheduling only on Pro tier ($100/mo)
        return False  # We schedule via our own system

    async def publish(
        self,
        post_id: str,
        workspace_id: str,
        media_assets: list[dict[str, Any]] | None = None,
        caption: str | None = None,
        title: str | None = None,
        access_token: str = "",
    ) -> PublishResult:
        """Publish a tweet to X/Twitter.

        Args:
            post_id: PostPlatform row ID.
            workspace_id: Owning workspace.
            media_assets: Resolved media assets.
            caption: Tweet text (max 280 chars free tier).
            title: Not used for tweets.
            access_token: Twitter OAuth 2.0 Bearer token.
        """
        if not access_token:
            return PublishResult(success=False, error_message="Missing access_token for X/Twitter")

        if not caption:
            return PublishResult(success=False, error_message="Caption is required")

        # Upload media first if present
        media_ids: list[str] = []
        if media_assets:
            for asset in media_assets:
                asset_url = asset.get("url", "")
                asset_type = asset.get("content_type", asset.get("type", ""))
                if asset_url and asset_type in ("image", "video", "gif", "reel"):
                    media_id = await self._upload_media(access_token, asset_url, asset_type)
                    if media_id:
                        media_ids.append(media_id)

        # Build tweet payload
        tweet_data: dict[str, Any] = {"text": caption}

        if media_ids:
            tweet_data["media"] = {"media_ids": media_ids}

        # Post the tweet
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{TWITTER_API_V2_BASE}/tweets",
                    json=tweet_data,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                    },
                )

                if response.status_code in (200, 201):
                    data = response.json()
                    tweet_id = data.get("data", {}).get("id", "")
                    logger.info(f"Tweet published: {tweet_id}")
                    return PublishResult(
                        success=True,
                        platform_post_id=tweet_id,
                        raw_response=data,
                    )
                else:
                    error_detail = response.text
                    logger.error(f"Tweet failed ({response.status_code}): {error_detail}")
                    return PublishResult(
                        success=False,
                        error_message=f"Twitter API error {response.status_code}: {error_detail}",
                        raw_response={"status": response.status_code, "body": error_detail},
                    )

        except httpx.TimeoutException:
            return PublishResult(success=False, error_message="Twitter API timeout")
        except Exception as e:
            logger.error(f"Tweet publish exception: {e}")
            return PublishResult(success=False, error_message=str(e))

    async def _upload_media(self, access_token: str, media_url: str, media_type: str) -> str | None:
        """Upload media to Twitter using v1.1 media upload endpoint.

        Twitter v2 media upload is limited; v1.1 is still required for most media.
        """
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                # First download the file from our URL
                file_response = await client.get(media_url)
                if file_response.status_code != 200:
                    logger.error(f"Failed to download media from {media_url}")
                    return None

                # Upload to Twitter
                files = {
                    "media": ("media", file_response.content, "image/jpeg"),
                }

                upload_response = await client.post(
                    f"{TWITTER_API_V1_1_BASE}/media/upload.json",
                    files=files,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                    },
                )

                if upload_response.status_code in (200, 201):
                    data = upload_response.json()
                    media_id = str(data.get("media_id_string") or data.get("media_id", ""))
                    logger.info(f"Twitter media uploaded: {media_id}")
                    return media_id

                logger.error(f"Twitter media upload failed: {upload_response.text}")
                return None

        except Exception as e:
            logger.error(f"Twitter media upload error: {e}")
            return None

    async def refresh_access_token(self, connection: Any) -> str | None:
        """Refresh Twitter OAuth 2.0 access token.

        Twitter uses standard OAuth 2.0 refresh token flow.
        """
        from app.core.config import get_settings
        settings = get_settings()

        refresh_token = (connection.meta or {}).get("refresh_token") or getattr(connection, "refresh_token", None)
        if not refresh_token:
            return None

        try:
            # Twitter uses Basic Auth with client_id:client_secret for token refresh
            import base64
            credentials = base64.b64encode(
                f"{settings.TWITTER_CLIENT_ID}:{settings.TWITTER_CLIENT_SECRET}".encode()
            ).decode()

            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(
                    "https://api.twitter.com/2/oauth2/token",
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": refresh_token,
                    },
                    headers={
                        "Authorization": f"Basic {credentials}",
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    new_access_token = data.get("access_token", "")
                    logger.info("Twitter token refreshed successfully")
                    return new_access_token
                else:
                    logger.error(f"Twitter token refresh failed: {response.text}")
                    return None

        except Exception as e:
            logger.error(f"Twitter token refresh error: {e}")
            return None
