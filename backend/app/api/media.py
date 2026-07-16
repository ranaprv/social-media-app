"""Media library API with platform-specific directories."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from datetime import datetime, timedelta
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.content import Asset

router = APIRouter(prefix="/media", tags=["media"])


# ── Platform directory structure ────────────────────────────────────────────

PLATFORM_DIRECTORIES: dict[str, dict[str, str]] = {
    "youtube": {
        "image": "YouTube Thumbnails & Images",
        "video": "YouTube Videos",
    },
    "instagram": {
        "reel": "Instagram Reels",
        "carousel": "Instagram Carousels",
        "vertical_video": "Instagram Vertical Videos",
        "image": "Instagram Images",
    },
    "linkedin": {
        "post": "LinkedIn Posts",
        "carousel": "LinkedIn Carousels",
        "video": "LinkedIn Videos",
        "document": "LinkedIn Documents",
    },
    "facebook": {
        "image": "Facebook Images",
        "video": "Facebook Videos",
    },
}


@router.get("/platforms")
async def get_platform_directories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all platform directories with asset counts.

    Returns the full directory tree: platform → content_type → {label, count}.
    The scheduler uses this to know where to pull content from for each platform.
    """
    result = {}
    for platform, content_types in PLATFORM_DIRECTORIES.items():
        result[platform] = {}
        for content_type, label in content_types.items():
            count_result = await db.execute(
                select(Asset).where(
                    Asset.workspace_id == current_user.id,
                    Asset.platform == platform,
                    Asset.content_type == content_type,
                )
            )
            count = len(count_result.scalars().all())
            result[platform][content_type] = {
                "label": label,
                "count": count,
            }
    return {"platforms": result}


@router.get("/assets")
async def get_media_assets(
    type: Optional[str] = Query(None, description="Filter by asset type: image, video, pdf, etc."),
    platform: Optional[str] = Query(None, description="Filter by platform: youtube, instagram, linkedin, facebook"),
    content_type: Optional[str] = Query(None, description="Filter by content type: reel, carousel, vertical_video, post, document"),
    search: Optional[str] = Query(None, description="Search by name or tags"),
    tags: Optional[str] = Query(None, description="Comma-separated tag filter"),
    folder: Optional[str] = Query(None, description="Filter by folder"),
    sort_by: str = "date",
    sort_order: str = "desc",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get media assets with filtering. Supports platform and content_type filters."""
    # Query real assets from database
    query = select(Asset).where(Asset.workspace_id == current_user.id)
    result = await db.execute(query)
    assets = result.scalars().all()

    # Build response
    assets_list = []
    for a in assets:
        assets_list.append({
            "id": a.id,
            "name": a.name,
            "type": a.type,
            "url": a.url,
            "platform": a.platform,
            "content_type": a.content_type,
            "size": (a.meta or {}).get("size", 0),
            "mime_type": (a.meta or {}).get("mime_type", ""),
            "tags": (a.meta or {}).get("tags", []),
            "folder": (a.meta or {}).get("folder", ""),
            "uploaded_by": current_user.id,
            "uploaded_by_name": current_user.name or "User",
            "created_at": a.created_at.isoformat() if a.created_at else datetime.utcnow().isoformat(),
            "metadata": a.meta or {},
        })

    # Apply filters
    if type and type != "all":
        assets_list = [a for a in assets_list if a["type"] == type]
    if platform:
        assets_list = [a for a in assets_list if a["platform"] == platform]
    if content_type:
        assets_list = [a for a in assets_list if a["content_type"] == content_type]
    if search:
        q = search.lower()
        assets_list = [a for a in assets_list if q in a["name"].lower() or any(q in t for t in a["tags"])]
    if tags:
        tag_list = [t.strip().lower() for t in tags.split(",")]
        assets_list = [a for a in assets_list if any(t in [tag.lower() for tag in a["tags"]] for t in tag_list)]
    if folder:
        assets_list = [a for a in assets_list if a["folder"] == folder]

    return {"assets": assets_list, "total": len(assets_list)}


@router.post("/assets")
async def upload_asset(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a new media asset. Optionally assign to a platform directory."""
    platform = request.get("platform")
    content_type = request.get("content_type")

    # Validate platform/content_type combination
    if platform and content_type:
        valid_types = PLATFORM_DIRECTORIES.get(platform, {})
        if content_type not in valid_types:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid content_type '{content_type}' for platform '{platform}'. "
                       f"Valid types: {list(valid_types.keys())}",
            )

    asset_id = str(uuid.uuid4())
    now = datetime.utcnow()

    asset = Asset(
        id=asset_id,
        workspace_id=current_user.id,
        name=request.get("name", "uploaded-file"),
        type=request.get("type", "image"),
        url=request.get("url", ""),
        platform=platform,
        content_type=content_type,
        meta={
            "size": request.get("size", 0),
            "mime_type": request.get("mime_type", ""),
            "tags": request.get("tags", []),
            "folder": request.get("folder"),
        },
        created_at=now,
    )
    db.add(asset)
    await db.flush()

    return {
        "id": asset_id,
        "message": "Asset uploaded",
        "platform": platform,
        "content_type": content_type,
    }


