"""add research_items table

Revision ID: b1e2d3f4a5c6
Revises: a6f5d168726f
Create Date: 2026-07-19
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "b1e2d3f4a5c6"
down_revision: Union[str, None] = "a6f5d168726f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "research_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),

        # Classification
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("subcategory", sa.String(50), nullable=True),

        # Core data
        sa.Column("topic", sa.String(255), nullable=True),
        sa.Column("platform", sa.String(50), nullable=True),
        sa.Column("data", postgresql.JSONB(), nullable=False, server_default="{}"),

        # Video SEO metrics
        sa.Column("keyword_difficulty", sa.Integer(), nullable=True),
        sa.Column("search_volume", sa.String(50), nullable=True),
        sa.Column("competition_level", sa.String(20), nullable=True),
        sa.Column("video_seo_score", sa.Integer(), nullable=True),

        # Trend tracking
        sa.Column("trend_direction", sa.String(20), nullable=True),
        sa.Column("trend_velocity", sa.Float(), nullable=True),

        # Content integration
        sa.Column("content_pillar", sa.String(100), nullable=True),
        sa.Column("pillar_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),

        # Engagement metrics
        sa.Column("engagement_rate", sa.Float(), nullable=True),
        sa.Column("estimated_reach", sa.Integer(), nullable=True),
        sa.Column("estimated_impressions", sa.Integer(), nullable=True),

        # Metadata
        sa.Column("source", sa.String(50), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),

        # Timestamps
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
    )

    # Indexes
    op.create_index("idx_research_workspace", "research_items", ["workspace_id"])
    op.create_index("idx_research_category", "research_items", ["category"])
    op.create_index("idx_research_platform", "research_items", ["platform"])
    op.create_index("idx_research_pillar", "research_items", ["content_pillar"])
    op.create_index("idx_research_created", "research_items", ["created_at"])


def downgrade() -> None:
    op.drop_index("idx_research_created", table_name="research_items")
    op.drop_index("idx_research_pillar", table_name="research_items")
    op.drop_index("idx_research_platform", table_name="research_items")
    op.drop_index("idx_research_category", table_name="research_items")
    op.drop_index("idx_research_workspace", table_name="research_items")
    op.drop_table("research_items")
