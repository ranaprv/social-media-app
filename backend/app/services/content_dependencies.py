"""Content dependency scheduler — post A before post B.

Manages dependencies between posts so that certain content must be
published before others (e.g., teaser before announcement).
"""
import logging
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post_platform import PostPlatform

logger = logging.getLogger(__name__)


async def add_dependency(
    db: AsyncSession,
    workspace_id: str,
    post_id: str,
    depends_on_post_id: str,
) -> dict[str, Any]:
    """Add a dependency: post_id cannot be published until depends_on_post_id is published."""
    # Get both entries
    result = await db.execute(
        select(PostPlatform).where(
            PostPlatform.post_id == post_id,
            PostPlatform.workspace_id == workspace_id,
        )
    )
    items = result.scalars().all()

    if not items:
        return {"error": f"No platform entries found for post {post_id}"}

    # Check for circular dependencies
    if await _has_cycle(db, post_id, depends_on_post_id, workspace_id):
        return {"error": "Adding this dependency would create a circular reference"}

    # Store dependency in metadata
    for item in items:
        meta = item.meta or {}
        deps = meta.get("depends_on", [])
        if depends_on_post_id not in deps:
            deps.append(depends_on_post_id)
        meta["depends_on"] = deps
        item.meta = meta

    await db.flush()

    return {
        "post_id": post_id,
        "depends_on": depends_on_post_id,
        "message": f"Post {post_id} now depends on {depends_on_post_id}",
    }


async def remove_dependency(
    db: AsyncSession,
    workspace_id: str,
    post_id: str,
    depends_on_post_id: str,
) -> dict[str, Any]:
    """Remove a dependency between two posts."""
    result = await db.execute(
        select(PostPlatform).where(
            PostPlatform.post_id == post_id,
            PostPlatform.workspace_id == workspace_id,
        )
    )
    items = result.scalars().all()

    for item in items:
        meta = item.meta or {}
        deps = meta.get("depends_on", [])
        if depends_on_post_id in deps:
            deps.remove(depends_on_post_id)
        meta["depends_on"] = deps
        item.meta = meta

    await db.flush()

    return {
        "post_id": post_id,
        "removed_dependency": depends_on_post_id,
    }


async def get_dependencies(
    db: AsyncSession,
    workspace_id: str,
    post_id: str,
) -> dict[str, Any]:
    """Get all dependencies for a post (what it depends on and what depends on it)."""
    # What does this post depend on?
    result = await db.execute(
        select(PostPlatform).where(
            PostPlatform.post_id == post_id,
            PostPlatform.workspace_id == workspace_id,
        )
    )
    items = result.scalars().all()

    depends_on: list[str] = []
    for item in items:
        meta = item.meta or {}
        deps = meta.get("depends_on", [])
        depends_on.extend(deps)
    depends_on = list(set(depends_on))

    # What depends on this post?
    all_result = await db.execute(
        select(PostPlatform).where(
            PostPlatform.workspace_id == workspace_id,
        )
    )
    all_items = all_result.scalars().all()

    depended_on_by: list[str] = []
    for item in all_items:
        meta = item.meta or {}
        deps = meta.get("depends_on", [])
        if post_id in deps:
            depended_on_by.append(item.post_id)
    depended_on_by = list(set(depended_on_by))

    return {
        "post_id": post_id,
        "depends_on": depends_on,
        "depended_on_by": depended_on_by,
    }


async def check_dependencies_met(
    db: AsyncSession,
    post_id: str,
) -> dict[str, Any]:
    """Check if all dependencies for a post are met (all deps published)."""
    result = await db.execute(
        select(PostPlatform).where(PostPlatform.post_id == post_id)
    )
    items = result.scalars().all()

    all_deps: list[str] = []
    for item in items:
        meta = item.meta or {}
        all_deps.extend(meta.get("depends_on", []))
    all_deps = list(set(all_deps))

    if not all_deps:
        return {"met": True, "missing": []}

    # Check if dependency posts are published
    missing: list[str] = []
    for dep_id in all_deps:
        dep_result = await db.execute(
            select(PostPlatform.status).where(
                PostPlatform.post_id == dep_id,
                PostPlatform.status == "published",
            ).limit(1)
        )
        if not dep_result.scalar_one():
            missing.append(dep_id)

    return {
        "met": len(missing) == 0,
        "missing": missing,
        "total_deps": len(all_deps),
    }


async def _has_cycle(
    db: AsyncSession,
    from_post: str,
    to_post: str,
    workspace_id: str,
) -> bool:
    """Check if adding from_post -> to_post would create a cycle."""
    # BFS from to_post to see if we can reach from_post
    visited = set()
    queue = [to_post]

    while queue:
        current = queue.pop(0)
        if current == from_post:
            return True
        if current in visited:
            continue
        visited.add(current)

        # Get what current depends on
        result = await db.execute(
            select(PostPlatform).where(
                PostPlatform.post_id == current,
                PostPlatform.workspace_id == workspace_id,
            )
        )
        items = result.scalars().all()
        for item in items:
            meta = item.meta or {}
            deps = meta.get("depends_on", [])
            queue.extend(deps)

    return False
