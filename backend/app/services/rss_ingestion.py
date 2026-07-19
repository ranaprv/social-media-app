"""RSS content ingestion — auto-create posts from RSS feeds.

Monitors RSS/Atom feeds and creates draft posts when new items appear.
"""
import logging
import uuid
from datetime import datetime
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Post
from app.models.post_platform import PostPlatform

logger = logging.getLogger(__name__)


async def ingest_rss_feed(
    db: AsyncSession,
    workspace_id: str,
    feed_url: str,
    author_id: str,
    platforms: list[str] | None = None,
    auto_schedule: bool = False,
) -> dict[str, Any]:
    """Fetch and parse an RSS feed, creating draft posts for new items.

    Returns summary of created posts.
    """
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(feed_url)
            if response.status_code != 200:
                return {"error": f"Failed to fetch feed: HTTP {response.status_code}"}

            content = response.text
    except Exception as e:
        return {"error": f"Feed fetch failed: {str(e)}"}

    # Parse RSS/Atom (simple XML parsing)
    items = _parse_feed(content)
    if not items:
        return {"error": "No items found in feed", "items": 0}

    created = []
    target_platforms = platforms or ["linkedin"]

    for item in items[:10]:  # Limit to 10 items per feed
        title = item.get("title", "")
        description = item.get("description", item.get("content", ""))
        link = item.get("link", "")

        # Create Post
        post = Post(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            author_id=author_id,
            title=title,
            content=description[:2000] if description else "",
            platform=target_platforms[0],
            status="draft",
            meta={"source": "rss", "feed_url": feed_url, "link": link},
        )
        db.add(post)

        # Create PostPlatform entries
        for platform in target_platforms:
            pp = PostPlatform(
                id=str(uuid.uuid4()),
                post_id=post.id,
                workspace_id=workspace_id,
                platform=platform,
                status="scheduled" if auto_schedule else "draft",
            )
            db.add(pp)

        created.append({
            "post_id": post.id,
            "title": title[:80],
            "platforms": target_platforms,
        })

    await db.flush()

    return {
        "feed_url": feed_url,
        "items_found": len(items),
        "posts_created": len(created),
        "auto_scheduled": auto_schedule,
        "posts": created,
    }


def _parse_feed(content: str) -> list[dict[str, str]]:
    """Simple RSS/Atom feed parser.

    For production, use a proper XML parser like feedparser.
    This handles basic RSS 2.0 and Atom feeds.
    """
    items = []

    # Try RSS 2.0 format
    import re
    item_pattern = re.compile(r"<item>(.*?)</item>", re.DOTALL | re.IGNORECASE)
    items_raw = item_pattern.findall(content)

    for item_raw in items_raw:
        item: dict[str, str] = {}

        title_match = re.search(r"<title>(.*?)</title>", item_raw, re.DOTALL)
        if title_match:
            item["title"] = _clean_xml(title_match.group(1))

        desc_match = re.search(r"<description>(.*?)</description>", item_raw, re.DOTALL)
        if desc_match:
            item["description"] = _clean_xml(desc_match.group(1))

        link_match = re.search(r"<link>(.*?)</link>", item_raw, re.DOTALL)
        if link_match:
            item["link"] = link_match.group(1).strip()

        content_match = re.search(r"<content:(?:encoded|rss)>(.*?)</content:(?:encoded|rss)>", item_raw, re.DOTALL)
        if content_match:
            item["content"] = _clean_xml(content_match.group(1))

        if item.get("title"):
            items.append(item)

    # Try Atom format if no RSS items found
    if not items:
        entry_pattern = re.compile(r"<entry>(.*?)</entry>", re.DOTALL | re.IGNORECASE)
        entries = entry_pattern.findall(content)
        for entry_raw in entries:
            item = {}
            title_match = re.search(r"<title>(.*?)</title>", entry_raw, re.DOTALL)
            if title_match:
                item["title"] = _clean_xml(title_match.group(1))

            summary_match = re.search(r"<summary>(.*?)</summary>", entry_raw, re.DOTALL)
            if summary_match:
                item["description"] = _clean_xml(summary_match.group(1))

            link_match = re.search(r'<link[^>]*href="([^"]*)"', entry_raw)
            if link_match:
                item["link"] = link_match.group(1)

            if item.get("title"):
                items.append(item)

    return items


def _clean_xml(text: str) -> str:
    """Remove XML tags and decode entities."""
    import re
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&quot;", '"').replace("&#39;", "'")
    text = text.strip()
    return text
