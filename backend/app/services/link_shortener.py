"""Link shortening service — Bitly API + TinyURL fallback."""
import httpx
import hashlib
import string
import logging
from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Simple base62 encoding for short IDs
ALPHABET = string.ascii_letters + string.digits


def _short_id(url: str, length: int = 7) -> str:
    """Generate a short ID from URL hash."""
    h = hashlib.md5(url.encode()).hexdigest()
    num = int(h[:12], 16)
    result = []
    for _ in range(length):
        result.append(ALPHABET[num % 62])
        num //= 62
    return "".join(result)


async def shorten_url(url: str) -> dict:
    """Shorten a URL using Bitly or TinyURL fallback."""
    settings = get_settings()

    # Try Bitly first
    if settings.BITLY_ACCESS_TOKEN:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://api-ssl.bitly.com/v4/shorten",
                    headers={"Authorization": f"Bearer {settings.BITLY_ACCESS_TOKEN}", "Content-Type": "application/json"},
                    json={"long_url": url},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return {
                        "short_url": data.get("link", ""),
                        "short_id": data.get("id", "").split("/")[-1],
                        "original_url": url,
                        "provider": "bitly",
                    }
        except Exception as e:
            logger.warning(f"Bitly failed: {e}")

    # Fallback: TinyURL
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"https://tinyurl.com/api-create.php?url={url}")
            if resp.status_code == 200:
                short_url = resp.text.strip()
                short_id = short_url.split("/")[-1]
                return {
                    "short_url": short_url,
                    "short_id": short_id,
                    "original_url": url,
                    "provider": "tinyurl",
                }
    except Exception as e:
        logger.warning(f"TinyURL failed: {e}")

    # Ultimate fallback: generate local short ID
    sid = _short_id(url)
    return {
        "short_url": f"/r/{sid}",
        "short_id": sid,
        "original_url": url,
        "provider": "local",
    }


async def get_click_stats(short_id: str) -> dict:
    """Get click statistics for a short link."""
    # In production, query from short_links table
    return {
        "short_id": short_id,
        "total_clicks": 0,
        "unique_visitors": 0,
        "referrers": [],
        "countries": [],
        "daily_clicks": [],
    }
