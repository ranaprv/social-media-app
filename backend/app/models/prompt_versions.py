"""Prompt versioning models — track prompt templates and their performance.

Tables:
    prompt_versions    — versioned prompt templates per content_type + platform
    prompt_usage_logs  — tracks each prompt usage and its engagement outcome
"""
from sqlalchemy import Column, String, DateTime, Float, Integer, Boolean, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class PromptVersion(Base):
    """A versioned prompt template for content generation.

    Each row is a specific prompt + system_prompt pair for a content_type + platform.
    The ``is_active`` flag marks the current best-performing version.
    ``performance_score`` is a rolling average updated from analytics feedback.
    """
    __tablename__ = "prompt_versions"

    id = Column(String, primary_key=True)
    content_type = Column(String(64), nullable=False, index=True)   # linkedin_post, reel, image, etc.
    platform = Column(String(32), nullable=False, index=True)       # linkedin, x, instagram, etc.
    version = Column(Integer, nullable=False, default=1)
    system_prompt = Column(Text, nullable=False)
    user_prompt_template = Column(Text, nullable=False)            # template with {placeholders}
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=3000)

    # Performance tracking
    is_active = Column(Boolean, default=True, index=True)
    performance_score = Column(Float, default=0.0)                 # rolling avg 0-100
    usage_count = Column(Integer, default=0)
    avg_engagement_rate = Column(Float, default=0.0)

    # Metadata
    created_by = Column(String, nullable=True)                     # "system" or user_id
    notes = Column(Text, nullable=True)                             # why this version was created
    meta = Column("metadata", JSON, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    usage_logs = relationship("PromptUsageLog", back_populates="prompt_version", cascade="all, delete-orphan")


class PromptUsageLog(Base):
    """Logs each time a prompt version is used for content generation.

    Linked to a post (if created) so analytics can update the prompt's score.
    """
    __tablename__ = "prompt_usage_logs"

    id = Column(String, primary_key=True)
    prompt_version_id = Column(String, ForeignKey("prompt_versions.id"), nullable=False, index=True)
    workspace_id = Column(String, nullable=False, index=True)
    post_id = Column(String, nullable=True)                        # FK to posts if created
    content_item_id = Column(String, nullable=True)                # FK to content_items if from workflow

    # Generation context
    topic = Column(String(500), nullable=True)
    provider = Column(String(32), nullable=True)
    model = Column(String(64), nullable=True)
    tokens_used = Column(Integer, default=0)

    # Outcome (filled in later by analytics feedback)
    engagement_score = Column(Float, nullable=True)                # 0-100 predicted
    actual_engagement_rate = Column(Float, nullable=True)          # real engagement %
    scored_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    prompt_version = relationship("PromptVersion", back_populates="usage_logs")
