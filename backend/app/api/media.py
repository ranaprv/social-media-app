"""Media library API with platform-specific directories."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from datetime import datetime, timedelta
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.workspace import ensure_system_workspace
from app.models.user import User
from app.models.content import Asset

router = APIRouter(prefix="/media", tags=["media"])


def _seed_dummy_assets() -> list:
    """Create dummy media assets with real playable URLs for testing."""
    now = datetime.utcnow()
    system_ws = "system-workspace"
    SAMPLE_VIDEOS = "https://storage.googleapis.com/gtv-videos-bucket/sample"
    SAMPLE_IMAGES = "https://picsum.photos"
    dummies = [
        # YouTube
        Asset(id=str(uuid.uuid4()), workspace_id=system_ws, name="Product Demo Video.mp4", type="video", url=f"{SAMPLE_VIDEOS}/ForBiggerBlazes.mp4", platform="youtube", content_type="video", meta={"size": 15_000_000, "mime_type": "video/mp4", "tags": ["demo", "product"]}, created_at=now),
        Asset(id=str(uuid.uuid4()), workspace_id=system_ws, name="Tutorial - Getting Started.mp4", type="video", url=f"{SAMPLE_VIDEOS}/ForBiggerEscapes.mp4", platform="youtube", content_type="video", meta={"size": 25_000_000, "mime_type": "video/mp4", "tags": ["tutorial", "beginner"]}, created_at=now),
        Asset(id=str(uuid.uuid4()), workspace_id=system_ws, name="5 Tips in 60 Seconds.mp4", type="video", url=f"{SAMPLE_VIDEOS}/ForBiggerFun.mp4", platform="youtube", content_type="short", meta={"size": 8_000_000, "mime_type": "video/mp4", "tags": ["shorts", "tips"]}, created_at=now),
        Asset(id=str(uuid.uuid4()), workspace_id=system_ws, name="Behind the Scenes.mp4", type="video", url=f"{SAMPLE_VIDEOS}/ForBiggerJoyrides.mp4", platform="youtube", content_type="short", meta={"size": 5_000_000, "mime_type": "video/mp4", "tags": ["bts", "behind-the-scenes"]}, created_at=now),
        Asset(id=str(uuid.uuid4()), workspace_id=system_ws, name="Thumbnail - Summer Campaign.png", type="image", url=f"{SAMPLE_IMAGES}/seed/400/300", platform="youtube", content_type="image", meta={"size": 500_000, "mime_type": "image/png", "tags": ["thumbnail", "summer"]}, created_at=now),
        # Instagram
        Asset(id=str(uuid.uuid4()), workspace_id=system_ws, name="Trending Reel - Product Launch.mp4", type="video", url=f"{SAMPLE_VIDEOS}/ForBiggerMeltdowns.mp4", platform="instagram", content_type="reel", meta={"size": 12_000_000, "mime_type": "video/mp4", "tags": ["reel", "launch"]}, created_at=now),
        Asset(id=str(uuid.uuid4()), workspace_id=system_ws, name="Tips Carousel - 10 Slides.pdf", type="pdf", url="/carousels/tips-carousel.pdf", platform="instagram", content_type="carousel", meta={"size": 2_000_000, "mime_type": "application/pdf", "tags": ["carousel", "tips"]}, created_at=now),
        Asset(id=str(uuid.uuid4()), workspace_id=system_ws, name="Team Photo - Office Day.jpg", type="image", url=f"{SAMPLE_IMAGES}/seed/401/301", platform="instagram", content_type="image", meta={"size": 3_000_000, "mime_type": "image/jpeg", "tags": ["team", "office"]}, created_at=now),
        Asset(id=str(uuid.uuid4()), workspace_id=system_ws, name="Product Showcase Reel.mp4", type="video", url=f"{SAMPLE_VIDEOS}/BigBuckBunny.mp4", platform="instagram", content_type="reel", meta={"size": 10_000_000, "mime_type": "video/mp4", "tags": ["product", "showcase"]}, created_at=now),
        # LinkedIn
        Asset(id=str(uuid.uuid4()), workspace_id=system_ws, name="Thought Leadership Post.txt", type="document", url="/docs/thought-leadership.txt", platform="linkedin", content_type="post", meta={"size": 5_000, "mime_type": "text/plain", "tags": ["thought-leadership", "article"]}, created_at=now),
        Asset(id=str(uuid.uuid4()), workspace_id=system_ws, name="Industry Report Carousel.pdf", type="pdf", url="/carousels/industry-report.pdf", platform="linkedin", content_type="carousel", meta={"size": 4_000_000, "mime_type": "application/pdf", "tags": ["report", "industry"]}, created_at=now),
        Asset(id=str(uuid.uuid4()), workspace_id=system_ws, name="CEO Message Video.mp4", type="video", url=f"{SAMPLE_VIDEOS}/ForBiggerBlazes.mp4", platform="linkedin", content_type="video", meta={"size": 20_000_000, "mime_type": "video/mp4", "tags": ["ceo", "message"]}, created_at=now),
        # Facebook
        Asset(id=str(uuid.uuid4()), workspace_id=system_ws, name="Community Event Photo.jpg", type="image", url=f"{SAMPLE_IMAGES}/seed/402/302", platform="facebook", content_type="image", meta={"size": 4_000_000, "mime_type": "image/jpeg", "tags": ["community", "event"]}, created_at=now),
        Asset(id=str(uuid.uuid4()), workspace_id=system_ws, name="Product Walkthrough.mp4", type="video", url=f"{SAMPLE_VIDEOS}/ElephantsDream.mp4", platform="facebook", content_type="video", meta={"size": 18_000_000, "mime_type": "video/mp4", "tags": ["product", "walkthrough"]}, created_at=now),
    ]
    return dummies


# ── Platform directory structure ────────────────────────────────────────────

PLATFORM_DIRECTORIES: dict[str, dict[str, str]] = {
    "youtube": {
        "video": "YouTube Videos",
        "short": "YouTube Shorts",
        "image": "YouTube Thumbnails & Images",
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
    db: AsyncSession = Depends(get_db),
):
    """Get media assets with filtering. Supports platform and content_type filters."""
    # Seed dummy assets if table is empty (idempotent — only seeds once)
    count_result = await db.execute(select(Asset))
    existing = count_result.scalars().all()
    if not existing:
        workspace_id = await ensure_system_workspace(db)
        dummy_assets = _seed_dummy_assets()
        for a in dummy_assets:
            db.add(a)
        try:
            await db.flush()
        except Exception:
            # Race: another request seeded — re-query
            await db.rollback()
            count_result = await db.execute(select(Asset))
            existing = count_result.scalars().all()
        else:
            existing = dummy_assets

    # Build response
    assets_list = []
    for a in existing:
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
            "content": (a.meta or {}).get("content", ""),
            "uploaded_by": "system",
            "uploaded_by_name": "System",
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

    workspace_id = await ensure_system_workspace(db)

    asset_id = str(uuid.uuid4())
    now = datetime.utcnow()
    text_content = request.get("content", "")

    asset = Asset(
        id=asset_id,
        workspace_id="system-workspace",
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
            "content": text_content,
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
