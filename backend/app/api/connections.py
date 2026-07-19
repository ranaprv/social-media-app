"""Platform connections — connect social media accounts."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.workspace import ensure_system_workspace
from app.models.user import User
from app.models.content import PlatformConnection

router = APIRouter(prefix="/connections", tags=["connections"])


@router.get("/")
async def list_connections(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all connected accounts for the current user."""
    workspace_id = await ensure_system_workspace(db)
    result = await db.execute(
        select(PlatformConnection).where(
            PlatformConnection.workspace_id == workspace_id
        )
    )
    connections = result.scalars().all()
    return [
        {
            "id": c.id,
            "platform": c.platform,
            "username": c.platform_username,
            "has_client_id": bool((c.meta or {}).get("client_id")),
            "has_client_secret": bool((c.meta or {}).get("client_secret")),
            "connected_at": (
                c.created_at.isoformat()
                if c.created_at
                else datetime.utcnow().isoformat()
            ),
        }
        for c in connections
    ]


@router.post("/")
async def connect_platform(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Connect a social media account."""
    workspace_id = await ensure_system_workspace(db)
    platform = request.get("platform", "")
    client_id = request.get("client_id", "")
    client_secret = request.get("client_secret", "")
    username = request.get("username", "")

    if not platform:
        raise HTTPException(status_code=400, detail="Platform is required")

    # Check if already connected for this platform
    existing = await db.execute(
        select(PlatformConnection).where(
            PlatformConnection.workspace_id == workspace_id,
            PlatformConnection.platform == platform,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail=f"{platform} is already connected. Disconnect first.",
        )

    connection = PlatformConnection(
        id=str(uuid.uuid4()),
        workspace_id=workspace_id,
        platform=platform,
        platform_user_id=client_id or f"demo-{platform}",
        platform_username=username or f"user-{platform}",
        access_token=client_secret or "demo-token",
        meta={
            "client_id": client_id,
            "client_secret": client_secret,
            "username": username,
        },
        created_at=datetime.utcnow(),
    )
    db.add(connection)
    await db.flush()

    return {
        "id": connection.id,
        "platform": platform,
        "username": username or f"user-{platform}",
        "has_client_id": bool(client_id),
        "has_client_secret": bool(client_secret),
        "connected_at": connection.created_at.isoformat(),
    }


@router.delete("/{connection_id}")
async def disconnect_platform(
    connection_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Disconnect a social media account."""
    workspace_id = await ensure_system_workspace(db)
    result = await db.execute(
        select(PlatformConnection).where(
            PlatformConnection.id == connection_id,
            PlatformConnection.workspace_id == workspace_id,
        )
    )
    connection = result.scalar_one_or_none()
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    await db.delete(connection)
    await db.flush()
    return {"status": "disconnected", "id": connection_id}
