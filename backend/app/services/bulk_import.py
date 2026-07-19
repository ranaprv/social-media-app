"""Bulk import service — import content from CSV/Google Sheets.

Supports importing scheduled posts from CSV files with
platform mapping and validation.
"""
import csv
import io
import logging
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def import_from_csv(
    db: AsyncSession,
    workspace_id: str,
    csv_content: str,
    author_id: str,
    platform: str = "linkedin",
    auto_schedule: bool = False,
) -> dict[str, Any]:
    """Import posts from CSV content.

    Expected CSV columns: title, content, platform, scheduled_at, tags
    """
    try:
        reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(reader)
    except Exception as e:
        return {"error": f"CSV parsing failed: {str(e)}"}

    if not rows:
        return {"error": "CSV is empty"}

    from app.models.content import Post
    from app.models.post_platform import PostPlatform

    created = []
    errors = []

    for i, row in enumerate(rows):
        try:
            title = row.get("title", "")
            content = row.get("content", "")
            target_platform = row.get("platform", platform)
            scheduled_at_str = row.get("scheduled_at", "")
            tags = row.get("tags", "").split(",") if row.get("tags") else []

            if not content:
                errors.append(f"Row {i + 1}: Missing content")
                continue

            # Parse scheduled time
            scheduled_at = None
            if scheduled_at_str:
                try:
                    scheduled_at = datetime.fromisoformat(scheduled_at_str.replace("Z", "+00:00"))
                except ValueError:
                    errors.append(f"Row {i + 1}: Invalid date format: {scheduled_at_str}")

            # Create Post
            post = Post(
                id=str(uuid.uuid4()),
                workspace_id=workspace_id,
                author_id=author_id,
                title=title,
                content=content,
                platform=target_platform,
                status="scheduled" if scheduled_at and auto_schedule else "draft",
                scheduled_at=scheduled_at,
                meta={"source": "csv_import", "tags": tags},
            )
            db.add(post)

            # Create PostPlatform entry
            pp = PostPlatform(
                id=str(uuid.uuid4()),
                post_id=post.id,
                workspace_id=workspace_id,
                platform=target_platform,
                status="scheduled" if scheduled_at and auto_schedule else "draft",
                scheduled_at=scheduled_at,
            )
            db.add(pp)

            created.append({
                "row": i + 1,
                "post_id": post.id,
                "platform": target_platform,
                "title": title[:50],
            })

        except Exception as e:
            errors.append(f"Row {i + 1}: {str(e)}")

    await db.flush()

    return {
        "total_rows": len(rows),
        "created": len(created),
        "errors": len(errors),
        "items": created,
        "error_details": errors[:20],
    }


async def export_to_csv(
    db: AsyncSession,
    workspace_id: str,
    status: str | None = None,
    platform: str | None = None,
) -> str:
    """Export posts to CSV format."""
    from app.models.content import Post
    from app.models.post_platform import PostPlatform
    from sqlalchemy import select

    query = select(PostPlatform, Post.title, Post.content).join(
        Post, PostPlatform.post_id == Post.id
    ).where(PostPlatform.workspace_id == workspace_id)

    if status:
        query = query.where(PostPlatform.status == status)
    if platform:
        query = query.where(PostPlatform.platform == platform)

    result = await db.execute(query)
    rows = result.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["title", "content", "platform", "status", "scheduled_at", "published_at"])

    for pp, title, content in rows:
        writer.writerow([
            title or "",
            content or "",
            pp.platform,
            pp.status,
            pp.scheduled_at.isoformat() if pp.scheduled_at else "",
            pp.published_at.isoformat() if pp.published_at else "",
        ])

    return output.getvalue()
