"""Content versioning — snapshot + rollback for posts.

Creates version snapshots of post content and platform configurations
before each publish attempt, enabling rollback to any previous version.
"""
import logging
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Post, PostVersion
from app.models.post_platform import PostPlatform

logger = logging.getLogger(__name__)


async def create_snapshot(
    db: AsyncSession,
    post_id: str,
    author_id: str,
    change_note: str = "",
) -> dict[str, Any]:
    """Create a version snapshot of a post and its platform entries.

    Captures the current state of:
      - Post content, title, media URLs
      - All PostPlatform entries (captions, status, schedule)

    Returns the version number.
    """
    # Get the post
    post_result = await db.execute(
        select(Post).where(Post.id == post_id)
    )
    post = post_result.scalar_one_none()
    if not post:
        return {"error": f"Post {post_id} not found"}

    # Get current version number
    version_result = await db.execute(
        select(func.max(PostVersion.version))
        .where(PostVersion.post_id == post_id)
    )
    max_version = version_result.scalar() or 0
    new_version = max_version + 1

    # Get all platform entries
    pp_result = await db.execute(
        select(PostPlatform).where(PostPlatform.post_id == post_id)
    )
    platforms = pp_result.scalars().all()

    # Build snapshot content
    snapshot = {
        "title": post.title,
        "content": post.content,
        "media_urls": post.media_urls or [],
        "platform": post.platform,
        "platforms": [
            {
                "id": pp.id,
                "platform": pp.platform,
                "caption": pp.caption,
                "media_asset_ids": pp.media_asset_ids or [],
                "title": pp.title,
                "status": pp.status,
                "scheduled_at": pp.scheduled_at.isoformat() if pp.scheduled_at else None,
            }
            for pp in platforms
        ],
    }

    # Create version record
    version = PostVersion(
        id=str(uuid.uuid4()),
        post_id=post_id,
        content=str(snapshot),  # Serialized snapshot
        version=new_version,
        author_id=author_id,
    )
    db.add(version)
    await db.flush()

    logger.info(f"Created version {new_version} for post {post_id}")

    return {
        "version": new_version,
        "post_id": post_id,
        "snapshot": snapshot,
        "change_note": change_note,
    }


async def get_version_history(
    db: AsyncSession,
    post_id: str,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Get version history for a post."""
    result = await db.execute(
        select(PostVersion)
        .where(PostVersion.post_id == post_id)
        .order_by(PostVersion.version.desc())
        .limit(limit)
    )
    versions = result.scalars().all()

    return [
        {
            "version": v.version,
            "author_id": v.author_id,
            "created_at": v.created_at.isoformat() if v.created_at else None,
            "content_preview": v.content[:200] + "..." if len(v.content or "") > 200 else v.content,
        }
        for v in versions
    ]


async def rollback_to_version(
    db: AsyncSession,
    post_id: str,
    target_version: int,
    author_id: str,
) -> dict[str, Any]:
    """Rollback a post to a previous version.

    Restores the post content and platform entries from the snapshot.
    Creates a new version recording the rollback.
    """
    # Get the target version
    version_result = await db.execute(
        select(PostVersion).where(
            PostVersion.post_id == post_id,
            PostVersion.version == target_version,
        )
    )
    version = version_result.scalar_one_none()
    if not version:
        return {"error": f"Version {target_version} not found for post {post_id}"}

    # Parse the snapshot
    import ast
    try:
        snapshot = ast.literal_eval(version.content)
    except (ValueError, SyntaxError):
        return {"error": "Invalid version snapshot data"}

    # Get the post
    post_result = await db.execute(
        select(Post).where(Post.id == post_id)
    )
    post = post_result.scalar_one_none()
    if not post:
        return {"error": f"Post {post_id} not found"}

    # Restore post content
    post.title = snapshot.get("title", post.title)
    post.content = snapshot.get("content", post.content)
    post.media_urls = snapshot.get("media_urls", post.media_urls)

    # Restore platform entries
    for pp_data in snapshot.get("platforms", []):
        pp_id = pp_data.get("id")
        if pp_id:
            pp_result = await db.execute(
                select(PostPlatform).where(PostPlatform.id == pp_id)
            )
            pp = pp_result.scalar_one_none()
            if pp:
                pp.caption = pp_data.get("caption", pp.caption)
                pp.media_asset_ids = pp_data.get("media_asset_ids", pp.media_asset_ids)
                pp.title = pp_data.get("title", pp.title)

    # Create a new version for the rollback
    await create_snapshot(db, post_id, author_id, f"Rollback to version {target_version}")

    await db.flush()

    return {
        "post_id": post_id,
        "rolled_back_to": target_version,
        "message": f"Post restored to version {target_version}",
    }
