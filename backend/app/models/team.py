from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Boolean, Integer, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class TeamMember(Base):
    __tablename__ = "team_members"
    
    id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    role = Column(String, default="editor")  # owner, admin, editor, viewer
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    workspace = relationship("Workspace", back_populates="team_members")
    user = relationship("User")


class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(String, primary_key=True)
    post_id = Column(String, ForeignKey("posts.id"), nullable=False)
    author_id = Column(String, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    parent_id = Column(String, ForeignKey("comments.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    post = relationship("Post", back_populates="comments")
    author = relationship("User")
    replies = relationship("Comment", backref="parent", remote_side=[id])


class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(String, primary_key=True)
    post_id = Column(String, ForeignKey("posts.id"), nullable=False)
    requested_by = Column(String, ForeignKey("users.id"), nullable=False)
    assigned_to = Column(String, ForeignKey("users.id"), nullable=False)
    status = Column(String, default="pending")  # pending, approved, changes-requested, rejected
    feedback = Column(Text)
    requested_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    post = relationship("Post")
    requester = relationship("User", foreign_keys=[requested_by])
    assignee = relationship("User", foreign_keys=[assigned_to])


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)  # comment, review-request, review-complete, approval, mention, assignment
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    read = Column(Boolean, default=False)
    post_id = Column(String, ForeignKey("posts.id"))
    actor_id = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", foreign_keys=[user_id])
    actor = relationship("User", foreign_keys=[actor_id])


class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    color = Column(String, default="#3b82f6")
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    workspace = relationship("Workspace", back_populates="campaigns")


class MediaAsset(Base):
    __tablename__ = "media_assets"
    
    id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # image, video, pdf, brand-asset, logo, template
    url = Column(String, nullable=False)
    thumbnail_url = Column(String)
    size = Column(Integer, default=0)
    mime_type = Column(String, default="")
    tags = Column(JSON, default=[])
    folder = Column(String)
    uploaded_by = Column(String, ForeignKey("users.id"), nullable=False)
    meta = Column("metadata", JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    workspace = relationship("Workspace", back_populates="media_assets")
    uploader = relationship("User")


class SchedulerConfig(Base):
    __tablename__ = "scheduler_configs"
    
    id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"), unique=True, nullable=False)
    timezone = Column(String, default="UTC")
    auto_publish = Column(Boolean, default=False)
    queue_enabled = Column(Boolean, default=True)
    max_daily_posts = Column(Integer, default=10)
    preferred_times = Column(JSON, default=[])
    platform_settings = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    workspace = relationship("Workspace", back_populates="scheduler_config")
