"""SQLAlchemy models for the autonomous AI workflow pipeline.

Tables:
    content_items            — tracks a piece of content through the generation pipeline
    platform_posts           — platform-specific post records linked to content_items
    platform_analytics       — daily raw stats ingested per post, with performance scores
    platform_provider_configs — per-workspace, per-platform AI provider selection (set via UI)
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON, ARRAY
from sqlalchemy.orm import relationship

from app.core.database import Base


class ContentItem(Base):
    """A content idea flowing through the Research → Draft → HITL pipeline."""

    __tablename__ = "content_items"

    id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False, index=True)
    topic = Column(String(500), nullable=False)
    platform = Column(String(32), nullable=False, index=True)
    status = Column(String(32), nullable=False, default="ideation", index=True)
    target_audience = Column(String(300))
    additional_context = Column(Text)
    brand_voice_id = Column(String, ForeignKey("brand_voices.id"))

    # AI-generated artefacts
    generated_texts = Column(JSON, default=list)     # list of {provider, model, content, tokens_used}
    visual_prompts = Column(JSON, default=list)      # list of {prompt_text, style, aspect_ratio}
    final_text = Column(Text)
    research_notes = Column(Text)

    # HITL fields
    approved_by = Column(String, ForeignKey("users.id"))
    approved_at = Column(DateTime)
    scheduled_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    platform_posts = relationship("PlatformPost", back_populates="content_item", cascade="all, delete-orphan")


class PlatformPost(Base):
    """A post that has been submitted to (or scheduled on) a social platform."""

    __tablename__ = "platform_posts"

    id = Column(String, primary_key=True)
    content_item_id = Column(String, ForeignKey("content_items.id"), nullable=False, index=True)
    platform = Column(String(32), nullable=False, index=True)
    platform_post_id = Column(String, index=True)          # native ID once published
    post_text = Column(Text, nullable=False)
    media_urls = Column(ARRAY(String), default=list)
    status = Column(String(32), nullable=False, default="pending_approval")
    published_at = Column(DateTime)
    meta = Column("metadata", JSON, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    content_item = relationship("ContentItem", back_populates="platform_posts")
    analytics_records = relationship("PlatformAnalytics", back_populates="platform_post", cascade="all, delete-orphan")


class PlatformAnalytics(Base):
    """Daily raw engagement stats ingested from platform APIs."""

    __tablename__ = "platform_analytics"

    id = Column(String, primary_key=True)
    platform_post_id = Column(String, ForeignKey("platform_posts.id"), nullable=False, index=True)
    platform = Column(String(32), nullable=False)
    impressions = Column(Integer, default=0)
    engagements = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    reach = Column(Integer, default=0)

    # Feedback loop outputs
    performance_score = Column(Float)
    stored_as_embedding = Column(Integer, default=0)  # boolean as int for PG compat

    recorded_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    platform_post = relationship("PlatformPost", back_populates="analytics_records")


class PlatformProviderConfig(Base):
    """Per-workspace, per-platform AI provider selection.

    Users configure this via the UI settings page. The factory reads it
    at runtime instead of using a hardcoded default mapping.

    One row per (workspace_id, platform) pair.  ``provider`` stores the
    chosen AI backend (``claude`` / ``openai`` / ``gemini``), and
    ``model`` optionally overrides the default model for that provider.
    """

    __tablename__ = "platform_provider_configs"
    __table_args__ = (
        UniqueConstraint("workspace_id", "platform", name="uq_workspace_platform"),
    )

    id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False, index=True)
    platform = Column(String(32), nullable=False)      # linkedin / twitter / instagram / ...
    provider = Column(String(32), nullable=False)       # claude / openai / gemini
    model = Column(String(64))                          # optional model override
    is_active = Column(Integer, default=1)              # soft-disable without deleting
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
