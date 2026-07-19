"""add platform and content_type to assets

Revision ID: 002_add_asset_platform
Revises: 001_initial
Create Date: 2026-07-17
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "002_add_asset_platform"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("assets", sa.Column("platform", sa.String(32), index=True))
    op.add_column("assets", sa.Column("content_type", sa.String(64), index=True))


def downgrade() -> None:
    op.drop_index("ix_assets_content_type", table_name="assets")
    op.drop_index("ix_assets_platform", table_name="assets")
    op.drop_column("assets", "content_type")
    op.drop_column("assets", "platform")
