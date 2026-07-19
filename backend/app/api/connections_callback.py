"""OAuth callback handlers — completes the OAuth flow for each platform."""
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx
import logging
from datetime import datetime, timedelta

from app.core.config import get_settings
from app.core.database import get_db
from app.models.content import PlatformConnection

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/connections", tags=["connections"])


# ─── LinkedIn Callback ──────────────────────────────────────────────────────

@router.get("/linkedin/callback")
async def linkedin_callback(
    request: Request,
    code: str = "",
    state: str = "",
    db: AsyncSession = Depends(get_db),
):
    """Handle LinkedIn OAuth callback — exchange code for tokens."""
    if not code:
        logger.warning("LinkedIn callback: no authorization code received")
        return {"error": "No authorization code received", "status": "failed"}

    result = await db.execute(
        select(PlatformConnection).where(PlatformConnection.platform == "linkedin")
    )
    conn = result.scalar_one_or_none()
    if not conn:
        logger.error("LinkedIn callback: no LinkedIn connection found in DB")
        return {"error": "No LinkedIn connection found. Connect first.", "status": "failed"}

    meta = conn.meta or {}
    settings = get_settings()

    # Prefer stored credentials, fall back to .env
    client_id = meta.get("client_id") or settings.LINKEDIN_CLIENT_ID
    client_secret = meta.get("client_secret") or settings.LINKEDIN_CLIENT_SECRET

    if not client_id or not client_secret:
        logger.error(
            "LinkedIn callback: missing client_id or client_secret "
            "(meta=%s, env_id_present=%s, env_secret_present=%s)",
            bool(meta), bool(settings.LINKEDIN_CLIENT_ID), bool(settings.LINKEDIN_CLIENT_SECRET),
        )
        return {"error": "Missing client credentials", "status": "failed"}

    # Use configured redirect_uri — must match LinkedIn Developer Portal exactly
    redirect_uri = settings.LINKEDIN_REDIRECT_URI
    logger.info("LinkedIn callback: exchanging code for token (client_id=%s..., redirect_uri=%s)", client_id[:8], redirect_uri)

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            token_response = await client.post(
                "https://www.linkedin.com/oauth/v2/accessToken",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
            )

        token_data = token_response.json()
        logger.info("LinkedIn token response: status=%s, keys=%s", token_response.status_code, list(token_data.keys()))

        if "access_token" not in token_data:
            error_msg = token_data.get("error_description", token_data.get("error", "Token exchange failed"))
            logger.error("LinkedIn token exchange failed: %s", error_msg)
            return {"error": error_msg, "status": "failed"}

    except httpx.TimeoutException:
        logger.error("LinkedIn token exchange timed out")
        return {"error": "LinkedIn API timeout", "status": "failed"}
    except Exception as e:
        logger.error("LinkedIn token exchange exception: %s", e)
        return {"error": f"Token exchange error: {e}", "status": "failed"}

    access_token = token_data["access_token"]

    # Get profile info and author_urn
    profile_info = {}
    author_urn = ""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # Try OpenID Connect userinfo first
            r = await client.get(
                "https://api.linkedin.com/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if r.status_code == 200:
                userinfo = r.json()
                profile_info = {
                    "id": userinfo.get("sub", ""),
                    "full_name": userinfo.get("name", ""),
                }
                author_urn = f"urn:li:person:{userinfo.get('sub', '')}"
            else:
                # Fallback: try /v2/me
                r2 = await client.get(
                    "https://api.linkedin.com/v2/me",
                    params={"projection": "(id,localizedFirstName,localizedLastName)"},
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                if r2.status_code == 200:
                    data = r2.json()
                    pid = data.get("id", "")
                    profile_info = {
                        "id": pid,
                        "full_name": f"{data.get('localizedFirstName', '')} {data.get('localizedLastName', '')}".strip(),
                    }
                    author_urn = f"urn:li:person:{pid}"
                else:
                    logger.warning("LinkedIn profile fetch returned %s: %s", r2.status_code, r2.text[:200])
    except Exception as e:
        logger.warning("LinkedIn profile fetch failed: %s", e)

    conn.access_token = access_token
    refresh_tok = token_data.get("refresh_token")
    if refresh_tok:
        conn.refresh_token = refresh_tok
        meta["refresh_token"] = refresh_tok
    meta["profile_info"] = profile_info
    meta["token_obtained"] = True
    meta["author_urn"] = author_urn
    meta["token_expires_at"] = (datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 5184000))).isoformat()
    conn.meta = meta
    await db.flush()

    logger.info("LinkedIn connected: %s (id=%s)", profile_info.get("full_name", "Unknown"), conn.id)
    return {
        "status": "connected",
        "platform": "linkedin",
        "profile": profile_info,
        "message": f"LinkedIn connected: {profile_info.get('full_name', 'Unknown')}",
    }


