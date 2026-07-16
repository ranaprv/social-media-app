from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, ARRAY, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Post(Base):
    __tablename__ = "posts"
    
    id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)
    author_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String)
    content = Column(String, nullable=False)
    media_urls = Column(ARRAY(String), default=[])
    platform = Column(String, nullable=False)
    status = Column(String, default="draft")
    scheduled_at = Column(DateTime)
    published_at = Column(DateTime)
    platform_post_id = Column(String)
    meta = Column("metadata", JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    workspace = relationship("Workspace", back_populates="posts")
    author = relationship("User", back_populates="posts")
    calendar = relationship("ContentCalendar", back_populates="post", uselist=False)
    analytics = relationship("AnalyticsMetric", back_populates="post", cascade="all, delete-orphan")
    versions = relationship("PostVersion", back_populates="post", cascade="all, delete-orphan")


class PostVersion(Base):
    __tablename__ = "post_versions"
    
    id = Column(String, primary_key=True)
    post_id = Column(String, ForeignKey("posts.id"), nullable=False)
    content = Column(String, nullable=False)
    version = Column(Integer, nullable=False)
    author_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    post = relationship("Post", back_populates="versions")
    author = relationship("User")


class PlatformConnection(Base):
    __tablename__ = "platform_connections"
    
    id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)
    platform = Column(String, nullable=False)
    platform_user_id = Column(String, nullable=False)
    platform_username = Column(String, nullable=False)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String)
    expires_at = Column(DateTime)
    meta = Column("metadata", JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    workspace = relationship("Workspace", back_populates="connections")


class ContentCalendar(Base):
    __tablename__ = "content_calendars"
    
    id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)
    post_id = Column(String, ForeignKey("posts.id"), unique=True, nullable=False)
    date = Column(DateTime, nullable=False)
    time_slot = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    workspace = relationship("Workspace", back_populates="calendar_entries")
    post = relationship("Post", back_populates="calendar")


class AnalyticsMetric(Base):
    __tablename__ = "analytics_metrics"
    
    id = Column(String, primary_key=True)
    post_id = Column(String, ForeignKey("posts.id"), nullable=False)
    platform = Column(String, nullable=False)
    impressions = Column(Integer, default=0)
    reach = Column(Integer, default=0)
    engagement = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    watch_time = Column(Integer)
    subscribers = Column(Integer)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    post = relationship("Post", back_populates="analytics")


class BrandVoice(Base):
    __tablename__ = "brand_voices"
    
    id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"), unique=True, nullable=False)
    tone = Column(String)
    writing_style = Column(String)
    cta_style = Column(String)
    emoji_usage = Column(String)
    formatting = Column(String)
    vocabulary = Column(String)
    technical_depth = Column(String)
    sample_posts = Column(ARRAY(String), default=[])
    training_sources = Column(JSON, default=[])
    approval_history = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    workspace = relationship("Workspace", back_populates="brand_voice")


class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    url = Column(String, nullable=False)
    platform = Column(String(32), index=True)           # youtube / instagram / linkedin / facebook / general
    content_type = Column(String(64), index=True)        # image / video / reel / carousel / vertical_video / post / document
    meta = Column("metadata", JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    workspace = relationship("Workspace", back_populates="assets")


class Activity(Base):
    __tablename__ = "activities"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)
    description = Column(String, nullable=False)
    meta = Column("metadata", JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="activities")
