"""Token refresh service — automatically refreshes expired OAuth tokens for all platforms."""
import httpx
import logging
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import get_settings
from app.models.content import PlatformConnection

logger = logging.getLogger(__name__)

LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
YOUTUBE_TOKEN_URL = "https://oauth2.googleapis.com/token"
FACEBOOK_TOKEN_URL = "https://graph.facebook.com/v19.0/oauth/access_token"


async def refresh_linkedin_token(conn: PlatformConnection, db: AsyncSession) -> str | None:
    """Refresh LinkedIn OAuth 2.0 access token using refresh token."""
    settings = get_settings()
    meta = conn.meta or {}
    refresh_token = meta.get("refresh_token") or getattr(conn, "refresh_token", None)
    
    if not refresh_token:
        logger.warning("LinkedIn: no refresh token available for connection %s", conn.id)
        return None

    client_id = meta.get("client_id") or settings.LINKEDIN_CLIENT_ID
    client_secret = meta.get("client_secret") or settings.LINKEDIN_CLIENT_SECRET

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                LINKEDIN_TOKEN_URL,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
            )

            if response.status_code == 200:
                data = response.json()
                new_token = data.get("access_token", "")
                new_refresh = data.get("refresh_token", refresh_token)
                
                conn.access_token = new_token
                if new_refresh != refresh_token:
                    meta["refresh_token"] = new_refresh
                    conn.refresh_token = new_refresh
                meta["token_obtained"] = True
                meta["last_refreshed"] = datetime.utcnow().isoformat()
                conn.meta = meta
                await db.flush()
                
                logger.info("LinkedIn token refreshed for connection %s", conn.id)
                return new_token
            else:
                logger.error("LinkedIn token refresh failed: %s", response.text[:200])
                return None

    except Exception as e:
        logger.error("LinkedIn token refresh error: %s", e)
        return None


async def refresh_youtube_token(conn: PlatformConnection, db: AsyncSession) -> str | None:
    """Refresh YouTube/Google OAuth 2.0 access token using refresh token."""
    settings = get_settings()
    meta = conn.meta or {}
    refresh_token = meta.get("refresh_token") or getattr(conn, "refresh_token", None)
    
    if not refresh_token:
        logger.warning("YouTube: no refresh token available for connection %s", conn.id)
        return None

    client_id = meta.get("client_id") or settings.YOUTUBE_CLIENT_ID
    client_secret = meta.get("client_secret") or settings.YOUTUBE_CLIENT_SECRET

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                YOUTUBE_TOKEN_URL,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
            )

            if response.status_code == 200:
                data = response.json()
                new_token = data.get("access_token", "")
                
                conn.access_token = new_token
                meta["token_obtained"] = True
                meta["last_refreshed"] = datetime.utcnow().isoformat()
                conn.meta = meta
                await db.flush()
                
                logger.info("YouTube token refreshed for connection %s", conn.id)
                return new_token
            else:
                logger.error("YouTube token refresh failed: %s", response.text[:200])
                return None

    except Exception as e:
        logger.error("YouTube token refresh error: %s", e)
        return None


async def refresh_facebook_token(conn: PlatformConnection, db: AsyncSession) -> str | None:
    """Refresh Facebook OAuth access token using long-lived token exchange."""
    settings = get_settings()
    meta = conn.meta or {}
    
    current_token = conn.access_token
    if not current_token:
        logger.warning("Facebook: no access token available for connection %s", conn.id)
        return None

    client_id = meta.get("client_id") or settings.FACEBOOK_APP_ID
    client_secret = meta.get("client_secret") or settings.FACEBOOK_APP_SECRET

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(
                FACEBOOK_TOKEN_URL,
                params={
                    "grant_type": "fb_exchange_token",
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "fb_exchange_token": current_token,
                },
            )

            if response.status_code == 200:
                data = response.json()
                new_token = data.get("access_token", "")
                
                conn.access_token = new_token
                meta["token_obtained"] = True
                meta["last_refreshed"] = datetime.utcnow().isoformat()
                conn.meta = meta
                await db.flush()
                
                logger.info("Facebook token refreshed for connection %s", conn.id)
                return new_token
            else:
                logger.error("Facebook token refresh failed: %s", response.text[:200])
                return None

    except Exception as e:
        logger.error("Facebook token refresh error: %s", e)
        return None


async def get_valid_token(conn: PlatformConnection, db: AsyncSession) -> str:
    """Get a valid access token, refreshing if necessary."""
    token = conn.access_token
    if not token:
        return ""

    platform = conn.platform.lower()
    refreshers = {
        "linkedin": refresh_linkedin_token,
        "youtube": refresh_youtube_token,
        "facebook": refresh_facebook_token,
    }

    refresher = refreshers.get(platform)
    if refresher:
        new_token = await refresher(conn, db)
        if new_token:
            return new_token

    return token


async def refresh_all_tokens(db: AsyncSession):
    """Refresh tokens for all connected platforms."""
    result = await db.execute(
        select(PlatformConnection).where(PlatformConnection.access_token.isnot(None))
    )
    connections = result.scalars().all()
    
    for conn in connections:
        logger.info("Refreshing token for %s (%s)", conn.platform, conn.id)
        await get_valid_token(conn, db)
    
    await db.commit()
    logger.info("Token refresh completed for %d connections", len(connections))


async def get_fresh_token(workspace_id: str, platform: str) -> str:
    """Get a fresh access token for the given platform and workspace.
    
    This is the main entry point used by Celery tasks.
    """
    from app.core.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(PlatformConnection).where(
                PlatformConnection.workspace_id == workspace_id,
                PlatformConnection.platform == platform,
            )
        )
        conn = result.scalar_one_or_none()
        
        if not conn or not conn.access_token:
            logger.warning("No connection or token for %s in workspace %s", platform, workspace_id)
            return ""
        
        return await get_valid_token(conn, session)


async def refresh_expiring_tokens():
    """Refresh tokens that are about to expire (within 10 minutes)."""
    from app.core.database import AsyncSessionLocal
    from datetime import datetime, timedelta
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(PlatformConnection).where(PlatformConnection.access_token.isnot(None))
        )
        connections = result.scalars().all()
        
        refreshed = 0
        for conn in connections:
            meta = conn.meta or {}
            expires_at_str = meta.get("token_expires_at")
            
            if expires_at_str:
                try:
                    expires_at = datetime.fromisoformat(expires_at_str)
                    if expires_at < datetime.utcnow() + timedelta(minutes=10):
                        logger.info("Token expiring soon for %s, refreshing...", conn.platform)
                        new_token = await get_valid_token(conn, session)
                        if new_token:
                            refreshed += 1
                except (ValueError, TypeError):
                    pass
        
        if refreshed:
            await session.commit()
        
        logger.info("Token refresh check completed, refreshed %d tokens", refreshed)
        return {"refreshed": refreshed}
