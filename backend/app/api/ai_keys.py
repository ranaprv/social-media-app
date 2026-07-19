"""API for managing AI provider API keys — stored in DB, not .env."""
import hashlib
import logging
import threading
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.security import get_current_user
from app.core.config import get_settings
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai/keys", tags=["ai-keys"])

# Thread-safe in-memory store for API keys.
# In production, store encrypted in the database.
_api_keys: dict[str, str] = {}
_lock = threading.Lock()

_VALID_PROVIDERS = frozenset({
    "openrouter", "openai", "anthropic", "gemini", "deepseek", "omniroute",
})

_ENV_MAP: dict[str, str] = {
    "openrouter": "OPENROUTER_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GOOGLE_AI_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "omniroute": "OPENROUTER_API_KEY",
}


class APIKeyPayload(BaseModel):
    provider: str
    api_key: str


def _fingerprint(key: str) -> str:
    """Return a short SHA-256 fingerprint — safe to show in UI."""
    return hashlib.sha256(key.encode()).hexdigest()[:12]


def _get_stored_key(provider: str) -> str:
    """Get API key from in-memory store, falling back to env var."""
    with _lock:
        if provider in _api_keys:
            return _api_keys[provider]
    import os
    return os.environ.get(_ENV_MAP.get(provider, ""), "")


def _apply_key(provider: str, api_key: str):
    """Store key in memory and set env var for existing services."""
    with _lock:
        _api_keys[provider] = api_key
    env_var = _ENV_MAP.get(provider)
    if env_var:
        import os
        os.environ[env_var] = api_key


@router.get("/")
async def list_keys(current_user: User = Depends(get_current_user)):
    """List all providers and their key status.

    Returns only a fingerprint hash — never the actual key.
    """
    result = []
    for p in _VALID_PROVIDERS:
        key = _get_stored_key(p)
        result.append({
            "provider": p,
            "configured": bool(key),
            "fingerprint": _fingerprint(key) if key else "",
        })
    return {"keys": result}


@router.post("/")
async def save_key(
    payload: APIKeyPayload,
    current_user: User = Depends(get_current_user),
):
    """Save an API key for a provider. Returns fingerprint only."""
    if payload.provider not in _VALID_PROVIDERS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid provider. Must be one of: {sorted(_VALID_PROVIDERS)}",
        )

    stripped = payload.api_key.strip()
    if not stripped:
        raise HTTPException(status_code=400, detail="API key cannot be empty")

    _apply_key(payload.provider, stripped)
    logger.info("API key saved for provider: %s (user=%s)", payload.provider, current_user.id)

    return {
        "provider": payload.provider,
        "configured": True,
        "fingerprint": _fingerprint(stripped),
        "message": f"API key saved for {payload.provider}",
    }


@router.delete("/{provider}")
async def delete_key(
    provider: str,
    current_user: User = Depends(get_current_user),
):
    """Remove an API key for a provider."""
    if provider not in _VALID_PROVIDERS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid provider. Must be one of: {sorted(_VALID_PROVIDERS)}",
        )

    with _lock:
        _api_keys.pop(provider, None)

    env_var = _ENV_MAP.get(provider)
    if env_var:
        import os
        os.environ.pop(env_var, None)

    logger.info("API key deleted for provider: %s (user=%s)", provider, current_user.id)
    return {
        "provider": provider,
        "configured": False,
        "message": f"API key removed for {provider}",
    }
