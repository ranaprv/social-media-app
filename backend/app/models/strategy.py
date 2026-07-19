"""Strategy-Driven Content Scheduling Engine models."""
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Integer, Float, Boolean, Text, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class ContentStrategy(Base):
    __tablename__ = "content_strategies"

    id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    goals = Column(JSON, nullable=False, default=[])
    content_pillars = Column(JSON, nullable=False, default=[])
    audience_personas = Column(JSON, nullable=False, default=[])
    posting_frequency = Column(JSON, nullable=False, default={})
    brand_voice_overrides = Column(JSON, default={})
    status = Column(String(16), nullable=False, default="draft", index=True)
    auto_generate = Column(Boolean, nullable=False, default=True)
    generate_ahead_days = Column(Integer, nullable=False, default=7)
    approval_required = Column(Boolean, nullable=False, default=True)
    auto_approve_threshold = Column(Float, default=0.85)
    last_generated_at = Column(DateTime, nullable=True)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    workspace = relationship("Workspace", back_populates="strategies")
    creator = relationship("User")
    plans = relationship("ContentPlan", back_populates="strategy", cascade="all, delete-orphan")
    audit_logs = relationship("StrategyAuditLog", back_populates="strategy", cascade="all, delete-orphan")


class ContentPlan(Base):
    __tablename__ = "content_plans"

    id = Column(String, primary_key=True)
    strategy_id = Column(String, ForeignKey("content_strategies.id"), nullable=False, index=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False, index=True)
    week_start = Column(DateTime, nullable=False)
    status = Column(String(16), nullable=False, default="draft", index=True)
    generation_task_id = Column(String(64), nullable=True)
    generation_progress = Column(JSON, default={})
    generated_at = Column(DateTime, nullable=True)
    slot_count = Column(Integer, default=0)
    approved_count = Column(Integer, default=0)
    published_count = Column(Integer, default=0)
    rejected_count = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    strategy = relationship("ContentStrategy", back_populates="plans")
    slots = relationship("ContentSlot", back_populates="plan", cascade="all, delete-orphan")


class ContentSlot(Base):
    __tablename__ = "content_slots"

    id = Column(String, primary_key=True)
    plan_id = Column(String, ForeignKey("content_plans.id"), nullable=False, index=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False, index=True)
    strategy_id = Column(String, ForeignKey("content_strategies.id"), nullable=False)
    pillar_name = Column(String(100), nullable=False)
    platform = Column(String(32), nullable=False, index=True)
    scheduled_date = Column(Date, nullable=False)
    scheduled_time = Column(String(5), nullable=False)
    scheduled_datetime = Column(DateTime, nullable=False, index=True)
    status = Column(String(16), nullable=False, default="empty", index=True)
    topic = Column(String(500), nullable=True)
    topic_sources = Column(JSON, default=[])
    generated_content = Column(Text, nullable=True)
    generated_variants = Column(JSON, default=[])
    selected_variant_index = Column(Integer, default=0)
    media_requirements = Column(JSON, default={})
    platform_metadata = Column(JSON, default={})
    brand_voice_score = Column(Float, nullable=True)
    generation_prompt_used = Column(Text, nullable=True)
    generation_model = Column(String(64), nullable=True)
    generation_tokens = Column(Integer, nullable=True)
    post_id = Column(String, ForeignKey("posts.id"), nullable=True)
    post_platform_id = Column(String, ForeignKey("post_platforms.id"), nullable=True)
    approved_by = Column(String, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(String(200), nullable=True)
    rejection_category = Column(String(32), nullable=True)
    user_edit_history = Column(JSON, default=[])
    auto_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    plan = relationship("ContentPlan", back_populates="slots")
    strategy = relationship("ContentStrategy")
    approver = relationship("User", foreign_keys=[approved_by])


class StrategyAuditLog(Base):
    __tablename__ = "strategy_audit_log"

    id = Column(String, primary_key=True)
    strategy_id = Column(String, ForeignKey("content_strategies.id"), nullable=False, index=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    action = Column(String(32), nullable=False)
    changes = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    strategy = relationship("ContentStrategy", back_populates="audit_logs")
    user = relationship("User")
