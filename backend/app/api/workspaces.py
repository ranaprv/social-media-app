from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import uuid
import re

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember
from app.models.content import BrandVoice, Asset
from app.schemas import (
    WorkspaceCreate,
    WorkspaceResponse,
    WorkspaceMemberResponse,
    WorkspaceMemberUpdate,
    BrandVoiceUpdate,
    BrandVoiceResponse,
    AssetCreate,
    AssetResponse,
)

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text


@router.post("/", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    workspace_data: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Check if slug is unique
    result = await db.execute(select(Workspace).where(Workspace.slug == workspace_data.slug))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workspace slug already exists",
        )
    
    # Create workspace
    workspace = Workspace(
        id=str(uuid.uuid4()),
        name=workspace_data.name,
        slug=workspace_data.slug or slugify(workspace_data.name),
        owner_id=current_user.id,
    )
    db.add(workspace)
    
    # Add owner as member
    member = WorkspaceMember(
        id=str(uuid.uuid4()),
        workspace_id=workspace.id,
        user_id=current_user.id,
        role="owner",
    )
    db.add(member)
    await db.flush()
    
    return WorkspaceResponse(
        id=workspace.id,
        name=workspace.name,
        slug=workspace.slug,
        owner_id=workspace.owner_id,
        created_at=workspace.created_at,
    )


@router.get("/", response_model=list[WorkspaceResponse])
async def list_workspaces(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Workspace)
        .join(WorkspaceMember)
        .where(WorkspaceMember.user_id == current_user.id)
    )
    workspaces = result.scalars().all()
    
    return [
        WorkspaceResponse(
            id=w.id,
            name=w.name,
            slug=w.slug,
            owner_id=w.owner_id,
            created_at=w.created_at,
        )
        for w in workspaces
    ]


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Check membership
    result = await db.execute(
        select(WorkspaceMember)
        .where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )
    
    result = await db.execute(select(Workspace).where(Workspace.id == workspace_id))
    workspace = result.scalar_one_or_none()
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )
    
    return WorkspaceResponse(
        id=workspace.id,
        name=workspace.name,
        slug=workspace.slug,
        owner_id=workspace.owner_id,
        created_at=workspace.created_at,
    )


# ─── Team Members ────────────────────────────────────────────────────────────

@router.get("/{workspace_id}/members", response_model=list[WorkspaceMemberResponse])
async def list_workspace_members(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Check membership first
    check = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id
        )
    )
    if not check.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not authorized to view members")

    result = await db.execute(
        select(WorkspaceMember, User)
        .join(User, WorkspaceMember.user_id == User.id)
        .where(WorkspaceMember.workspace_id == workspace_id)
    )
    
    response = []
    for row in result.all():
        member, user = row
        response.append(WorkspaceMemberResponse(
            id=member.id,
            workspace_id=member.workspace_id,
            user_id=member.user_id,
            role=member.role,
            name=user.name,
            email=user.email,
            created_at=member.created_at,
        ))
    return response


@router.post("/{workspace_id}/members", response_model=WorkspaceMemberResponse)
async def add_workspace_member(
    workspace_id: str,
    invite_email: str,
    role: str = "editor",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Check if user has owner/admin permission in this workspace
    check = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id
        )
    )
    member_record = check.scalar_one_or_none()
    if not member_record or member_record.role not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Only owners and admins can invite members")

    # Check if user to invite exists
    user_result = await db.execute(select(User).where(User.email == invite_email))
    invited_user = user_result.scalar_one_or_none()
    if not invited_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if user is already a member
    exist_check = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == invited_user.id
        )
    )
    if exist_check.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User is already a member of this workspace")

    # Add member
    new_member = WorkspaceMember(
        id=str(uuid.uuid4()),
        workspace_id=workspace_id,
        user_id=invited_user.id,
        role=role,
    )
    db.add(new_member)
    await db.flush()

    return WorkspaceMemberResponse(
        id=new_member.id,
        workspace_id=new_member.workspace_id,
        user_id=new_member.user_id,
        role=new_member.role,
        name=invited_user.name,
        email=invited_user.email,
        created_at=new_member.created_at,
    )


