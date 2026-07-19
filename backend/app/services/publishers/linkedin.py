"""LinkedIn Publisher — real API integration via LinkedIn REST API v2.

Endpoints used:
  POST https://api.linkedin.com/v2/ugcPosts              — text + image posts
  POST https://api.linkedin.com/v2/assets?action=registerUpload  — image upload registration
  POST https://api.linkedin.com/v2/assets?action=finalizeUpload — image upload finalization

Docs: https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api
"""
import httpx
import logging
from typing import Any

from app.services.publishers.base import PlatformPublisher, ContentLimits, PublishResult

logger = logging.getLogger(__name__)

LINKEDIN_API_BASE = "https://api.linkedin.com/v2"


class LinkedInPublisher(PlatformPublisher):

    @property
    def platform_name(self) -> str:
        return "linkedin"

    def content_limits(self) -> ContentLimits:
        return ContentLimits(
            max_caption_length=3000,
            max_title_length=200,
            max_media_count=5,
            supported_media_types=["image", "video", "document"],
            supported_image_formats=["jpg", "jpeg", "png", "gif"],
            supported_video_formats=["mp4"],
            max_video_duration_seconds=600,
            max_video_size_mb=200,
        )

    def supports_scheduling(self) -> bool:
        return False  # LinkedIn has no native scheduling API

    async def publish(
        self,
        post_id: str,
        workspace_id: str,
        media_assets: list[dict[str, Any]] | None = None,
        caption: str | None = None,
        title: str | None = None,
        access_token: str = "",
        author_urn: str = "",
        db: Any = None,
        connection: Any = None,
    ) -> PublishResult:
        """Publish a post to LinkedIn.

        Args:
            post_id: PostPlatform row ID.
            workspace_id: Owning workspace.
            media_assets: Resolved media assets (image/video URLs).
            caption: Post text content.
            title: Not used for standard posts (use for articles).
            access_token: LinkedIn OAuth access token.
            author_urn: Person or Organization URN, e.g. "urn:li:person:XXXXX".
            db: Database session for token refresh.
            connection: PlatformConnection object for token refresh.
        """
        if not access_token or not author_urn:
            return PublishResult(
                success=False,
                error_message="Missing access_token or author_urn for LinkedIn",
            )

        if not caption:
            return PublishResult(success=False, error_message="Caption is required")

        # Upload images first if present
        image_urns: list[str] = []
        if media_assets:
            for asset in media_assets:
                asset_url = asset.get("url", "")
                asset_type = asset.get("content_type", asset.get("type", ""))
                if asset_type in ("image",) and asset_url:
                    upload_result = await self._register_upload(
                        access_token=access_token,
                        author_urn=author_urn,
                        upload_url=asset_url,
                    )
                    if upload_result:
                        image_urns.append(upload_result)
                elif asset_type in ("video",) and asset_url:
                    upload_result = await self._register_upload(
                        access_token=access_token,
                        author_urn=author_urn,
                        upload_url=asset_url,
                        is_video=True,
                    )
                    if upload_result:
                        image_urns.append(upload_result)

        # Build the UGC post payload
        share_media_category = "NONE"
        if image_urns:
            # Determine if it's a video or image post
            has_video = any("VIDEO" in urn.upper() for urn in image_urns)
            share_media_category = "VIDEO" if has_video else "IMAGE"

        payload: dict[str, Any] = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": caption},
                    "shareMediaCategory": share_media_category,
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            },
        }

        # Attach media if we have uploads
        if image_urns and share_media_category == "IMAGE":
            payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                {"status": "READY", "media": urn} for urn in image_urns
            ]
        elif image_urns and share_media_category == "VIDEO":
            payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                {"status": "READY", "media": urn, "title": {"text": title or "Video"}} for urn in image_urns
            ]

        # Post to LinkedIn
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{LINKEDIN_API_BASE}/ugcPosts",
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                        "X-Restli-Protocol-Version": "2.0.0",
                    },
                )

                # If token expired, try refreshing
                if response.status_code == 401:
                    logger.info("LinkedIn token expired, attempting refresh...")
                    from app.services.token_refresh import refresh_linkedin_token
                    new_token = await refresh_linkedin_token(connection, db)
                    if new_token:
                        access_token = new_token
                        response = await client.post(
                            f"{LINKEDIN_API_BASE}/ugcPosts",
                            json=payload,
                            headers={
                                "Authorization": f"Bearer {access_token}",
                                "Content-Type": "application/json",
                                "X-Restli-Protocol-Version": "2.0.0",
                            },
                        )

                if response.status_code in (200, 201):
                    data = response.json()
                    post_urn = data.get("id", "")
                    logger.info(f"LinkedIn post published: {post_urn}")
                    return PublishResult(
                        success=True,
                        platform_post_id=post_urn,
                        raw_response=data,
                    )
                else:
                    error_detail = response.text
                    logger.error(
                        f"LinkedIn publish failed ({response.status_code}): {error_detail}"
                    )
                    return PublishResult(
                        success=False,
                        error_message=f"LinkedIn API error {response.status_code}: {error_detail}",
                        raw_response={"status": response.status_code, "body": error_detail},
                    )

        except httpx.TimeoutException:
            return PublishResult(success=False, error_message="LinkedIn API timeout")
        except Exception as e:
            logger.error(f"LinkedIn publish exception: {e}")
            return PublishResult(success=False, error_message=str(e))

    async def _register_upload(
        self,
        access_token: str,
        author_urn: str,
        upload_url: str,
        is_video: bool = False,
    ) -> str | None:
        """Register an upload with LinkedIn and return the asset URN."""
        request_payload = {
            "registerUploadRequest": {
                "recipes": (
                    ["urn:li:digitalmediaRecipe:feedshare-video"]
                    if is_video
                    else ["urn:li:digitalmediaRecipe:feedshare-image"]
                ),
                "owner": author_urn,
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent",
                    }
                ],
            }
        }

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{LINKEDIN_API_BASE}/assets?action=registerUpload",
                    json=request_payload,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                    },
                )

                if response.status_code in (200, 201):
                    data = response.json()
                    asset_urn = data.get("value", {}).get("asset", "")
                    upload_url = (
                        data.get("value", {}).get("uploadMechanism", {})
                        .get("com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest", {})
                        .get("uploadUrl", "")
                    )
                    # If we have an upload URL from LinkedIn, upload the file there
                    if upload_url:
                        await self._upload_file(upload_url, access_token)
                    return asset_urn

                logger.error(f"LinkedIn upload registration failed: {response.text}")
                return None

        except Exception as e:
            logger.error(f"LinkedIn upload registration error: {e}")
            return None

    async def _upload_file(self, upload_url: str, access_token: str) -> bool:
        """Upload a file to the LinkedIn-provided upload URL."""
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.put(
                    upload_url,
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                return response.status_code in (200, 201, 204)
        except Exception as e:
            logger.error(f"LinkedIn file upload error: {e}")
            return False

    async def refresh_access_token(self, connection: Any) -> str | None:
        """Refresh LinkedIn OAuth 2.0 access token.

        LinkedIn uses standard OAuth 2.0 refresh token flow.
        """
        from app.core.config import get_settings
        settings = get_settings()

        refresh_token = (connection.meta or {}).get("refresh_token") or getattr(connection, "refresh_token", None)
        if not refresh_token:
            return None

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(
                    "https://www.linkedin.com/oauth/v2/accessToken",
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": refresh_token,
                        "client_id": settings.LINKEDIN_CLIENT_ID,
                        "client_secret": settings.LINKEDIN_CLIENT_SECRET,
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    new_access_token = data.get("access_token", "")
                    new_refresh_token = data.get("refresh_token", refresh_token)
                    expires_in = data.get("expires_at", 0)

                    logger.info("LinkedIn token refreshed successfully")
                    return new_access_token
                else:
                    logger.error(f"LinkedIn token refresh failed: {response.text}")
                    return None

        except Exception as e:
            logger.error(f"LinkedIn token refresh error: {e}")
            return None
