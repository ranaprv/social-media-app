"""Bulk scheduling — CSV upload for up to 350 posts."""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import csv
import io
import uuid
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/scheduler", tags=["scheduler-bulk"])


@router.post("/bulk-upload")
async def bulk_upload(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload CSV to schedule up to 350 posts at once.

    CSV columns: title, content, platform, scheduled_at, media_url
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    content_bytes = await file.read()
    if len(content_bytes) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")

    try:
        text = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded")

    reader = csv.DictReader(io.StringIO(text))

    # Validate required columns
    required = {"title", "content", "platform", "scheduled_at"}
    if not required.issubset(set(reader.fieldnames or [])):
        missing = required - set(reader.fieldnames or [])
        raise HTTPException(status_code=400, detail=f"Missing CSV columns: {', '.join(missing)}")

    valid_platforms = ["linkedin", "x", "instagram", "facebook", "youtube"]
    total = 0
    valid = 0
    errors = []
    posts_created = []

    for i, row in enumerate(reader, start=2):  # row 1 is header
        total += 1
        if total > 350:
            errors.append({"row": i, "error": "Maximum 350 posts per upload"})
            break

        platform = row.get("platform", "").strip().lower()
        scheduled_at = row.get("scheduled_at", "").strip()
        title = row.get("title", "").strip()
        content_text = row.get("content", "").strip()
        media_url = row.get("media_url", "").strip()

        # Validate
        if platform not in valid_platforms:
            errors.append({"row": i, "error": f"Invalid platform: {platform}. Use: {', '.join(valid_platforms)}"})
            continue
        if not content_text:
            errors.append({"row": i, "error": "Content is required"})
            continue
        try:
            scheduled_dt = datetime.fromisoformat(scheduled_at.replace("Z", "+00:00")) if scheduled_at else None
        except ValueError:
            errors.append({"row": i, "error": f"Invalid date format: {scheduled_at}. Use ISO format (2026-07-16T09:00:00)"})
            continue

        post_id = str(uuid.uuid4())
        posts_created.append({
            "id": post_id,
            "title": title or f"Post {i}",
            "content": content_text[:500],
            "platform": platform,
            "scheduled_at": scheduled_dt.isoformat() if scheduled_dt else None,
            "media_url": media_url,
            "status": "scheduled" if scheduled_dt else "draft",
        })
        valid += 1

    return {
        "total_rows": total,
        "valid_rows": valid,
        "error_rows": len(errors),
        "errors": errors[:20],  # Show first 20 errors
        "posts": posts_created,
        "message": f"Processed {valid} posts from {total} rows. {len(errors)} errors.",
    }


@router.get("/bulk-template")
async def download_template():
    """Download a CSV template for bulk scheduling."""
    template = "title,content,platform,scheduled_at,media_url\n"
    template += '"10 Tips for Growth","Here are 10 tips...","linkedin","2026-07-20T09:00:00",""\n'
    template += '"Weekly Motivation","Stay inspired...","instagram","2026-07-21T12:00:00",""\n'
    template += '"Product Update","Exciting news...","x","2026-07-22T15:00:00",""\n'
    return {"template": template, "filename": "bulk-schedule-template.csv"}
