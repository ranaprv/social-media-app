"""Research Engine models — Video SEO research data storage."""
from sqlalchemy import Column, String, DateTime, Float, Integer, Text, JSON, Uuid
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.core.database import Base


class ResearchItem(Base):
    __tablename__ = "research_items"

    id = Column(Uuid(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(Uuid(), nullable=False, index=True)

    # Classification
    category = Column(String(50), nullable=False, index=True)  # 'keyword', 'competitor', 'trend', 'thumbnail', 'audience'
    subcategory = Column(String(50), nullable=True)  # 'video_seo', 'title_test', 'demographics', etc.

    # Core data
    topic = Column(String(255), nullable=True)
    platform = Column(String(50), nullable=True, index=True)  # 'youtube', 'tiktok', 'instagram', 'all'
    data = Column(JSON, nullable=False, default=dict)

    # Video SEO metrics
    keyword_difficulty = Column(Integer, nullable=True)  # 1-100
    search_volume = Column(String(50), nullable=True)  # 'high', 'medium', 'low', or numeric string
    competition_level = Column(String(20), nullable=True)  # 'low', 'medium', 'high'
    video_seo_score = Column(Integer, nullable=True)  # 0-100 composite score

    # Trend tracking
    trend_direction = Column(String(20), nullable=True)  # 'rising', 'stable', 'declining'
    trend_velocity = Column(Float, nullable=True)  # rate of change

    # Content integration
    content_pillar = Column(String(100), nullable=True, index=True)
    pillar_id = Column(Uuid(), nullable=True)  # FK to strategy_content_pillars when it exists
    priority = Column(Integer, default=0, nullable=False)

    # Engagement metrics
    engagement_rate = Column(Float, nullable=True)
    estimated_reach = Column(Integer, nullable=True)
    estimated_impressions = Column(Integer, nullable=True)

    # Metadata
    source = Column(String(50), nullable=True)  # 'llm', 'api', 'manual'
    confidence = Column(Float, nullable=True)  # 0-1 reliability

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<ResearchItem {self.id} category={self.category} topic={self.topic}>"
