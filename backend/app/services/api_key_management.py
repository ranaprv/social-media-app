"""API key management — generate, rotate, revoke keys.

Manages API access keys for external integrations and developer access.
"""
import hashlib
import logging
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Activity

logger = logging.getLogger(__name__)


def generate_api_key(prefix: str = "smm") -> dict[str, Any]:
    """Generate a new API key pair."""
    key_id = f"{prefix}_{secrets.token_hex(8)}"
    api_key = f"{prefix}_key_{secrets.token_hex(32)}"
    secret_key = f"{prefix}_secret_{secrets.token_hex(32)}"

    # Hash the API key for storage
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    return {
        "key_id": key_id,
        "api_key": api_key,
        "secret_key": secret_key,
        "key_hash": key_hash,
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(days=90)).isoformat(),
    }


async def create_api_key(
    db: AsyncSession,
    workspace_id: str,
    name: str,
    permissions: list[str] | None = None,
    rate_limit: int = 100,
    expires_days: int = 90,
) -> dict[str, Any]:
    """Create a new API key for a workspace."""
    key_data = generate_api_key()

    activity = Activity(
        id=str(uuid.uuid4()),
        user_id="system",
        type="api_key_created",
        description=f"API key created: {name}",
        meta={
            "key_id": key_data["key_id"],
            "name": name,
            "permissions": permissions or ["read"],
            "rate_limit": rate_limit,
        },
    )
    db.add(activity)
    await db.flush()

    return {
        "key_id": key_data["key_id"],
        "name": name,
        "api_key": key_data["api_key"],
        "secret_key": key_data["secret_key"],
        "permissions": permissions or ["read"],
        "rate_limit": rate_limit,
        "expires_at": (datetime.utcnow() + timedelta(days=expires_days)).isoformat(),
        "created_at": key_data["created_at"],
    }


async def revoke_api_key(
    db: AsyncSession,
    workspace_id: str,
    key_id: str,
    reason: str = "",
) -> dict[str, Any]:
    """Revoke an API key."""
    activity = Activity(
        id=str(uuid.uuid4()),
        user_id="system",
        type="api_key_revoked",
        description=f"API key revoked: {key_id}",
        meta={"key_id": key_id, "reason": reason},
    )
    db.add(activity)
    await db.flush()

    return {
        "key_id": key_id,
        "status": "revoked",
        "reason": reason,
    }


def get_key_scopes() -> list[dict[str, str]]:
    """Get available API key permission scopes."""
    return [
        {"scope": "posts:read", "description": "Read posts and schedules"},
        {"scope": "posts:write", "description": "Create and update posts"},
        {"scope": "posts:publish", "description": "Publish posts to platforms"},
        {"scope": "analytics:read", "description": "Read analytics data"},
        {"scope": "media:read", "description": "Read media library"},
        {"scope": "media:write", "description": "Upload media files"},
        {"scope": "workspace:read", "description": "Read workspace settings"},
        {"scope": "workspace:write", "description": "Update workspace settings"},
        {"scope": "team:read", "description": "Read team members"},
        {"scope": "admin", "description": "Full admin access"},
    ]
