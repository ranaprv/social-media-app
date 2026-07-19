"""Facebook Publisher — real API integration via Facebook Graph API v19.0.

Endpoints used:
  POST https://graph.facebook.com/v19.0/{page_id}/feed        — text/link posts
  POST https://graph.facebook.com/v19.0/{page_id}/photos      — photo posts
  POST https://graph.facebook.com/v19.0/{page_id}/videos      — video posts
  POST https://graph.facebook.com/v19.0/me/accounts            — get page tokens

Docs: https://developers.facebook.com/docs/pages-api/posts
"""
import httpx
import logging
from typing import Any

from app.services.publishers.base import PlatformPublisher, ContentLimits, PublishResult

logger = logging.getLogger(__name__)

FB_API_VERSION = "v19.0"
FB_GRAPH_BASE = f"https://graph.facebook.com/{FB_API_VERSION}"


class FacebookPublisher(PlatformPublisher):

    @property
    def platform_name(self) -> str:
        return "facebook"

    def content_limits(self) -> ContentLimits:
        return ContentLimits(
            max_caption_length=63206,
            max_title_length=0,
            max_media_count=10,
            supported_media_types=["image", "video"],
            supported_image_formats=["jpg", "jpeg", "png", "gif", "webp"],
            supported_video_formats=["mp4", "mov"],
            max_video_duration_seconds=14400,  # 4 hours
            max_video_size_mb=10240,  # 10 GB
        )

    def supports_scheduling(self) -> bool:
        return False  # Facebook has no public scheduling API

    async def publish(
        self,
        post_id: str,
        workspace_id: str,
        media_assets: list[dict[str, Any]] | None = None,
        caption: str | None = None,
        title: str | None = None,
        access_token: str = "",
        page_id: str = "",
    ) -> PublishResult:
        """Publish a post to a Facebook Page.

        Args:
            access_token: Page access token (not user token).
            page_id: Facebook Page ID to post to.
        """
        if not access_token or not page_id:
            return PublishResult(
                success=False,
                error_message="Missing access_token or page_id for Facebook",
            )

        if not caption:
            return PublishResult(success=False, error_message="Caption is required")

        # Determine post type based on media
        has_image = False
        has_video = False
        image_url = None
        video_url = None

        if media_assets:
            for asset in media_assets:
                asset_type = asset.get("content_type", asset.get("type", ""))
                asset_url = asset.get("url", "")
                if asset_type in ("image",) and asset_url and not has_image:
                    has_image = True
                    image_url = asset_url
                elif asset_type in ("video",) and asset_url and not has_video:
                    has_video = True
                    video_url = asset_url

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                if has_video and video_url:
                    return await self._publish_video(
                        client, access_token, page_id, caption, video_url
                    )
                elif has_image and image_url:
                    return await self._publish_photo(
                        client, access_token, page_id, caption, image_url
                    )
                else:
                    return await self._publish_text(
                        client, access_token, page_id, caption
                    )

        except httpx.TimeoutException:
            return PublishResult(success=False, error_message="Facebook API timeout")
        except Exception as e:
            logger.error(f"Facebook publish exception: {e}")
            return PublishResult(success=False, error_message=str(e))

    async def _publish_text(
        self, client: httpx.AsyncClient, access_token: str,
        page_id: str, message: str,
    ) -> PublishResult:
        """Publish a text-only post."""
        response = await client.post(
            f"{FB_GRAPH_BASE}/{page_id}/feed",
            data={"message": message, "access_token": access_token},
        )
        return self._parse_response(response, "text post")

    async def _publish_photo(
        self, client: httpx.AsyncClient, access_token: str,
        page_id: str, message: str, image_url: str,
    ) -> PublishResult:
        """Publish a photo post with an external image URL."""
        response = await client.post(
            f"{FB_GRAPH_BASE}/{page_id}/photos",
            data={
                "url": image_url,
                "caption": message,
                "access_token": access_token,
            },
        )
        return self._parse_response(response, "photo post")

    async def _publish_video(
        self, client: httpx.AsyncClient, access_token: str,
        page_id: str, description: str, video_url: str,
    ) -> PublishResult:
        """Publish a video post.

        Facebook video upload is async — we submit the URL and Facebook
        processes it server-side.
        """
        response = await client.post(
            f"{FB_GRAPH_BASE}/{page_id}/videos",
            data={
                "file_url": video_url,
                "description": description,
                "access_token": access_token,
            },
        )
        return self._parse_response(response, "video post")

    def _parse_response(self, response: httpx.Response, post_type: str) -> PublishResult:
        """Parse a Facebook Graph API response into a PublishResult."""
        if response.status_code in (200, 201):
            data = response.json()
            post_id = data.get("id", "") or data.get("post_id", "")
            logger.info(f"Facebook {post_type} published: {post_id}")
            return PublishResult(
                success=True,
                platform_post_id=post_id,
                raw_response=data,
            )
        else:
            error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"message": response.text}
            fb_error = error_data.get("error", {})
            error_msg = fb_error.get("message", response.text)
            error_code = fb_error.get("code", response.status_code)
            logger.error(f"Facebook {post_type} failed ({error_code}): {error_msg}")
            return PublishResult(
                success=False,
                error_message=f"Facebook API error {error_code}: {error_msg}",
                raw_response={"status": response.status_code, "error": fb_error},
            )

    async def refresh_access_token(self, connection: Any) -> str | None:
        """Refresh Facebook Page access token.

        Facebook short-lived tokens (~1 hour) can be extended to long-lived
        (~60 days) using the endpoint below. We then extend again periodically.
        """
        from app.core.config import get_settings
        settings = get_settings()

        short_token = getattr(connection, "access_token", None) or (connection.meta or {}).get("access_token")
        if not short_token:
            return None

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(
                    f"{FB_GRAPH_BASE}/oauth/access_token",
                    params={
                        "grant_type": "fb_exchange_token",
                        "client_id": settings.FACEBOOK_APP_ID,
                        "client_secret": settings.FACEBOOK_APP_SECRET,
                        "fb_exchange_token": short_token,
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    long_token = data.get("access_token", "")
                    if long_token:
                        logger.info("Facebook token extended to long-lived")
                        return long_token
                    return short_token  # Return existing if no new token
                else:
                    logger.error(f"Facebook token refresh failed: {response.text}")
                    return None

        except Exception as e:
            logger.error(f"Facebook token refresh error: {e}")
            return None
