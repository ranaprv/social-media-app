"""add prompt_versions and prompt_usage_logs tables

Revision ID: c4d5e6f7a8b9
Revises: b1e2d3f4a5c6
Create Date: 2026-07-20
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "c4d5e6f7a8b9"
down_revision: Union[str, None] = "b1e2d3f4a5c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # prompt_versions table
    op.create_table(
        "prompt_versions",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("content_type", sa.String(64), nullable=False),
        sa.Column("platform", sa.String(32), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("system_prompt", sa.Text(), nullable=False),
        sa.Column("user_prompt_template", sa.Text(), nullable=False),
        sa.Column("temperature", sa.Float(), server_default="0.7"),
        sa.Column("max_tokens", sa.Integer(), server_default="3000"),
        sa.Column("is_active", sa.Boolean(), server_default="1"),
        sa.Column("performance_score", sa.Float(), server_default="0.0"),
        sa.Column("usage_count", sa.Integer(), server_default="0"),
        sa.Column("avg_engagement_rate", sa.Float(), server_default="0.0"),
        sa.Column("created_by", sa.String(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), server_default="{}"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_index("ix_prompt_versions_content_type", "prompt_versions", ["content_type"])
    op.create_index("ix_prompt_versions_platform", "prompt_versions", ["platform"])
    op.create_index("ix_prompt_versions_is_active", "prompt_versions", ["is_active"])

    # prompt_usage_logs table
    op.create_table(
        "prompt_usage_logs",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column(
            "prompt_version_id",
            sa.String(),
            sa.ForeignKey("prompt_versions.id"),
            nullable=False,
        ),
        sa.Column("workspace_id", sa.String(), nullable=False),
        sa.Column("post_id", sa.String(), nullable=True),
        sa.Column("content_item_id", sa.String(), nullable=True),
        sa.Column("topic", sa.String(500), nullable=True),
        sa.Column("provider", sa.String(32), nullable=True),
        sa.Column("model", sa.String(64), nullable=True),
        sa.Column("tokens_used", sa.Integer(), server_default="0"),
        sa.Column("engagement_score", sa.Float(), nullable=True),
        sa.Column("actual_engagement_rate", sa.Float(), nullable=True),
        sa.Column("scored_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_index("ix_prompt_usage_logs_prompt_version_id", "prompt_usage_logs", ["prompt_version_id"])
    op.create_index("ix_prompt_usage_logs_workspace_id", "prompt_usage_logs", ["workspace_id"])


def downgrade() -> None:
    op.drop_index("ix_prompt_usage_logs_workspace_id", table_name="prompt_usage_logs")
    op.drop_index("ix_prompt_usage_logs_prompt_version_id", table_name="prompt_usage_logs")
    op.drop_table("prompt_usage_logs")

    op.drop_index("ix_prompt_versions_is_active", table_name="prompt_versions")
    op.drop_index("ix_prompt_versions_platform", table_name="prompt_versions")
    op.drop_index("ix_prompt_versions_content_type", table_name="prompt_versions")
    op.drop_table("prompt_versions")
