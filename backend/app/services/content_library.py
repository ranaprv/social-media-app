"""Content library — save, tag, organize reusable content.

Stores successful posts as library entries that can be searched,
tagged, and reused across workspaces.
"""
import logging
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select, func, desc, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Post
from app.models.post_platform import PostPlatform

logger = logging.getLogger(__name__)


async def save_to_library(
    db: AsyncSession,
    workspace_id: str,
    post_id: str,
    tags: list[str] | None = None,
    category: str = "general",
    notes: str = "",
) -> dict[str, Any]:
    """Save a published post to the content library."""
    result = await db.execute(
        select(Post).where(Post.id == post_id, Post.workspace_id == workspace_id)
    )
    post = result.scalar_one_none()
    if not post:
        return {"error": f"Post {post_id} not found"}

    meta = post.meta or {}
    meta["in_library"] = True
    meta["library_saved_at"] = datetime.utcnow().isoformat()
    meta["library_tags"] = tags or []
    meta["library_category"] = category
    meta["library_notes"] = notes

    # Get platform performance data
    pp_result = await db.execute(
        select(PostPlatform.platform, PostPlatform.status, PostPlatform.published_at)
        .where(PostPlatform.post_id == post_id)
    )
    platforms = [
        {"platform": pp[0], "status": pp[1], "published_at": pp[2].isoformat() if pp[2] else None}
        for pp in pp_result.all()
    ]
    meta["library_platforms"] = platforms

    post.meta = meta
    await db.flush()

    return {
        "post_id": post_id,
        "category": category,
        "tags": tags or [],
        "platforms": [p["platform"] for p in platforms],
    }


async def search_library(
    db: AsyncSession,
    workspace_id: str,
    query: str | None = None,
    category: str | None = None,
    platform: str | None = None,
    tags: list[str] | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    """Search the content library."""
    result = await db.execute(
        select(Post).where(
            Post.workspace_id == workspace_id,
            Post.meta["in_library"].as_bool() == True,
        )
    )
    all_posts = result.scalars().all()

    # Filter
    filtered = []
    for post in all_posts:
        meta = post.meta or {}

        # Text search
        if query:
            searchable = f"{post.title or ''} {post.content or ''}".lower()
            if query.lower() not in searchable:
                continue

        # Category filter
        if category and meta.get("library_category") != category:
            continue

        # Tag filter
        if tags:
            post_tags = set(meta.get("library_tags", []))
            if not set(tags).intersection(post_tags):
                continue

        # Platform filter
        if platform:
            post_platforms = [p["platform"] for p in meta.get("library_platforms", [])]
            if platform not in post_platforms:
                continue

        filtered.append({
            "id": post.id,
            "title": post.title,
            "content_preview": (post.content or "")[:200],
            "platform": post.platform,
            "category": meta.get("library_category", "general"),
            "tags": meta.get("library_tags", []),
            "platforms": meta.get("library_platforms", []),
            "saved_at": meta.get("library_saved_at"),
            "notes": meta.get("library_notes", ""),
        })

    # Sort by saved_at
    filtered.sort(key=lambda x: x.get("saved_at") or "", reverse=True)

    total = len(filtered)
    paginated = filtered[offset:offset + limit]

    # Get categories
    categories = list(set(
        (p.meta or {}).get("library_category", "general")
        for p in all_posts
    ))

    # Get all tags
    all_tags: set[str] = set()
    for p in all_posts:
        all_tags.update((p.meta or {}).get("library_tags", []))

    return {
        "items": paginated,
        "total": total,
        "offset": offset,
        "limit": limit,
        "categories": sorted(categories),
        "tags": sorted(all_tags),
    }


async def remove_from_library(
    db: AsyncSession,
    workspace_id: str,
    post_id: str,
) -> dict[str, Any]:
    """Remove a post from the content library."""
    result = await db.execute(
        select(Post).where(Post.id == post_id, Post.workspace_id == workspace_id)
    )
    post = result.scalar_one_none()
    if not post:
        return {"error": f"Post {post_id} not found"}

    meta = post.meta or {}
    meta["in_library"] = False
    post.meta = meta
    await db.flush()

    return {"post_id": post_id, "message": "Removed from library"}


async def get_library_stats(
    db: AsyncSession,
    workspace_id: str,
) -> dict[str, Any]:
    """Get content library statistics."""
    result = await db.execute(
        select(Post).where(
            Post.workspace_id == workspace_id,
            Post.meta["in_library"].as_bool() == True,
        )
    )
    posts = result.scalars().all()

    categories: dict[str, int] = {}
    platform_counts: dict[str, int] = {}
    all_tags: dict[str, int] = {}

    for post in posts:
        meta = post.meta or {}
        cat = meta.get("library_category", "general")
        categories[cat] = categories.get(cat, 0) + 1
        for p in meta.get("library_platforms", []):
            plat = p.get("platform", "unknown")
            platform_counts[plat] = platform_counts.get(plat, 0) + 1
        for tag in meta.get("library_tags", []):
            all_tags[tag] = all_tags.get(tag, 0) + 1

    return {
        "total_items": len(posts),
        "by_category": categories,
        "by_platform": platform_counts,
        "top_tags": dict(sorted(all_tags.items(), key=lambda x: x[1], reverse=True)[:20]),
    }
