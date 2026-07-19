"""Instagram Publisher — real API integration via Instagram Graph API.

Instagram publishing uses a two-phase flow:
  1. POST /{ig-user-id}/media — create a media container (image or video)
  2. POST /{ig-user-id}/media_publish — publish the container

For carousels:
  1. POST /{ig-user-id}/media — create individual item containers
  2. POST /{ig-user-id}/media — create carousel container with children
  3. POST /{ig-user-id}/media_publish — publish the carousel

For Reels:
  Same as video but with video_type=REELS

Docs: https://developers.facebook.com/docs/instagram-api/guides/publishing
"""
import httpx
import logging
import time
from typing import Any

from app.services.publishers.base import PlatformPublisher, ContentLimits, PublishResult

logger = logging.getLogger(__name__)

FB_API_VERSION = "v19.0"
FB_GRAPH_BASE = f"https://graph.facebook.com/{FB_API_VERSION}"

# How long to wait for Instagram to process a container before publishing
CONTAINER_POLL_INTERVAL = 5  # seconds
CONTAINER_POLL_MAX_ATTEMPTS = 30  # 5 * 30 = 150 seconds max


class InstagramPublisher(PlatformPublisher):

    @property
    def platform_name(self) -> str:
        return "instagram"

    def content_limits(self) -> ContentLimits:
        return ContentLimits(
            max_caption_length=2200,
            max_media_count=10,  # carousels: 2-10 items
            supported_media_types=["image", "reel", "carousel", "video"],
            supported_image_formats=["jpg", "jpeg", "png"],
            supported_video_formats=["mp4", "mov"],
            max_video_duration_seconds=90,  # Reels
            max_video_size_mb=256,
        )

    def supports_scheduling(self) -> bool:
        return False  # IG API has no native scheduling

    async def publish(
        self,
        post_id: str,
        workspace_id: str,
        media_assets: list[dict[str, Any]] | None = None,
        caption: str | None = None,
        title: str | None = None,
        access_token: str = "",
        ig_user_id: str = "",
    ) -> PublishResult:
        """Publish to Instagram.

        Args:
            access_token: Instagram Graph API access token (Page token).
            ig_user_id: Instagram Business/Creator account ID.
        """
        if not access_token or not ig_user_id:
            return PublishResult(
                success=False,
                error_message="Missing access_token or ig_user_id for Instagram",
            )

        if not caption:
            return PublishResult(success=False, error_message="Caption is required")

        # Classify media
        images = []
        videos = []
        if media_assets:
            for asset in media_assets:
                asset_type = asset.get("content_type", asset.get("type", ""))
                asset_url = asset.get("url", "")
                if asset_type in ("image",) and asset_url:
                    images.append(asset_url)
                elif asset_type in ("video", "reel") and asset_url:
                    videos.append(asset_url)

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                # Determine post type
                if len(images) > 1:
                    return await self._publish_carousel(
                        client, access_token, ig_user_id, images, caption
                    )
                elif len(images) == 1 and not videos:
                    return await self._publish_image(
                        client, access_token, ig_user_id, images[0], caption
                    )
                elif videos:
                    is_reel = any(
                        media_assets and
                        any(a.get("content_type") == "reel" for a in media_assets)
                    )
                    return await self._publish_video(
                        client, access_token, ig_user_id, videos[0], caption, is_reel
                    )
                else:
                    return PublishResult(
                        success=False,
                        error_message="Instagram requires at least one image or video",
                    )

        except httpx.TimeoutException:
            return PublishResult(success=False, error_message="Instagram API timeout")
        except Exception as e:
            logger.error(f"Instagram publish exception: {e}")
            return PublishResult(success=False, error_message=str(e))

    async def _publish_image(
        self, client: httpx.AsyncClient, access_token: str,
        ig_user_id: str, image_url: str, caption: str,
    ) -> PublishResult:
        """Single image post: create container → poll → publish."""
        # Step 1: Create image container
        container_id = await self._create_container(
            client, access_token, ig_user_id,
            {"image_url": image_url, "caption": caption},
        )
        if not container_id:
            return PublishResult(success=False, error_message="Failed to create image container")

        # Step 2: Wait for processing
        ready = await self._wait_for_container(client, access_token, ig_user_id, container_id)
        if not ready:
            return PublishResult(success=False, error_message="Image container processing timed out")

        # Step 3: Publish
        return await self._finalize_publish(
            client, access_token, ig_user_id, container_id, "image"
        )

    async def _publish_video(
        self, client: httpx.AsyncClient, access_token: str,
        ig_user_id: str, video_url: str, caption: str, is_reel: bool = False,
    ) -> PublishResult:
        """Video/Reel post: create container → poll → publish."""
        params: dict[str, Any] = {
            "media_type": "REELS" if is_reel else "VIDEO",
            "video_url": video_url,
            "caption": caption,
        }

        container_id = await self._create_container(
            client, access_token, ig_user_id, params,
        )
        if not container_id:
            return PublishResult(success=False, error_message="Failed to create video container")

        # Video containers take longer to process
        ready = await self._wait_for_container(
            client, access_token, ig_user_id, container_id,
            max_attempts=60,  # 5 min for videos
        )
        if not ready:
            return PublishResult(success=False, error_message="Video container processing timed out")

        return await self._finalize_publish(
            client, access_token, ig_user_id, container_id,
            "reel" if is_reel else "video",
        )

    async def _publish_carousel(
        self, client: httpx.AsyncClient, access_token: str,
        ig_user_id: str, image_urls: list[str], caption: str,
    ) -> PublishResult:
        """Carousel post: create child containers → create carousel → poll → publish."""
        children_ids: list[str] = []

        for url in image_urls[:10]:  # max 10 items
            child_id = await self._create_container(
                client, access_token, ig_user_id,
                {"image_url": url, "is_carousel_item": True},
            )
            if child_id:
                children_ids.append(child_id)

        if len(children_ids) < 2:
            return PublishResult(
                success=False,
                error_message=f"Need at least 2 carousel items, got {len(children_ids)}",
            )

        # Create carousel container
        carousel_params = {
            "media_type": "CAROUSEL",
            "children": ",".join(children_ids),
            "caption": caption,
        }
        container_id = await self._create_container(
            client, access_token, ig_user_id, carousel_params,
        )
        if not container_id:
            return PublishResult(success=False, error_message="Failed to create carousel container")

        ready = await self._wait_for_container(client, access_token, ig_user_id, container_id)
        if not ready:
            return PublishResult(success=False, error_message="Carousel container processing timed out")

        return await self._finalize_publish(
            client, access_token, ig_user_id, container_id, "carousel",
        )

    async def _create_container(
        self, client: httpx.AsyncClient, access_token: str,
        ig_user_id: str, params: dict[str, Any],
    ) -> str | None:
        """Create a media container and return its ID."""
        params["access_token"] = access_token
        response = await client.post(
            f"{FB_GRAPH_BASE}/{ig_user_id}/media",
            data=params,
        )

        if response.status_code == 200:
            data = response.json()
            container_id = data.get("id", "")
            logger.info(f"Instagram container created: {container_id}")
            return container_id
        else:
            logger.error(f"Instagram container creation failed: {response.text}")
            return None

    async def _wait_for_container(
        self, client: httpx.AsyncClient, access_token: str,
        ig_user_id: str, container_id: str,
        max_attempts: int = CONTAINER_POLL_MAX_ATTEMPTS,
    ) -> bool:
        """Poll container status until it's ready to publish."""
        for attempt in range(max_attempts):
            response = await client.get(
                f"{FB_GRAPH_BASE}/{container_id}",
                params={"fields": "status_code", "access_token": access_token},
            )

            if response.status_code == 200:
                data = response.json()
                status = data.get("status_code", "")

                if status == "FINISHED":
                    return True
                elif status == "ERROR":
                    logger.error(f"Instagram container {container_id} processing error")
                    return False
                # else: STILL_PROCESSING or INITIATED — keep polling

            time.sleep(CONTAINER_POLL_INTERVAL)

        logger.error(f"Instagram container {container_id} timed out after {max_attempts} attempts")
        return False

    async def _finalize_publish(
        self, client: httpx.AsyncClient, access_token: str,
        ig_user_id: str, container_id: str, media_type: str,
    ) -> PublishResult:
        """Publish a ready container."""
        response = await client.post(
            f"{FB_GRAPH_BASE}/{ig_user_id}/media_publish",
            data={"creation_id": container_id, "access_token": access_token},
        )

        if response.status_code == 200:
            data = response.json()
            media_id = data.get("id", "")
            logger.info(f"Instagram {media_type} published: {media_id}")
            return PublishResult(
                success=True,
                platform_post_id=media_id,
                raw_response=data,
            )
        else:
            error_msg = response.text
            logger.error(f"Instagram publish failed: {error_msg}")
            return PublishResult(
                success=False,
                error_message=f"Instagram API error: {error_msg}",
                raw_response={"status": response.status_code, "body": error_msg},
            )

    async def refresh_access_token(self, connection: Any) -> str | None:
        """Refresh Instagram/Facebook token (uses same FB OAuth flow).

        Instagram tokens are actually Facebook Page tokens — same refresh.
        """
        from app.services.publishers.facebook import FacebookPublisher
        fb_publisher = FacebookPublisher()
        return await fb_publisher.refresh_access_token(connection)
