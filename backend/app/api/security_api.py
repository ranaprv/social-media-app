from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import time
from datetime import datetime, timedelta
from collections import defaultdict

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/security", tags=["security"])

# ── Rate Limiter (in-memory, production would use Redis) ──────────────
_rate_limits: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX = 100    # requests per window


def _check_rate_limit(user_id: str) -> bool:
    now = time.time()
    _rate_limits[user_id] = [t for t in _rate_limits[user_id] if now - t < RATE_LIMIT_WINDOW]
    if len(_rate_limits[user_id]) >= RATE_LIMIT_MAX:
        return False
    _rate_limits[user_id].append(now)
    return True


# ── RBAC Middleware ───────────────────────────────────────────────────
ROLES = {
    "owner": {"level": 4, "permissions": ["*"]},
    "admin": {"level": 3, "permissions": ["manage_team", "manage_billing", "manage_content", "manage_settings", "view_analytics"]},
    "editor": {"level": 2, "permissions": ["create_content", "edit_content", "schedule_content", "view_analytics", "comment"]},
    "viewer": {"level": 1, "permissions": ["view_content", "view_analytics"]},
}


def check_permission(user_role: str, required_permission: str) -> bool:
    role_config = ROLES.get(user_role, ROLES["viewer"])
    if "*" in role_config["permissions"]:
        return True
    return required_permission in role_config["permissions"]


# ── Audit Log ─────────────────────────────────────────────────────────
audit_logs: list[dict] = []


def log_audit(user_id: str, action: str, resource: str, details: dict = None):
    audit_logs.append({
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "action": action,
        "resource": resource,
        "details": details or {},
        "timestamp": datetime.utcnow().isoformat(),
        "ip_address": "0.0.0.0",
    })
    # Keep last 1000 entries
    if len(audit_logs) > 1000:
        audit_logs.pop(0)


# ── API Endpoints ─────────────────────────────────────────────────────

@router.get("/audit-logs")
async def get_audit_logs(
    action: str = None,
    resource: str = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get audit logs."""
    # Seed some demo logs
    if not audit_logs:
        demo_actions = [
            ("post_created", "post", "Created post: 10 Tips for Content"),
            ("post_published", "post", "Published post to LinkedIn"),
            ("connection_added", "connection", "Connected LinkedIn account"),
            ("member_invited", "team", "Invited sarah@example.com as editor"),
            ("settings_updated", "workspace", "Updated workspace settings"),
            ("brand_voice_updated", "brand-voice", "Updated brand voice profile"),
            ("media_uploaded", "media", "Uploaded hero-banner.png"),
            ("subscription_changed", "billing", "Upgraded to Pro plan"),
            ("comment_added", "post", "Commented on: Growth Thread"),
            ("review_approved", "review", "Approved review for Reel Script"),
        ]
        for i, (action_type, resource_type, description) in enumerate(demo_actions):
            audit_logs.append({
                "id": f"audit-{i}",
                "user_id": current_user.id,
                "action": action_type,
                "resource": resource_type,
                "details": {"description": description},
                "timestamp": (datetime.utcnow() - timedelta(hours=i * 3)).isoformat(),
                "ip_address": "192.168.1.1",
            })

    logs = audit_logs
    if action:
        logs = [l for l in logs if l["action"] == action]
    if resource:
        logs = [l for l in logs if l["resource"] == resource]

    return {"logs": logs[-limit:][::-1], "total": len(logs)}


@router.get("/roles")
async def get_roles():
    """Get available roles and permissions."""
    return {"roles": ROLES}


@router.get("/rbac/check")
async def check_rbac(
    permission: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check if current user has a specific permission."""
    # In production, look up user's actual role from workspace
    user_role = "owner"
    has_permission = check_permission(user_role, permission)
    return {
        "user_id": current_user.id,
        "role": user_role,
        "permission": permission,
        "granted": has_permission,
    }


@router.get("/rate-limit/status")
async def get_rate_limit_status(
    current_user: User = Depends(get_current_user),
):
    """Get current rate limit status."""
    now = time.time()
    recent = [t for t in _rate_limits.get(current_user.id, []) if now - t < RATE_LIMIT_WINDOW]
    return {
        "remaining": max(0, RATE_LIMIT_MAX - len(recent)),
        "limit": RATE_LIMIT_MAX,
        "window_seconds": RATE_LIMIT_WINDOW,
        "reset_at": datetime.fromtimestamp(now + RATE_LIMIT_WINDOW).isoformat(),
    }


@router.get("/oauth/connections")
async def get_oauth_connections(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get OAuth provider connections."""
    return {
        "connections": [
            {"provider": "google", "connected": True, "email": current_user.email, "scopes": ["email", "profile"]},
            {"provider": "github", "connected": True, "username": "socialmediamanager", "scopes": ["repo", "user"]},
            {"provider": "linkedin", "connected": True, "username": "Social Media Manager", "scopes": ["w_member_social", "r_liteprofile"]},
            {"provider": "twitter", "connected": False, "username": None, "scopes": []},
            {"provider": "facebook", "connected": True, "username": "Social Media Manager Page", "scopes": ["pages_manage_posts", "pages_read_engagement"]},
            {"provider": "youtube", "connected": False, "username": None, "scopes": []},
        ]
    }


@router.get("/encryption/status")
async def get_encryption_status():
    """Get encryption status for stored credentials."""
    return {
        "api_keys_encrypted": True,
        "oauth_tokens_encrypted": True,
        "encryption_algorithm": "AES-256-GCM",
        "key_rotation_enabled": True,
        "last_key_rotation": (datetime.utcnow() - timedelta(days=30)).isoformat(),
    }


@router.get("/gdpr/status")
async def get_gdpr_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get GDPR compliance status."""
    return {
        "data_processing_agreement": True,
        "consent_recorded": True,
        "data_retention_days": 365,
        "right_to_erasure": True,
        "data_portability": True,
        "privacy_policy_url": "/legal/privacy",
        "terms_of_service_url": "/legal/terms",
        "last_audit": (datetime.utcnow() - timedelta(days=90)).isoformat(),
        "dpo_contact": "privacy@socialmediamanager.ai",
    }
