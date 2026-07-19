"""PostPlatform — per-platform scheduling and publishing state.

One Post can target multiple platforms. Each PostPlatform row tracks
the platform-specific caption, media, schedule, and publish state.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Integer, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class PostPlatform(Base):
    __tablename__ = "post_platforms"

    id = Column(String, primary_key=True)
    post_id = Column(String, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False, index=True)
    platform = Column(String(32), nullable=False, index=True)  # linkedin, x, instagram, facebook, youtube

    # Platform-specific content overrides (null = use parent Post content)
    caption = Column(Text, nullable=True)
    media_asset_ids = Column(JSON, default=list)  # list of asset IDs for this platform
    title = Column(String, nullable=True)          # e.g. YouTube video title

    # State machine: draft → scheduled → publishing → published | failed | cancelled
    status = Column(String(16), default="draft", nullable=False, index=True)
    scheduled_at = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)
    platform_post_id = Column(String, nullable=True)  # ID returned by platform API

    # Error tracking
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)

    # Token version at time of scheduling (detects stale tokens)
    token_version = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    post = relationship("Post", back_populates="platform_targets")
    workspace = relationship("Workspace")
