"""Resolve media assets from platform-specific directories.

When a post is scheduled for a platform, this module finds the right
assets from the media library's platform directory.
"""
import logging
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.content import Asset

logger = logging.getLogger(__name__)

# Content types accepted per platform for media attachment
PLATFORM_MEDIA_TYPES: dict[str, list[str]] = {
    "youtube": ["video", "image"],
    "instagram": ["reel", "carousel", "vertical_video", "image"],
    "linkedin": ["carousel", "video", "document"],
    "facebook": ["image", "video"],
}


async def resolve_platform_media(
    db: AsyncSession,
    workspace_id: str,
    platform: str,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Find media assets assigned to a platform directory.

    Queries the assets table for records matching the platform, ordered by
    creation date (newest first). Returns asset metadata dicts suitable
    for the publisher to upload.
    """
    accepted_types = PLATFORM_MEDIA_TYPES.get(platform, [])
    if not accepted_types:
        logger.warning("No media types defined for platform %s", platform)
        return []

    result = await db.execute(
        select(Asset)
        .where(
            Asset.workspace_id == workspace_id,
            Asset.platform == platform,
            Asset.content_type.in_(accepted_types),
        )
        .order_by(Asset.created_at.desc())
        .limit(limit)
    )
    assets = result.scalars().all()

    media = []
    for a in assets:
        media.append({
            "id": a.id,
            "name": a.name,
            "url": a.url,
            "type": a.type,
            "platform": a.platform,
            "content_type": a.content_type,
            "mime_type": (a.meta or {}).get("mime_type", ""),
            "size": (a.meta or {}).get("size", 0),
        })

    logger.info(
        "Resolved %d media assets for platform=%s workspace=%s",
        len(media),
        platform,
        workspace_id,
    )
    return media
