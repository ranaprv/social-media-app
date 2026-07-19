"""Pydantic schemas for PostPlatform — request/response models."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PostPlatformCreate(BaseModel):
    """Request to create a PostPlatform entry."""
    post_id: str
    platform: str  # linkedin, x, instagram, facebook, youtube
    caption: Optional[str] = None  # null = use parent Post content
    media_asset_ids: list[str] = []
    title: Optional[str] = None
    scheduled_at: Optional[datetime] = None


class PostPlatformUpdate(BaseModel):
    """Request to update a PostPlatform entry."""
    caption: Optional[str] = None
    media_asset_ids: Optional[list[str]] = None
    title: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    status: Optional[str] = None  # allow manual status override (cancel, etc.)


class PostPlatformResponse(BaseModel):
    """Response for a PostPlatform entry."""
    id: str
    post_id: str
    workspace_id: str
    platform: str
    caption: Optional[str]
    media_asset_ids: list[str]
    title: Optional[str]
    status: str
    scheduled_at: Optional[datetime]
    published_at: Optional[datetime]
    platform_post_id: Optional[str]
    error_message: Optional[str]
    retry_count: int
    max_retries: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SchedulePostRequest(BaseModel):
    """Request to schedule a post to one or more platforms."""
    post_id: str
    platforms: list[dict]  # [{platform, caption?, scheduled_at?, media_asset_ids?}]
    default_scheduled_at: Optional[datetime] = None  # fallback if platform entry has no time


class BulkScheduleRequest(BaseModel):
    """Request to schedule multiple posts at once."""
    items: list[SchedulePostRequest]
