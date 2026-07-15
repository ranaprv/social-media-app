from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# ─── Auth ────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: str
    password: str
    name: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]
    image: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


# ─── Workspace ───────────────────────────────────────────────────────────────

class WorkspaceCreate(BaseModel):
    name: str
    slug: str


class WorkspaceResponse(BaseModel):
    id: str
    name: str
    slug: str
    owner_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Post ────────────────────────────────────────────────────────────────────

class PostCreate(BaseModel):
    title: Optional[str] = None
    content: str
    media_urls: list[str] = []
    platform: str
    status: str = "draft"
    scheduled_at: Optional[datetime] = None
    metadata: dict = {}


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    media_urls: Optional[list[str]] = None
    platform: Optional[str] = None
    status: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    metadata: Optional[dict] = None


class PostResponse(BaseModel):
    id: str
    workspace_id: str
    author_id: str
    title: Optional[str]
    content: str
    media_urls: list[str]
    platform: str
    status: str
    scheduled_at: Optional[datetime]
    published_at: Optional[datetime]
    platform_post_id: Optional[str]
    metadata: dict
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── Platform Connection ─────────────────────────────────────────────────────

class PlatformConnectionCreate(BaseModel):
    platform: str
    access_token: str
    refresh_token: Optional[str] = None
    platform_user_id: str
    platform_username: str


class PlatformConnectionResponse(BaseModel):
    id: str
    workspace_id: str
    platform: str
    platform_user_id: str
    platform_username: str
    created_at: datetime

    class Config:
        from_attributes = True


# ─── AI Content ──────────────────────────────────────────────────────────────

class AIContentRequest(BaseModel):
    platform: str
    content_type: str
    topic: str
    brand_voice: Optional[str] = None
    keywords: list[str] = []
    tone: Optional[str] = None
    length: str = "medium"  # short, medium, long


class AIContentResponse(BaseModel):
    content: str
    hashtags: list[str]
    suggestions: list[str]
    engagement_score: float


# ─── Analytics ───────────────────────────────────────────────────────────────

class AnalyticsResponse(BaseModel):
    post_id: str
    platform: str
    impressions: int
    reach: int
    engagement: int
    likes: int
    comments: int
    shares: int
    clicks: int
    watch_time: Optional[int]
    subscribers: Optional[int]
    recorded_at: datetime

    class Config:
        from_attributes = True


# ─── Dashboard ───────────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_posts: int
    scheduled_posts: int
    published_posts: int
    total_impressions: int
    total_engagement: int
    followers_growth: int


# ─── Auth Extra ──────────────────────────────────────────────────────────────

class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    password: str


class MFASetupResponse(BaseModel):
    secret: str
    qr_code: str


class MFAVerifyRequest(BaseModel):
    code: str
    secret: str


class MFAToggleRequest(BaseModel):
    enabled: bool


# ─── Workspace Extra ─────────────────────────────────────────────────────────

class WorkspaceMemberResponse(BaseModel):
    id: str
    workspace_id: str
    user_id: str
    role: str
    name: Optional[str]
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class WorkspaceMemberUpdate(BaseModel):
    role: str


class BrandVoiceUpdate(BaseModel):
    tone: Optional[str] = None
    writing_style: Optional[str] = None
    cta_style: Optional[str] = None
    emoji_usage: Optional[str] = None
    formatting: Optional[str] = None
    vocabulary: Optional[str] = None
    sample_posts: list[str] = []


class BrandVoiceResponse(BaseModel):
    tone: Optional[str]
    writing_style: Optional[str]
    cta_style: Optional[str]
    emoji_usage: Optional[str]
    formatting: Optional[str]
    vocabulary: Optional[str]
    sample_posts: list[str]

    class Config:
        from_attributes = True


class AssetCreate(BaseModel):
    name: str
    type: str  # image, video, document, template
    url: str
    metadata: dict = {}


class AssetResponse(BaseModel):
    id: str
    workspace_id: str
    name: str
    type: str
    url: str
    metadata: dict
    created_at: datetime

    class Config:
        from_attributes = True


# ─── AI Research Engine ──────────────────────────────────────────────────────

class AIResearchRequest(BaseModel):
    topic: str
    platform: Optional[str] = "all"


class AIResearchTrendsResponse(BaseModel):
    trends: dict


class AIResearchCompetitorsResponse(BaseModel):
    competitors: list


class AIResearchKeywordsResponse(BaseModel):
    keywords: list


class AIResearchIdeasResponse(BaseModel):
    trending_topics: list[str]
    audience_pain_points: list[str]
    faqs: list[dict]
    content_opportunities: list[str]
    popular_keywords: list[str]

