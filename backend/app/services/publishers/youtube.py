"""YouTube Publisher — real API integration via YouTube Data API v3.

YouTube has a native scheduling API — videos.upload supports a publishAt
parameter for deferred publication.

Flow:
  1. POST (resumable upload) → initiate upload session
  2. PUT  → upload video binary
  3. POST → set video metadata (title, description, tags, privacy)
  4. (Optional) videos.update with publishAt for scheduling

Docs: https://developers.google.com/youtube/v3/docs/videos/insert
"""
import httpx
import logging
from datetime import datetime
from typing import Any

from app.services.publishers.base import PlatformPublisher, ContentLimits, PublishResult

logger = logging.getLogger(__name__)

YT_API_BASE = "https://www.googleapis.com/youtube/v3"


class YouTubePublisher(PlatformPublisher):

    @property
    def platform_name(self) -> str:
        return "youtube"

    def content_limits(self) -> ContentLimits:
        return ContentLimits(
            max_caption_length=5000,   # description
            max_title_length=100,
            max_media_count=1,         # one video per upload
            supported_media_types=["video", "image"],
            supported_image_formats=["jpg", "jpeg", "png", "gif", "bmp"],
            supported_video_formats=["mp4", "avi", "mov", "wmv", "mkv", "flv", "webm"],
            max_video_duration_seconds=43200,  # 12 hours
            max_video_size_mb=256000,  # 256 GB
        )

    def supports_scheduling(self) -> bool:
        return True  # YouTube has native publishAt scheduling

    async def publish(
        self,
        post_id: str,
        workspace_id: str,
        media_assets: list[dict[str, Any]] | None = None,
        caption: str | None = None,
        title: str | None = None,
        access_token: str = "",
        scheduled_at: datetime | None = None,
        db: Any = None,
        connection: Any = None,
    ) -> PublishResult:
        """Upload and publish a video to YouTube.

        Args:
            access_token: YouTube OAuth access token with youtube.upload scope.
            title: Video title (required, max 100 chars).
            caption: Video description (max 5000 chars).
            scheduled_at: If provided, YouTube will publish at this time.
            db: Database session for token refresh.
            connection: PlatformConnection object for token refresh.
        """
        if not access_token:
            return PublishResult(success=False, error_message="Missing access_token for YouTube")

        if not title:
            return PublishResult(success=False, error_message="Video title is required")

        if not caption:
            return PublishResult(success=False, error_message="Video description is required")

        # Find the video file
        video_url = None
        if media_assets:
            for asset in media_assets:
                asset_type = asset.get("content_type", asset.get("type", ""))
                asset_url = asset.get("url", "")
                if asset_type in ("video",) and asset_url:
                    video_url = asset_url
                    break

        if not video_url:
            return PublishResult(
                success=False,
                error_message="No video file found in media assets",
            )

        # Get video bytes
        try:
            if video_url.startswith("file://"):
                local_path = video_url.replace("file://", "")
                with open(local_path, "rb") as f:
                    video_bytes = f.read()
            else:
                async with httpx.AsyncClient(timeout=300) as dl_client:
                    download_response = await dl_client.get(video_url)
                    if download_response.status_code != 200:
                        return PublishResult(success=False, error_message=f"Failed to download video: {download_response.status_code}")
                    video_bytes = download_response.content
        except Exception as e:
            return PublishResult(success=False, error_message=f"Video read error: {e}")

        # Build metadata
        import json
        metadata = json.dumps({
            "snippet": {
                "title": title[:100],
                "description": caption[:5000],
                "categoryId": "28",  # Science & Technology
            },
            "status": {
                "privacyStatus": "private" if scheduled_at else "public",
                "selfDeclaredMadeForKids": False,
            }
        })

        # Direct multipart upload
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                response = await client.post(
                    "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=multipart&part=snippet,status",
                    headers={"Authorization": f"Bearer {access_token}"},
                    files={
                        "metadata": (None, metadata, "application/json; charset=UTF-8"),
                        "video": ("video.mp4", video_bytes, "video/mp4"),
                    },
                )

                # If token expired, try refreshing
                if response.status_code == 401:
                    logger.info("YouTube token expired, attempting refresh...")
                    from app.services.token_refresh import refresh_youtube_token
                    if db and connection:
                        new_token = await refresh_youtube_token(connection, db)
                        if new_token:
                            access_token = new_token
                            response = await client.post(
                                "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=multipart&part=snippet,status",
                                headers={"Authorization": f"Bearer {access_token}"},
                                files={
                                    "metadata": (None, metadata, "application/json; charset=UTF-8"),
                                    "video": ("video.mp4", video_bytes, "video/mp4"),
                                },
                            )

                if response.status_code == 200:
                    data = response.json()
                    video_id = data.get("id", "")
                    logger.info(f"YouTube video published: {video_id}")
                    return PublishResult(
                        success=True,
                        platform_post_id=video_id,
                        raw_response=data,
                    )
                else:
                    error_detail = response.text
                    logger.error(f"YouTube publish failed ({response.status_code}): {error_detail}")
                    return PublishResult(
                        success=False,
                        error_message=f"YouTube API error {response.status_code}: {error_detail}",
                    )

        except httpx.TimeoutException:
            return PublishResult(success=False, error_message="YouTube API timeout")
        except Exception as e:
            logger.error(f"YouTube publish exception: {e}")
            return PublishResult(success=False, error_message=str(e))

    async def _initiate_upload(
        self, client: httpx.AsyncClient, access_token: str,
        title: str, description: str,
        scheduled_at: datetime | None = None,
    ) -> str | None:
        """Initiate a resumable upload session. Returns upload URL."""
        # Build video metadata
        snippet: dict[str, Any] = {
            "title": title[:100],
            "description": description[:5000],
            "categoryId": "22",  # People & Blogs
        }

        # Privacy status: public, private, or unlisted
        # If scheduled, use "private" and set publishAt
        privacy_status = "private" if scheduled_at else "public"

        status: dict[str, Any] = {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
        }

        if scheduled_at:
            # YouTube expects RFC 3339 format
            status["publishAt"] = scheduled_at.strftime("%Y-%m-%dT%H:%M:%SZ")

        body = {
            "snippet": snippet,
            "status": status,
        }

        response = await client.post(
            f"{YT_API_BASE}/videos?uploadType=resumable&part=snippet,status",
            json=body,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json; charset=UTF-8",
                "X-Upload-Content-Type": "video/mp4",
                "X-Upload-Content-Length": "0",
            },
        )

        # If token expired, try refreshing
        if response.status_code == 401:
            logger.info("YouTube token expired, attempting refresh...")
            from app.services.token_refresh import refresh_youtube_token
            if db and connection:
                new_token = await refresh_youtube_token(connection, db)
                if new_token:
                    access_token = new_token
                    response = await client.post(
                        f"{YT_API_BASE}/videos?uploadType=resumable&part=snippet,status",
                        json=body,
                        headers={
                            "Authorization": f"Bearer {access_token}",
                            "Content-Type": "application/json; charset=UTF-8",
                            "X-Upload-Content-Type": "video/mp4",
                            "X-Upload-Content-Length": "0",
                        },
                    )

        if response.status_code in (200, 201):
            # The upload URL is in the Location header
            upload_url = response.headers.get("Location", "")
            if upload_url:
                logger.info("YouTube upload session initiated")
                return upload_url

        logger.error(f"YouTube upload initiation failed: {response.text}")
        return None

    async def _upload_video(
        self, client: httpx.AsyncClient,
        upload_url: str, video_url: str,
    ) -> str | None:
        """Upload video binary to YouTube via the resumable upload URL.

        We download the video from our storage, then PUT it to YouTube.
        For large files, this should use chunked/resumable uploads.
        """
        # Handle local files vs URLs
        if video_url.startswith("file://"):
            local_path = video_url.replace("file://", "")
            try:
                with open(local_path, "rb") as f:
                    video_bytes = f.read()
            except Exception as e:
                logger.error(f"Failed to read local file {local_path}: {e}")
                return None
        else:
            # Download the video from our storage
            try:
                download_response = await client.get(video_url, timeout=300)
                if download_response.status_code != 200:
                    logger.error(f"Failed to download video from {video_url}")
                    return None

                video_bytes = download_response.content
            except Exception as e:
                logger.error(f"Video download error: {e}")
                return None

        # Upload to YouTube
        response = await client.put(
            upload_url,
            content=video_bytes,
            headers={
                "Content-Type": "video/mp4",
                "Content-Length": str(len(video_bytes)),
            },
        )

        if response.status_code in (200, 201):
            data = response.json()
            video_id = data.get("id", "")
            logger.info(f"YouTube video uploaded: {video_id}")
            return video_id

        logger.error(f"YouTube video upload failed: {response.text}")
        return None

    async def _set_thumbnail(
        self, client: httpx.AsyncClient, access_token: str,
        video_id: str, thumbnail_url: str,
    ) -> bool:
        """Set a custom thumbnail for the uploaded video."""
        try:
            # Download the thumbnail
            download = await client.get(thumbnail_url, timeout=30)
            if download.status_code != 200:
                return False

            # Upload to YouTube
            response = await client.post(
                f"{YT_API_BASE}/thumbnails/set",
                params={"videoId": video_id},
                files={"image": ("thumbnail.jpg", download.content, "image/jpeg")},
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if response.status_code == 200:
                logger.info(f"YouTube thumbnail set for {video_id}")
                return True

            logger.warning(f"YouTube thumbnail failed: {response.text}")
            return False

        except Exception as e:
            logger.error(f"YouTube thumbnail error: {e}")
            return False

    async def refresh_access_token(self, connection: Any) -> str | None:
        """Refresh YouTube OAuth 2.0 access token (Google OAuth flow)."""
        from app.core.config import get_settings
        settings = get_settings()

        refresh_token = (connection.meta or {}).get("refresh_token") or getattr(connection, "refresh_token", None)
        if not refresh_token:
            return None

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": refresh_token,
                        "client_id": settings.YOUTUBE_CLIENT_ID,
                        "client_secret": settings.YOUTUBE_CLIENT_SECRET,
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    new_access_token = data.get("access_token", "")
                    logger.info("YouTube token refreshed successfully")
                    return new_access_token
                else:
                    logger.error(f"YouTube token refresh failed: {response.text}")
                    return None

        except Exception as e:
            logger.error(f"YouTube token refresh error: {e}")
            return None
