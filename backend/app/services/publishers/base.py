"""PlatformPublisher — abstract base defining the contract all platform publishers must satisfy."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ContentLimits:
    """Platform-specific content constraints."""
    max_caption_length: int
    max_title_length: int = 0
    max_media_count: int = 0
    supported_media_types: list[str] = field(default_factory=list)
    supported_video_formats: list[str] = field(default_factory=list)
    supported_image_formats: list[str] = field(default_factory=list)
    max_video_duration_seconds: int = 0
    max_video_size_mb: int = 0


@dataclass
class PublishResult:
    """Outcome of a publish attempt."""
    success: bool
    platform_post_id: str = ""
    error_message: str = ""
    raw_response: dict = field(default_factory=dict)


class PlatformPublisher(ABC):
    """Contract every platform publisher must implement."""

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Canonical platform key (linkedin, x, instagram, facebook, youtube)."""
        ...

    @abstractmethod
    def content_limits(self) -> ContentLimits:
        """Return platform-specific content constraints."""
        ...

    @abstractmethod
    def supports_scheduling(self) -> bool:
        """True if the platform has a native scheduling API (YouTube does)."""
        ...

    @abstractmethod
    async def publish(
        self,
        post_id: str,
        workspace_id: str,
        media_assets: list[dict[str, Any]] | None = None,
        caption: str | None = None,
        title: str | None = None,
    ) -> PublishResult:
        """Publish immediately to the platform.

        Args:
            post_id: PostPlatform row ID.
            workspace_id: Owning workspace.
            media_assets: Resolved media from the platform directory.
            caption: Platform-specific caption override (else parent Post content).
            title: Optional title (YouTube, LinkedIn articles).
        """
        ...

    @abstractmethod
    async def refresh_access_token(self, connection: Any) -> str | None:
        """Attempt to refresh an expired access token. Returns new token or None."""
        ...

    def validate_content(self, caption: str, media_count: int) -> list[str]:
        """Validate content against platform limits. Returns list of error messages (empty = OK)."""
        limits = self.content_limits()
        errors: list[str] = []

        if len(caption) > limits.max_caption_length:
            errors.append(
                f"Caption exceeds {limits.max_caption_length} chars "
                f"(got {len(caption)})"
            )
        if media_count > limits.max_media_count:
            errors.append(
                f"Too many media files: {media_count} (max {limits.max_media_count})"
            )

        return errors