@router.put("/assets/{asset_id}")
async def update_asset(
    asset_id: str,
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update asset metadata (tags, name, folder, platform, content_type)."""
    result = await db.execute(
        select(Asset).where(Asset.id == asset_id, Asset.workspace_id == current_user.id)
    )
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    if "name" in request:
        asset.name = request["name"]
    if "platform" in request:
        asset.platform = request["platform"]
    if "content_type" in request:
        asset.content_type = request["content_type"]
    if "tags" in request or "folder" in request:
        meta = asset.meta or {}
        if "tags" in request:
            meta["tags"] = request["tags"]
        if "folder" in request:
            meta["folder"] = request["folder"]
        asset.meta = meta

    await db.flush()
    return {"id": asset_id, "message": "Asset updated"}


@router.delete("/assets/{asset_id}")
async def delete_asset(
    asset_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a media asset."""
    result = await db.execute(
        select(Asset).where(Asset.id == asset_id, Asset.workspace_id == current_user.id)
    )
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    await db.delete(asset)
    await db.flush()
    return {"id": asset_id, "message": "Asset deleted"}


@router.get("/folders")
async def get_folders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get media folders."""
    folders = [
        {"id": "f-1", "name": "campaigns", "parent_id": None, "asset_count": 4, "created_at": (datetime.utcnow() - timedelta(days=60)).isoformat()},
        {"id": "f-2", "name": "videos", "parent_id": None, "asset_count": 2, "created_at": (datetime.utcnow() - timedelta(days=60)).isoformat()},
        {"id": "f-3", "name": "brand", "parent_id": None, "asset_count": 3, "created_at": (datetime.utcnow() - timedelta(days=60)).isoformat()},
        {"id": "f-4", "name": "templates", "parent_id": None, "asset_count": 2, "created_at": (datetime.utcnow() - timedelta(days=60)).isoformat()},
    ]
    return {"folders": folders}


@router.post("/folders")
async def create_folder(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new media folder."""
    return {
        "id": str(uuid.uuid4()),
        "name": request.get("name", "New Folder"),
        "parent_id": request.get("parent_id"),
        "asset_count": 0,
        "created_at": datetime.utcnow().isoformat(),
    }


@router.get("/tags")
async def get_tags(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all unique tags across assets."""
    result = await db.execute(
        select(Asset).where(Asset.workspace_id == current_user.id)
    )
    assets = result.scalars().all()
    all_tags: set[str] = set()
    for a in assets:
        tags = (a.meta or {}).get("tags", [])
        all_tags.update(tags)
    return {"tags": sorted(all_tags)}
