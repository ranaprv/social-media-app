from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember
from app.models.content import Post, Activity
from app.schemas import PostCreate, PostUpdate, PostResponse
from app.schemas.post_platform import PostPlatformCreate, PostPlatformResponse
from app.services.sanitizer import sanitize_html

router = APIRouter(prefix="/posts", tags=["posts"])


async def verify_workspace_access(
    workspace_id: str,
    current_user: User,
    db: AsyncSession,
) -> Workspace:
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
            detail="Workspace not found or access denied",
        )
    
    result = await db.execute(select(Workspace).where(Workspace.id == workspace_id))
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )
    
    return workspace


@router.post("/{workspace_id}", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    workspace_id: str,
    post_data: PostCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await verify_workspace_access(workspace_id, current_user, db)
    
    post = Post(
        id=str(uuid.uuid4()),
        workspace_id=workspace_id,
        author_id=current_user.id,
        title=post_data.title,
        content=sanitize_html(post_data.content),
        media_urls=post_data.media_urls,
        platform=post_data.platform,
        status=post_data.status,
        scheduled_at=post_data.scheduled_at,
        metadata=post_data.metadata,
    )
    db.add(post)
    
    # Log activity
    activity = Activity(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        type="post_created",
        description=f"Created post: {post_data.title or 'Untitled'}",
    )
    db.add(activity)
    await db.flush()
    
    return PostResponse(
        id=post.id,
        workspace_id=post.workspace_id,
        author_id=post.author_id,
        title=post.title,
        content=post.content,
        media_urls=post.media_urls,
        platform=post.platform,
        status=post.status,
        scheduled_at=post.scheduled_at,
        published_at=post.published_at,
        platform_post_id=post.platform_post_id,
        metadata=post.meta or {},
        created_at=post.created_at,
        updated_at=post.updated_at,
    )


@router.post("/{workspace_id}/schedule", status_code=status.HTTP_201_CREATED)
async def create_and_schedule_post(
    workspace_id: str,
    post_data: PostCreate,
    platforms: list[str] = Query(None, description="Target platforms"),
    scheduled_at: datetime = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a post and schedule it to multiple platforms at once.

    This is the convenience endpoint that creates both the Post
    and the PostPlatform rows in one call.
    """
    await verify_workspace_access(workspace_id, current_user, db)

    if not platforms:
        platforms = [post_data.platform] if post_data.platform else []

    # Create the parent Post
    post = Post(
        id=str(uuid.uuid4()),
        workspace_id=workspace_id,
        author_id=current_user.id,
        title=post_data.title,
        content=sanitize_html(post_data.content),
        media_urls=post_data.media_urls,
        platform=platforms[0] if platforms else post_data.platform,
        status="scheduled" if scheduled_at else "draft",
        scheduled_at=scheduled_at,
        metadata=post_data.metadata,
    )
    db.add(post)

    # Create PostPlatform rows
    from app.models.post_platform import PostPlatform
    platform_targets = []
    for platform in platforms:
        pp = PostPlatform(
            id=str(uuid.uuid4()),
            post_id=post.id,
            workspace_id=workspace_id,
            platform=platform,
            status="scheduled" if scheduled_at else "draft",
            scheduled_at=scheduled_at,
        )
        db.add(pp)
        platform_targets.append(pp)

    # Log activity
    activity = Activity(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        type="post_scheduled",
        description=f"Scheduled post for {', '.join(platforms)}",
    )
    db.add(activity)
    await db.flush()

    return {
        "post": PostResponse(
            id=post.id,
            workspace_id=post.workspace_id,
            author_id=post.author_id,
            title=post.title,
            content=post.content,
            media_urls=post.media_urls,
            platform=post.platform,
            status=post.status,
            scheduled_at=post.scheduled_at,
            published_at=post.published_at,
            platform_post_id=post.platform_post_id,
            metadata=post.meta or {},
            created_at=post.created_at,
            updated_at=post.updated_at,
        ),
        "platforms": [
            PostPlatformResponse.model_validate(pt).model_dump()
            for pt in platform_targets
        ],
    }


@router.get("/{workspace_id}")
async def list_posts(
    workspace_id: str,
    platform: str = None,
    status: str = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List posts with filtering and pagination."""
    await verify_workspace_access(workspace_id, current_user, db)
    
    query = select(Post).where(Post.workspace_id == workspace_id)
    count_query = select(func.count(Post.id)).where(Post.workspace_id == workspace_id)
    
    if platform:
        query = query.where(Post.platform == platform)
        count_query = count_query.where(Post.platform == platform)
    if status:
        query = query.where(Post.status == status)
        count_query = count_query.where(Post.status == status)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    query = query.order_by(Post.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    posts = result.scalars().all()
    
    return {
        "items": [
            PostResponse(
                id=p.id,
                workspace_id=p.workspace_id,
                author_id=p.author_id,
                title=p.title,
                content=p.content,
                media_urls=p.media_urls,
                platform=p.platform,
                status=p.status,
                scheduled_at=p.scheduled_at,
                published_at=p.published_at,
                platform_post_id=p.platform_post_id,
                metadata=p.meta or {},
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            for p in posts
        ],
        "total": total,
        "offset": offset,
        "limit": limit,
    }


@router.get("/{workspace_id}/{post_id}", response_model=PostResponse)
async def get_post(
    workspace_id: str,
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await verify_workspace_access(workspace_id, current_user, db)
    
    result = await db.execute(
        select(Post).where(Post.id == post_id, Post.workspace_id == workspace_id)
    )
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    
    return PostResponse(
        id=post.id,
        workspace_id=post.workspace_id,
        author_id=post.author_id,
        title=post.title,
        content=post.content,
        media_urls=post.media_urls,
        platform=post.platform,
        status=post.status,
        scheduled_at=post.scheduled_at,
        published_at=post.published_at,
        platform_post_id=post.platform_post_id,
        metadata=post.meta or {},
        created_at=post.created_at,
        updated_at=post.updated_at,
    )


@router.put("/{workspace_id}/{post_id}", response_model=PostResponse)
async def update_post(
    workspace_id: str,
    post_id: str,
    post_data: PostUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await verify_workspace_access(workspace_id, current_user, db)
    
    result = await db.execute(
        select(Post).where(Post.id == post_id, Post.workspace_id == workspace_id)
    )
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    
    update_data = post_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)
    
    await db.flush()
    
    return PostResponse(
        id=post.id,
        workspace_id=post.workspace_id,
        author_id=post.author_id,
        title=post.title,
        content=post.content,
        media_urls=post.media_urls,
        platform=post.platform,
        status=post.status,
        scheduled_at=post.scheduled_at,
        published_at=post.published_at,
        platform_post_id=post.platform_post_id,
        metadata=post.meta or {},
        created_at=post.created_at,
        updated_at=post.updated_at,
    )


@router.delete("/{workspace_id}/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    workspace_id: str,
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await verify_workspace_access(workspace_id, current_user, db)
    
    result = await db.execute(
        select(Post).where(Post.id == post_id, Post.workspace_id == workspace_id)
    )
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    
    await db.delete(post)
    await db.flush()