# ─── YouTube Callback ───────────────────────────────────────────────────────

@router.get("/youtube/callback")
async def youtube_callback(request: Request, code: str = "", state: str = "", db: AsyncSession = Depends(get_db)):
    """Handle YouTube OAuth callback — exchange code for tokens."""
    if not code:
        logger.warning("YouTube callback: no authorization code received")
        return {"error": "No authorization code received", "status": "failed"}

    result = await db.execute(
        select(PlatformConnection).where(PlatformConnection.platform == "youtube")
    )
    conn = result.scalar_one_or_none()
    if not conn:
        logger.error("YouTube callback: no YouTube connection found in DB")
        return {"error": "No YouTube connection found. Connect first.", "status": "failed"}

    meta = conn.meta or {}
    settings = get_settings()

    # Prefer stored credentials, fall back to .env
    client_id = meta.get("client_id") or settings.YOUTUBE_CLIENT_ID
    client_secret = meta.get("client_secret") or settings.YOUTUBE_CLIENT_SECRET

    if not client_id or not client_secret:
        logger.error(
            "YouTube callback: missing client_id or client_secret "
            "(meta=%s, env_id_present=%s, env_secret_present=%s)",
            bool(meta), bool(settings.YOUTUBE_CLIENT_ID), bool(settings.YOUTUBE_CLIENT_SECRET),
        )
        return {"error": "Missing client credentials", "status": "failed"}

    # Use configured redirect_uri — must match Google Cloud Console exactly
    redirect_uri = settings.YOUTUBE_REDIRECT_URI
    logger.info("YouTube callback: exchanging code for token (client_id=%s..., redirect_uri=%s)", client_id[:20], redirect_uri)

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri,
                },
            )

        token_data = token_response.json()
        logger.info("YouTube token response: status=%s, keys=%s", token_response.status_code, list(token_data.keys()))

        if "access_token" not in token_data:
            error_msg = token_data.get("error_description", token_data.get("error", "Token exchange failed"))
            logger.error("YouTube token exchange failed: %s", error_msg)
            return {"error": error_msg, "status": "failed"}

    except httpx.TimeoutException:
        logger.error("YouTube token exchange timed out")
        return {"error": "Google API timeout", "status": "failed"}
    except Exception as e:
        logger.error("YouTube token exchange exception: %s", e)
        return {"error": f"Token exchange error: {e}", "status": "failed"}

    access_token = token_data["access_token"]
    channel_info = {}
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "https://www.googleapis.com/youtube/v3/channels",
            params={"part": "snippet,statistics", "mine": "true"},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if r.status_code == 200:
            items = r.json().get("items", [])
            if items:
                snippet = items[0].get("snippet", {})
                stats = items[0].get("statistics", {})
                channel_info = {
                    "title": snippet.get("title", ""),
                    "subscribers": stats.get("subscriberCount", "0"),
                    "videos": stats.get("videoCount", "0"),
                }

    conn.access_token = access_token
    refresh_tok = token_data.get("refresh_token")
    if refresh_tok:
        conn.refresh_token = refresh_tok
        meta["refresh_token"] = refresh_tok
    meta["channel_info"] = channel_info
    meta["token_obtained"] = True
    meta["token_expires_at"] = (datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600))).isoformat()
    conn.meta = meta
    await db.flush()

    return {
        "status": "connected",
        "platform": "youtube",
        "channel": channel_info,
        "message": f"YouTube connected: {channel_info.get('title', 'Unknown')}",
    }


# ─── Facebook Callback ──────────────────────────────────────────────────────

