from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember
from app.models.content import PlatformConnection
from app.schemas import PlatformConnectionCreate, PlatformConnectionResponse

router = APIRouter(prefix="/connections", tags=["connections"])


@router.post("/{workspace_id}", response_model=PlatformConnectionResponse, status_code=201)
async def connect_platform(
    workspace_id: str,
    connection_data: PlatformConnectionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify workspace access
    result = await db.execute(
        select(WorkspaceMember)
        .where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # Check if already connected
    result = await db.execute(
        select(PlatformConnection)
        .where(
            PlatformConnection.workspace_id == workspace_id,
            PlatformConnection.platform == connection_data.platform,
            PlatformConnection.platform_user_id == connection_data.platform_user_id,
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Platform already connected")
    
    connection = PlatformConnection(
        id=str(uuid.uuid4()),
        workspace_id=workspace_id,
        platform=connection_data.platform,
        platform_user_id=connection_data.platform_user_id,
        platform_username=connection_data.platform_username,
        access_token=connection_data.access_token,
        refresh_token=connection_data.refresh_token,
    )
    db.add(connection)
    await db.flush()
    
    return PlatformConnectionResponse(
        id=connection.id,
        workspace_id=connection.workspace_id,
        platform=connection.platform,
        platform_user_id=connection.platform_user_id,
        platform_username=connection.platform_username,
        created_at=connection.created_at,
    )


@router.get("/{workspace_id}", response_model=list[PlatformConnectionResponse])
async def list_connections(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify workspace access
    result = await db.execute(
        select(WorkspaceMember)
        .where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    result = await db.execute(
        select(PlatformConnection)
        .where(PlatformConnection.workspace_id == workspace_id)
    )
    connections = result.scalars().all()
    
    return [
        PlatformConnectionResponse(
            id=c.id,
            workspace_id=c.workspace_id,
            platform=c.platform,
            platform_user_id=c.platform_user_id,
            platform_username=c.platform_username,
            created_at=c.created_at,
        )
        for c in connections
    ]


@router.delete("/{workspace_id}/{connection_id}", status_code=204)
async def disconnect_platform(
    workspace_id: str,
    connection_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify workspace access
    result = await db.execute(
        select(WorkspaceMember)
        .where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    result = await db.execute(
        select(PlatformConnection)
        .where(
            PlatformConnection.id == connection_id,
            PlatformConnection.workspace_id == workspace_id,
        )
    )
    connection = result.scalar_one_or_none()
    
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    await db.delete(connection)
    await db.flush()
