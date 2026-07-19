"""add post_platforms table

Revision ID: 003_add_post_platforms
Revises: 002_add_asset_platform
Create Date: 2026-07-17
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "003_add_post_platforms"
down_revision: Union[str, None] = "002_add_asset_platform"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "post_platforms",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column(
            "post_id",
            sa.String(),
            sa.ForeignKey("posts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "workspace_id",
            sa.String(),
            sa.ForeignKey("workspaces.id"),
            nullable=False,
        ),
        sa.Column("platform", sa.String(32), nullable=False),
        sa.Column("caption", sa.Text(), nullable=True),
        sa.Column("media_asset_ids", sa.JSON(), server_default="[]"),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("status", sa.String(16), nullable=False, server_default="draft"),
        sa.Column("scheduled_at", sa.DateTime(), nullable=True),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("platform_post_id", sa.String(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("retry_count", sa.Integer(), server_default="0"),
        sa.Column("max_retries", sa.Integer(), server_default="3"),
        sa.Column("token_version", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_index("ix_post_platforms_post_id", "post_platforms", ["post_id"])
    op.create_index("ix_post_platforms_workspace_id", "post_platforms", ["workspace_id"])
    op.create_index("ix_post_platforms_platform", "post_platforms", ["platform"])
    op.create_index("ix_post_platforms_status", "post_platforms", ["status"])

    # Unique constraint: one entry per post+platform combination
    op.create_index(
        "uq_post_platform",
        "post_platforms",
        ["post_id", "platform"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_post_platform", table_name="post_platforms")
    op.drop_index("ix_post_platforms_status", table_name="post_platforms")
    op.drop_index("ix_post_platforms_platform", table_name="post_platforms")
    op.drop_index("ix_post_platforms_workspace_id", table_name="post_platforms")
    op.drop_index("ix_post_platforms_post_id", table_name="post_platforms")
    op.drop_table("post_platforms")