@router.put("/{workspace_id}/members/{member_id}", response_model=WorkspaceMemberResponse)
async def update_member_role(
    workspace_id: str,
    member_id: str,
    update_data: WorkspaceMemberUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Check if updater is admin or owner
    check = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id
        )
    )
    updater = check.scalar_one_or_none()
    if not updater or updater.role not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Only owners and admins can edit member roles")

    # Get target member record
    member_result = await db.execute(
        select(WorkspaceMember, User)
        .join(User, WorkspaceMember.user_id == User.id)
        .where(WorkspaceMember.id == member_id, WorkspaceMember.workspace_id == workspace_id)
    )
    row = member_result.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Workspace member not found")

    target_member, target_user = row
    
    # Restrict modifying owners
    if target_member.role == "owner" and updater.role != "owner":
        raise HTTPException(status_code=403, detail="Cannot demote or update workspace owner")

    target_member.role = update_data.role
    await db.flush()

    return WorkspaceMemberResponse(
        id=target_member.id,
        workspace_id=target_member.workspace_id,
        user_id=target_member.user_id,
        role=target_member.role,
        name=target_user.name,
        email=target_user.email,
        created_at=target_member.created_at,
    )


@router.delete("/{workspace_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    workspace_id: str,
    member_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    check = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id
        )
    )
    updater = check.scalar_one_or_none()
    if not updater or updater.role not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Only owners and admins can remove members")

    result = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.id == member_id, WorkspaceMember.workspace_id == workspace_id
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    if member.role == "owner":
        raise HTTPException(status_code=400, detail="Cannot delete the workspace owner")

    await db.delete(member)
    await db.flush()


# ─── Brand Voice ────────────────────────────────────────────────────────────

@router.get("/{workspace_id}/brand-voice", response_model=BrandVoiceResponse)
async def get_workspace_brand_voice(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify access
    check = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id
        )
    )
    if not check.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")

    result = await db.execute(select(BrandVoice).where(BrandVoice.workspace_id == workspace_id))
    voice = result.scalar_one_or_none()
    
    if not voice:
        # Return empty default voice
        return BrandVoiceResponse(
            tone="",
            writing_style="",
            cta_style="",
            emoji_usage="",
            formatting="",
            vocabulary="",
            sample_posts=[]
        )
    return voice


@router.post("/{workspace_id}/brand-voice", response_model=BrandVoiceResponse)
async def update_workspace_brand_voice(
    workspace_id: str,
    voice_data: BrandVoiceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify access
    check = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id
        )
    )
    member = check.scalar_one_or_none()
    if not member or member.role in ["viewer", "writer"]:
         raise HTTPException(status_code=403, detail="Permission denied to edit brand voice")

    result = await db.execute(select(BrandVoice).where(BrandVoice.workspace_id == workspace_id))
    voice = result.scalar_one_or_none()

    if not voice:
        voice = BrandVoice(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
        )
        db.add(voice)

    update_dict = voice_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(voice, field, value)

    await db.flush()
    return voice


# ─── Assets ─────────────────────────────────────────────────────────────────

@router.get("/{workspace_id}/assets", response_model=list[AssetResponse])
async def list_workspace_assets(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify access
    check = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id
        )
    )
    if not check.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")

    result = await db.execute(select(Asset).where(Asset.workspace_id == workspace_id))
    return result.scalars().all()


@router.post("/{workspace_id}/assets", response_model=AssetResponse)
async def create_workspace_asset(
    workspace_id: str,
    asset_data: AssetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify access
    check = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id
        )
    )
    member = check.scalar_one_or_none()
    if not member or member.role in ["viewer"]:
         raise HTTPException(status_code=403, detail="Permission denied to add assets")

    asset = Asset(
        id=str(uuid.uuid4()),
        workspace_id=workspace_id,
        name=asset_data.name,
        type=asset_data.type,
        url=asset_data.url,
        metadata=asset_data.metadata
    )
    db.add(asset)
    await db.flush()
    return asset
