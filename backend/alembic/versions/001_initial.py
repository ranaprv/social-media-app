"""initial schema

Revision ID: 001_initial
Revises: 
Create Date: 2026-07-16
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users
    op.create_table(
        "users",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("email", sa.String(), unique=True, nullable=False, index=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("image", sa.String(), nullable=True),
        sa.Column("hashed_password", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # Accounts (OAuth)
    op.create_table(
        "accounts",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("provider_account_id", sa.String(), nullable=False),
        sa.Column("refresh_token", sa.String(), nullable=True),
        sa.Column("access_token", sa.String(), nullable=True),
        sa.Column("expires_at", sa.String(), nullable=True),
        sa.Column("token_type", sa.String(), nullable=True),
        sa.Column("scope", sa.String(), nullable=True),
        sa.Column("id_token", sa.String(), nullable=True),
        sa.Column("session_state", sa.String(), nullable=True),
    )

    # Sessions
    op.create_table(
        "sessions",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("session_token", sa.String(), unique=True, nullable=False),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("expires", sa.DateTime(), nullable=False),
    )

    # Workspaces
    op.create_table(
        "workspaces",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), unique=True, nullable=False),
        sa.Column("owner_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # Workspace Members
    op.create_table(
        "workspace_members",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("workspace_id", sa.String(), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("role", sa.String(), default="editor"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # Posts
    op.create_table(
        "posts",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("workspace_id", sa.String(), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("author_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("media_urls", sa.ARRAY(sa.String()), default=[]),
        sa.Column("platform", sa.String(), nullable=False),
        sa.Column("status", sa.String(), default="draft"),
        sa.Column("scheduled_at", sa.DateTime(), nullable=True),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("platform_post_id", sa.String(), nullable=True),
        sa.Column("metadata", sa.JSON(), default={}),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_posts_workspace_id", "posts", ["workspace_id"])
    op.create_index("ix_posts_platform", "posts", ["platform"])
    op.create_index("ix_posts_status", "posts", ["status"])

    # Post Versions
    op.create_table(
        "post_versions",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("post_id", sa.String(), sa.ForeignKey("posts.id"), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # Platform Connections
    op.create_table(
        "platform_connections",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("workspace_id", sa.String(), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("platform", sa.String(), nullable=False),
        sa.Column("platform_user_id", sa.String(), nullable=False),
        sa.Column("platform_username", sa.String(), nullable=False),
        sa.Column("access_token", sa.String(), nullable=False),
        sa.Column("refresh_token", sa.String(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("metadata", sa.JSON(), default={}),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # Content Calendar
    op.create_table(
        "content_calendars",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("workspace_id", sa.String(), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("post_id", sa.String(), sa.ForeignKey("posts.id"), unique=True, nullable=False),
        sa.Column("date", sa.DateTime(), nullable=False),
        sa.Column("time_slot", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # Analytics Metrics
    op.create_table(
        "analytics_metrics",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("post_id", sa.String(), sa.ForeignKey("posts.id"), nullable=False),
        sa.Column("platform", sa.String(), nullable=False),
        sa.Column("impressions", sa.Integer(), default=0),
        sa.Column("reach", sa.Integer(), default=0),
        sa.Column("engagement", sa.Integer(), default=0),
        sa.Column("likes", sa.Integer(), default=0),
        sa.Column("comments", sa.Integer(), default=0),
        sa.Column("shares", sa.Integer(), default=0),
        sa.Column("clicks", sa.Integer(), default=0),
        sa.Column("watch_time", sa.Integer(), nullable=True),
        sa.Column("subscribers", sa.Integer(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # Brand Voice
    op.create_table(
        "brand_voices",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("workspace_id", sa.String(), sa.ForeignKey("workspaces.id"), unique=True, nullable=False),
        sa.Column("tone", sa.String(), nullable=True),
        sa.Column("writing_style", sa.String(), nullable=True),
        sa.Column("cta_style", sa.String(), nullable=True),
        sa.Column("emoji_usage", sa.String(), nullable=True),
        sa.Column("formatting", sa.String(), nullable=True),
        sa.Column("vocabulary", sa.String(), nullable=True),
        sa.Column("technical_depth", sa.String(), nullable=True),
        sa.Column("sample_posts", sa.ARRAY(sa.String()), default=[]),
        sa.Column("training_sources", sa.JSON(), default=[]),
        sa.Column("approval_history", sa.JSON(), default=[]),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # Assets
    op.create_table(
        "assets",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("workspace_id", sa.String(), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("url", sa.String(), nullable=False),
        sa.Column("metadata", sa.JSON(), default={}),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # Activities
    op.create_table(
        "activities",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("metadata", sa.JSON(), default={}),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("activities")
    op.drop_table("assets")
    op.drop_table("brand_voices")
    op.drop_table("analytics_metrics")
    op.drop_table("content_calendars")
    op.drop_table("platform_connections")
    op.drop_table("post_versions")
    op.drop_table("posts")
    op.drop_table("workspace_members")
    op.drop_table("workspaces")
    op.drop_table("sessions")
    op.drop_table("accounts")
    op.drop_table("users")
