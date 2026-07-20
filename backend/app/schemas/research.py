"""Pydantic schemas for ResearchItem — request/response models."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class ResearchItemCreate(BaseModel):
    """Request to create a new research item."""
    workspace_id: UUID
    category: str  # 'keyword', 'competitor', 'trend', 'thumbnail', 'audience'
    subcategory: Optional[str] = None
    topic: Optional[str] = None
    platform: Optional[str] = None  # 'youtube', 'tiktok', 'instagram', 'all'
    data: dict = {}
    keyword_difficulty: Optional[int] = Field(None, ge=1, le=100)
    search_volume: Optional[str] = None
    competition_level: Optional[str] = None
    video_seo_score: Optional[int] = Field(None, ge=0, le=100)
    trend_direction: Optional[str] = None
    trend_velocity: Optional[float] = None
    content_pillar: Optional[str] = None
    pillar_id: Optional[UUID] = None
    priority: int = 0
    engagement_rate: Optional[float] = None
    estimated_reach: Optional[int] = None
    estimated_impressions: Optional[int] = None
    source: Optional[str] = None  # 'llm', 'api', 'manual'
    confidence: Optional[float] = Field(None, ge=0, le=1)
    expires_at: Optional[datetime] = None


class ResearchItemUpdate(BaseModel):
    """Request to update an existing research item."""
    category: Optional[str] = None
    subcategory: Optional[str] = None
    topic: Optional[str] = None
    platform: Optional[str] = None
    data: Optional[dict] = None
    keyword_difficulty: Optional[int] = Field(None, ge=1, le=100)
    search_volume: Optional[str] = None
    competition_level: Optional[str] = None
    video_seo_score: Optional[int] = Field(None, ge=0, le=100)
    trend_direction: Optional[str] = None
    trend_velocity: Optional[float] = None
    content_pillar: Optional[str] = None
    pillar_id: Optional[UUID] = None
    priority: Optional[int] = None
    engagement_rate: Optional[float] = None
    estimated_reach: Optional[int] = None
    estimated_impressions: Optional[int] = None
    source: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0, le=1)
    expires_at: Optional[datetime] = None


class ResearchItemResponse(BaseModel):
    """Response for a single research item."""
    id: UUID
    workspace_id: UUID
    category: str
    subcategory: Optional[str]
    topic: Optional[str]
    platform: Optional[str]
    data: dict
    keyword_difficulty: Optional[int]
    search_volume: Optional[str]
    competition_level: Optional[str]
    video_seo_score: Optional[int]
    trend_direction: Optional[str]
    trend_velocity: Optional[float]
    content_pillar: Optional[str]
    pillar_id: Optional[UUID]
    priority: int
    engagement_rate: Optional[float]
    estimated_reach: Optional[int]
    estimated_impressions: Optional[int]
    source: Optional[str]
    confidence: Optional[float]
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True


class ResearchItemList(BaseModel):
    """Paginated list of research items."""
    items: list[ResearchItemResponse]
    total: int
    offset: int
    limit: int
