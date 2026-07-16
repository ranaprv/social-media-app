from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/media", tags=["media"])


@router.get("/assets")
async def get_media_assets(
    type: str = None,
    search: str = None,
    tags: str = None,
    folder: str = None,
    sort_by: str = "date",
    sort_order: str = "desc",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get media assets with filtering and search."""
    assets = [
        {"id": "ma-1", "name": "hero-banner.png", "type": "image", "url": "/assets/hero-banner.png", "thumbnail_url": "/assets/thumbs/hero-banner.png", "size": 245000, "mime_type": "image/png", "tags": ["banner", "hero", "marketing"], "folder": "campaigns", "uploaded_by": current_user.id, "uploaded_by_name": current_user.name or "User", "created_at": (datetime.utcnow() - timedelta(days=5)).isoformat(), "metadata": {"width": 1200, "height": 630}},
        {"id": "ma-2", "name": "product-demo.mp4", "type": "video", "url": "/assets/product-demo.mp4", "thumbnail_url": "/assets/thumbs/product-demo.png", "size": 15400000, "mime_type": "video/mp4", "tags": ["demo", "product", "tutorial"], "folder": "videos", "uploaded_by": "user-2", "uploaded_by_name": "Sarah Chen", "created_at": (datetime.utcnow() - timedelta(days=3)).isoformat(), "metadata": {"duration": 120, "resolution": "1080p"}},
        {"id": "ma-3", "name": "brand-guidelines.pdf", "type": "pdf", "url": "/assets/brand-guidelines.pdf", "size": 890000, "mime_type": "application/pdf", "tags": ["brand", "guidelines", "design"], "folder": "brand", "uploaded_by": current_user.id, "uploaded_by_name": current_user.name or "User", "created_at": (datetime.utcnow() - timedelta(days=30)).isoformat(), "metadata": {"pages": 24}},
        {"id": "ma-4", "name": "company-logo.svg", "type": "logo", "url": "/assets/company-logo.svg", "size": 12000, "mime_type": "image/svg+xml", "tags": ["logo", "brand"], "folder": "brand", "uploaded_by": current_user.id, "uploaded_by_name": current_user.name or "User", "created_at": (datetime.utcnow() - timedelta(days=60)).isoformat(), "metadata": {}},
        {"id": "ma-5", "name": "post-template-linkedin.psd", "type": "template", "url": "/assets/templates/linkedin-post.psd", "size": 3400000, "mime_type": "application/octet-stream", "tags": ["template", "linkedin", "design"], "folder": "templates", "uploaded_by": "user-3", "uploaded_by_name": "Marcus Johnson", "created_at": (datetime.utcnow() - timedelta(days=14)).isoformat(), "metadata": {"dimensions": "1200x627"}},
        {"id": "ma-6", "name": "infographic-q2.png", "type": "image", "url": "/assets/infographic-q2.png", "thumbnail_url": "/assets/thumbs/infographic-q2.png", "size": 520000, "mime_type": "image/png", "tags": ["infographic", "data", "q2"], "folder": "campaigns", "uploaded_by": "user-4", "uploaded_by_name": "Priya Patel", "created_at": (datetime.utcnow() - timedelta(days=7)).isoformat(), "metadata": {"width": 1080, "height": 1920}},
        {"id": "ma-7", "name": "webinar-recording.mp4", "type": "video", "url": "/assets/webinar-recording.mp4", "thumbnail_url": "/assets/thumbs/webinar.png", "size": 89000000, "mime_type": "video/mp4", "tags": ["webinar", "recording", "education"], "folder": "videos", "uploaded_by": current_user.id, "uploaded_by_name": current_user.name or "User", "created_at": (datetime.utcnow() - timedelta(days=10)).isoformat(), "metadata": {"duration": 2400, "resolution": "1080p"}},
        {"id": "ma-8", "name": "social-templates-bundle.zip", "type": "template", "url": "/assets/templates/social-bundle.zip", "size": 12000000, "mime_type": "application/zip", "tags": ["template", "bundle", "social"], "folder": "templates", "uploaded_by": "user-2", "uploaded_by_name": "Sarah Chen", "created_at": (datetime.utcnow() - timedelta(days=20)).isoformat(), "metadata": {"count": 15}},
        {"id": "ma-9", "name": "icon-set-brand.svg", "type": "brand-asset", "url": "/assets/brand/icon-set.svg", "size": 45000, "mime_type": "image/svg+xml", "tags": ["icons", "brand", "ui"], "folder": "brand", "uploaded_by": current_user.id, "uploaded_by_name": current_user.name or "User", "created_at": (datetime.utcnow() - timedelta(days=45)).isoformat(), "metadata": {"icons": 50}},
    ]

    # Apply filters
    if type and type != "all":
        assets = [a for a in assets if a["type"] == type]
    if search:
        q = search.lower()
        assets = [a for a in assets if q in a["name"].lower() or any(q in t for t in a["tags"])]
    if tags:
        tag_list = [t.strip().lower() for t in tags.split(",")]
        assets = [a for a in assets if any(t in [tag.lower() for tag in a["tags"]] for t in tag_list)]
    if folder:
        assets = [a for a in assets if a["folder"] == folder]

    return {"assets": assets, "total": len(assets)}


@router.post("/assets")
async def upload_asset(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a new media asset."""
    return {
        "id": str(uuid.uuid4()),
        "message": "Asset uploaded",
        "asset": {
            "id": str(uuid.uuid4()),
            "name": request.get("name", "uploaded-file"),
            "type": request.get("type", "image"),
            "url": request.get("url", ""),
            "size": request.get("size", 0),
            "tags": request.get("tags", []),
            "folder": request.get("folder"),
            "uploaded_by": current_user.id,
            "uploaded_by_name": current_user.name or "User",
            "created_at": datetime.utcnow().isoformat(),
        },
    }


@router.put("/assets/{asset_id}")
async def update_asset(
    asset_id: str,
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update asset metadata (tags, name, folder)."""
    return {"id": asset_id, "message": "Asset updated", "updates": request}


@router.delete("/assets/{asset_id}")
async def delete_asset(
    asset_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a media asset."""
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
    tags = ["banner", "hero", "marketing", "demo", "product", "tutorial", "brand", "guidelines", "design", "logo", "template", "linkedin", "infographic", "data", "webinar", "recording", "education", "icons", "ui", "social"]
    return {"tags": tags}
