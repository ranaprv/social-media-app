"""Publisher factory — resolves platform string to publisher instance.

All 5 core platforms now have real API implementations:
  LinkedIn, X/Twitter, Instagram, Facebook, YouTube.
"""
from app.services.publishers.base import PlatformPublisher
from app.services.publishers.linkedin import LinkedInPublisher
from app.services.publishers.twitter import TwitterPublisher
from app.services.publishers.facebook import FacebookPublisher
from app.services.publishers.instagram import InstagramPublisher
from app.services.publishers.youtube import YouTubePublisher

_PUBLISHER_REGISTRY: dict[str, type[PlatformPublisher]] = {
    "linkedin": LinkedInPublisher,
    "x": TwitterPublisher,
    "facebook": FacebookPublisher,
    "instagram": InstagramPublisher,
    "youtube": YouTubePublisher,
}


def get_publisher(platform: str) -> PlatformPublisher | None:
    """Get a publisher instance for the given platform."""
    cls = _PUBLISHER_REGISTRY.get(platform)
    return cls() if cls else None


def get_all_publishers() -> dict[str, PlatformPublisher]:
    """Get instances of all registered publishers."""
    return {name: cls() for name, cls in _PUBLISHER_REGISTRY.items()}


def register_publisher(platform: str, publisher_cls: type[PlatformPublisher]):
    """Register a new platform publisher."""
    _PUBLISHER_REGISTRY[platform] = publisher_cls
