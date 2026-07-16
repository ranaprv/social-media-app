from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    image = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    workspaces = relationship("Workspace", back_populates="owner")
    posts = relationship("Post", back_populates="author")
    activities = relationship("Activity", back_populates="user")


class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    provider_account_id = Column(String, nullable=False)
    refresh_token = Column(String)
    access_token = Column(String)
    expires_at = Column(String)
    token_type = Column(String)
    scope = Column(String)
    id_token = Column(String)
    session_state = Column(String)
    
    user = relationship("User", back_populates="accounts")


class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True)
    session_token = Column(String, unique=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    expires = Column(DateTime, nullable=False)
    
    user = relationship("User", back_populates="sessions")
