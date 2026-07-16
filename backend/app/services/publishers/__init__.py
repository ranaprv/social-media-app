"""Base publisher interface and factory."""
from abc import ABC, abstractmethod
from typing import Any


class BasePublisher(ABC):
    """Abstract base for platform publishers."""

    @abstractmethod
    async def publish(
        self,
        post_id: str,
        workspace_id: str,
        media_assets: list[dict[str, Any]] | None = None,
    ) -> dict:
        """Publish a post. Returns result dict with platform_post_id.

        Args:
            post_id: The post ID to publish.
            workspace_id: The workspace owning the post.
            media_assets: Resolved media from platform directory (optional).
        """
        ...


def get_publisher(platform: str) -> BasePublisher | None:
    """Get publisher instance for a platform."""
    publishers = {
        "linkedin": LinkedInPublisher,
        "x": TwitterPublisher,
        "instagram": InstagramPublisher,
        "facebook": FacebookPublisher,
        "youtube": YouTubePublisher,
    }
    cls = publishers.get(platform)
    return cls() if cls else None


class LinkedInPublisher(BasePublisher):
    async def publish(self, post_id: str, workspace_id: str, media_assets: list[dict[str, Any]] | None = None) -> dict:
        # TODO: Implement LinkedIn API post creation
        # If media_assets provided, upload images/documents as part of the post
        return {"platform_post_id": "mock-linkedin-id", "status": "published"}


class TwitterPublisher(BasePublisher):
    async def publish(self, post_id: str, workspace_id: str, media_assets: list[dict[str, Any]] | None = None) -> dict:
        # TODO: Implement X/Twitter API tweet posting
        return {"platform_post_id": "mock-twitter-id", "status": "published"}


class InstagramPublisher(BasePublisher):
    async def publish(self, post_id: str, workspace_id: str, media_assets: list[dict[str, Any]] | None = None) -> dict:
        # TODO: Implement Instagram Graph API publishing
        return {"platform_post_id": "mock-instagram-id", "status": "published"}


class FacebookPublisher(BasePublisher):
    async def publish(self, post_id: str, workspace_id: str, media_assets: list[dict[str, Any]] | None = None) -> dict:
        # TODO: Implement Facebook Graph API publishing
        return {"platform_post_id": "mock-facebook-id", "status": "published"}


class YouTubePublisher(BasePublisher):
    async def publish(self, post_id: str, workspace_id: str, media_assets: list[dict[str, Any]] | None = None) -> dict:
        # TODO: Implement YouTube Data API v3 upload
        return {"platform_post_id": "mock-youtube-id", "status": "published"}