@router.get("/facebook/callback")
async def facebook_callback(request: Request, code: str = "", db: AsyncSession = Depends(get_db)):
    """Handle Facebook OAuth callback — exchange code for tokens."""
    if not code:
        logger.warning("Facebook callback: no authorization code received")
        return {"error": "No authorization code received", "status": "failed"}

    result = await db.execute(
        select(PlatformConnection).where(PlatformConnection.platform == "facebook")
    )
    conn = result.scalar_one_or_none()
    if not conn:
        logger.error("Facebook callback: no Facebook connection found in DB")
        return {"error": "No Facebook connection found. Connect first.", "status": "failed"}

    meta = conn.meta or {}
    settings = get_settings()

    # Prefer stored credentials, fall back to .env
    client_id = meta.get("client_id") or settings.FACEBOOK_APP_ID
    client_secret = meta.get("client_secret") or settings.FACEBOOK_APP_SECRET

    if not client_id or not client_secret:
        logger.error(
            "Facebook callback: missing client_id or client_secret "
            "(meta=%s, env_id_present=%s, env_secret_present=%s)",
            bool(meta), bool(settings.FACEBOOK_APP_ID), bool(settings.FACEBOOK_APP_SECRET),
        )
        return {"error": "Missing client credentials", "status": "failed"}

    # Use configured redirect_uri — must match Facebook App Settings exactly
    redirect_uri = settings.FACEBOOK_REDIRECT_URI
    logger.info("Facebook callback: exchanging code for token (app_id=%s..., redirect_uri=%s)", client_id[:10], redirect_uri)

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            token_response = await client.get(
                "https://graph.facebook.com/v19.0/oauth/access_token",
                params={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                    "code": code,
                },
            )

        token_data = token_response.json()
        logger.info("Facebook token response: status=%s, keys=%s", token_response.status_code, list(token_data.keys()))

        if "access_token" not in token_data:
            error_msg = token_data.get("error", {}).get("message", "Token exchange failed")
            logger.error("Facebook token exchange failed: %s", error_msg)
            return {"error": error_msg, "status": "failed"}

    except httpx.TimeoutException:
        logger.error("Facebook token exchange timed out")
        return {"error": "Facebook API timeout", "status": "failed"}
    except Exception as e:
        logger.error("Facebook token exchange exception: %s", e)
        return {"error": f"Token exchange error: {e}", "status": "failed"}

    access_token = token_data["access_token"]

    # Exchange for long-lived token
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "https://graph.facebook.com/v19.0/oauth/access_token",
            params={
                "grant_type": "fb_exchange_token",
                "client_id": client_id,
                "client_secret": client_secret,
                "fb_exchange_token": access_token,
            },
        )
    long_data = r.json()
    access_token = long_data.get("access_token", access_token)

    # Get page info
    page_info = {}
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "https://graph.facebook.com/v19.0/me/accounts",
            params={"access_token": access_token},
        )
        if r.status_code == 200:
            pages = r.json().get("data", [])
            if pages:
                page = pages[0]
                page_info = {
                    "page_name": page.get("name", ""),
                    "page_id": page.get("id", ""),
                    "category": page.get("category", ""),
                }

    conn.access_token = access_token
    meta["page_info"] = page_info
    meta["token_obtained"] = True
    meta["token_expires_at"] = (datetime.utcnow() + timedelta(days=59)).isoformat()
    conn.meta = meta
    await db.flush()

    return {
        "status": "connected",
        "platform": "facebook",
        "page": page_info,
        "message": f"Facebook connected: {page_info.get('page_name', 'Unknown')}",
    }


# ─── Connection Health Check ────────────────────────────────────────────────

@router.get("/health-check")
async def connection_health_check(
    platform: str,
    db: AsyncSession = Depends(get_db),
):
    """Test stored token by making a lightweight API call."""
    result = await db.execute(
        select(PlatformConnection).where(PlatformConnection.platform == platform)
    )
    conn = result.scalar_one_or_none()
    if not conn or not conn.access_token:
        raise HTTPException(status_code=404, detail=f"No {platform} connection found")

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            if platform == "linkedin":
                r = await client.get(
                    "https://api.linkedin.com/v2/userinfo",
                    headers={"Authorization": f"Bearer {conn.access_token}"},
                )
            elif platform == "youtube":
                r = await client.get(
                    "https://www.googleapis.com/oauth2/v3/userinfo",
                    headers={"Authorization": f"Bearer {conn.access_token}"},
                )
            elif platform == "facebook":
                r = await client.get(
                    "https://graph.facebook.com/v19.0/me",
                    params={"fields": "id,name", "access_token": conn.access_token},
                )
            else:
                return {"status": "unknown_platform", "healthy": False}

            if r.status_code == 200:
                return {"status": "healthy", "platform": platform, "user": r.json()}
            else:
                # Token might be expired — attempt refresh
                from app.services.token_refresh import get_valid_token
                new_token = await get_valid_token(conn, db)
                if new_token and new_token != conn.access_token:
                    return {"status": "refreshed_and_healthy", "platform": platform}
                return {"status": "unhealthy", "platform": platform, "error": r.status_code}

    except Exception as e:
        return {"status": "error", "platform": platform, "error": str(e)}
