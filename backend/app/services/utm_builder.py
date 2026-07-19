"""UTM builder — auto-tag links per platform for analytics tracking.

Generates UTM parameters for each platform's link requirements
and tracks campaign attribution.
"""
import logging
from typing import Any
from urllib.parse import urlencode, urlparse, parse_qs, urljoin

logger = logging.getLogger(__name__)

# Platform-specific UTM defaults
PLATFORM_UTM_DEFAULTS: dict[str, dict[str, str]] = {
    "linkedin": {
        "utm_source": "linkedin",
        "utm_medium": "social",
        "utm_campaign": "linkedin_post",
    },
    "x": {
        "utm_source": "twitter",
        "utm_medium": "social",
        "utm_campaign": "tweet",
    },
    "instagram": {
        "utm_source": "instagram",
        "utm_medium": "social",
        "utm_campaign": "instagram_post",
    },
    "facebook": {
        "utm_source": "facebook",
        "utm_medium": "social",
        "utm_campaign": "facebook_post",
    },
    "youtube": {
        "utm_source": "youtube",
        "utm_medium": "video",
        "utm_campaign": "youtube_video",
    },
}

# Platform link rules
PLATFORM_LINK_RULES: dict[str, dict[str, Any]] = {
    "linkedin": {
        "max_url_length": 2000,
        "auto_shorten": True,
        "supports_card_preview": True,
        "notes": "Links in posts get card preview if Open Graph tags are set",
    },
    "x": {
        "max_url_length": 23,
        "auto_shorten": True,
        "supports_card_preview": True,
        "notes": "All URLs count as 23 chars (t.co wrapping)",
    },
    "instagram": {
        "max_url_length": 0,
        "auto_shorten": False,
        "supports_card_preview": False,
        "notes": "No clickable links in captions. Use bio link or story link sticker.",
    },
    "facebook": {
        "max_url_length": 2000,
        "auto_shorten": False,
        "supports_card_preview": True,
        "notes": "Links get automatic card preview",
    },
    "youtube": {
        "max_url_length": 2000,
        "auto_shorten": False,
        "supports_card_preview": False,
        "notes": "Links in description are clickable",
    },
}


def build_utm_url(
    url: str,
    platform: str,
    campaign_name: str = "",
    content_type: str = "",
    custom_params: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build a URL with UTM parameters for a specific platform.

    Returns the tagged URL and metadata.
    """
    defaults = PLATFORM_UTM_DEFAULTS.get(platform, {})
    parsed = urlparse(url)

    # Start with existing query params
    existing_params = parse_qs(parsed.query)

    # Build UTM params
    utm_params: dict[str, str] = {}
    utm_params["utm_source"] = defaults.get("utm_source", platform)
    utm_params["utm_medium"] = defaults.get("utm_medium", "social")

    if campaign_name:
        utm_params["utm_campaign"] = campaign_name
    else:
        utm_params["utm_campaign"] = defaults.get("utm_campaign", f"{platform}_post")

    if content_type:
        utm_params["utm_content"] = content_type

    # Custom params override defaults
    if custom_params:
        utm_params.update(custom_params)

    # Merge with existing params (existing take precedence for non-utm params)
    all_params: dict[str, str] = {}
    for key, values in existing_params.items():
        all_params[key] = values[0] if isinstance(values, list) else values
    all_params.update(utm_params)

    # Build final URL
    base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    tagged_url = f"{base_url}?{urlencode(all_params)}"

    # Check against platform limits
    rules = PLATFORM_LINK_RULES.get(platform, {})
    max_length = rules.get("max_url_length", 2000)
    needs_shortening = len(tagged_url) > max_length if max_length > 0 else False

    return {
        "original_url": url,
        "tagged_url": tagged_url,
        "platform": platform,
        "utm_params": utm_params,
        "url_length": len(tagged_url),
        "max_length": max_length,
        "needs_shortening": needs_shortening,
        "auto_shorten": rules.get("auto_shorten", False),
    }


def build_multi_platform_urls(
    url: str,
    platforms: list[str],
    campaign_name: str = "",
    content_type: str = "",
) -> dict[str, dict[str, Any]]:
    """Build tagged URLs for multiple platforms at once."""
    return {
        platform: build_utm_url(url, platform, campaign_name, content_type)
        for platform in platforms
    }


def strip_utm_params(url: str) -> str:
    """Remove UTM parameters from a URL."""
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    clean_params = {k: v[0] if isinstance(v, list) else v for k, v in params.items() if not k.startswith("utm_")}
    base = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    if clean_params:
        return f"{base}?{urlencode(clean_params)}"
    return base


def get_link_rules(platform: str) -> dict[str, Any]:
    """Get link rules for a platform."""
    return PLATFORM_LINK_RULES.get(platform, {})
