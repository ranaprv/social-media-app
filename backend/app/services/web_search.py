"""Web search service — free web search via DuckDuckGo HTML API.

No API key required. Uses DuckDuckGo's HTML endpoint for search results.
Falls back gracefully when search is unavailable.

Design:
    - DuckDuckGo HTML endpoint: free, no key, rate-limited
    - Extracts: titles, snippets, URLs from search results
    - Caches results for 5 minutes to reduce duplicate requests
    - Async with httpx for non-blocking I/O
"""
import asyncio
import hashlib
import logging
import re
import time
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Cache: key → (timestamp, data)
_search_cache: dict[str, tuple[float, list[dict]]] = {}
_CACHE_TTL = 300  # 5 minutes


async def web_search(
    query: str,
    max_results: int = 5,
    region: str = "wt-wt",  # wt-wt = worldwide
) -> list[dict]:
    """Search the web via DuckDuckGo HTML endpoint.

    Returns list of {title, snippet, url} dicts.
    No API key required.
    """
    # Check cache
    cache_key = hashlib.md5(f"{query}:{max_results}:{region}".encode()).hexdigest()
    if cache_key in _search_cache:
        ts, data = _search_cache[cache_key]
        if time.time() - ts < _CACHE_TTL:
            return data[:max_results]

    try:
        results = await _search_duckduckgo(query, max_results, region)
    except Exception:
        results = []

    # Cache results
    if results:
        _search_cache[cache_key] = (time.time(), results)

    return results[:max_results]


async def _search_duckduckgo(
    query: str,
    max_results: int,
    region: str,
) -> list[dict]:
    """Search DuckDuckGo HTML endpoint."""
    try:
        url = "https://html.duckduckgo.com/html/"
        params = {"q": query, "kl": region}
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; SocialMediaManager/1.0)",
        }

        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.post(url, data=params, headers=headers)
            response.raise_for_status()

        return _parse_html_results(response.text, max_results)

    except httpx.TimeoutException:
        logger.warning("DuckDuckGo search timed out for query: %s", query[:50])
        return []
    except httpx.HTTPStatusError as e:
        logger.warning("DuckDuckGo search HTTP error %d for query: %s", e.response.status_code, query[:50])
        return []
    except Exception as e:
        logger.warning("DuckDuckGo search failed: %s", e)
        return []


def _parse_html_results(html: str, max_results: int) -> list[dict]:
    """Parse DuckDuckGo HTML search results."""
    results = []

    # Find result blocks — DuckDuckGo uses class="result__body" or "result"
    # Extract titles, snippets, and URLs using regex (stdlib only)
    result_blocks = re.findall(
        r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?'
        r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>',
        html,
        re.DOTALL,
    )

    for url, title, snippet in result_blocks[:max_results]:
        # Clean HTML tags
        title = re.sub(r'<[^>]+>', '', title).strip()
        snippet = re.sub(r'<[^>]+>', '', snippet).strip()
        url = re.sub(r'<[^>]+>', '', url).strip()

        # Decode DuckDuckGo redirect URLs
        if "uddg=" in url:
            import urllib.parse
            parsed = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
            url = parsed.get("uddg", [url])[0]

        if title and snippet:
            results.append({
                "title": title,
                "snippet": snippet,
                "url": url,
            })

    # Fallback: try simpler pattern if main pattern didn't match
    if not results:
        titles = re.findall(r'<a[^>]*class="result__a"[^>]*>(.*?)</a>', html, re.DOTALL)
        snippets = re.findall(r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
        urls = re.findall(r'<a[^>]*class="result__a"[^>]*href="([^"]*)"', html)

        for i in range(min(len(titles), len(snippets), len(urls), max_results)):
            title = re.sub(r'<[^>]+>', '', titles[i]).strip()
            snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip()
            url = urls[i].strip()

            if "uddg=" in url:
                import urllib.parse
                parsed = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
                url = parsed.get("uddg", [url])[0]

            if title:
                results.append({"title": title, "snippet": snippet, "url": url})

    return results


async def research_topic(
    topic: str,
    platform: str = "linkedin",
    aspect: str = "general",
) -> dict[str, Any]:
    """Research a topic using web search + LLM analysis.

    Combines web search results with LLM analysis to produce
    actionable research insights for content generation.

    Args:
        topic: The topic to research
        platform: Target platform
        aspect: What to research — "general", "trends", "competitors", "hooks"

    Returns:
        {
            "web_results": [...],       # raw search results
            "summary": "...",           # LLM-analyzed summary
            "key_insights": [...],      # extracted insights
            "suggested_angles": [...],  # content angles to explore
            "source_urls": [...],       # source URLs for reference
        }
    """
    # Build search query based on aspect
    query = _build_search_query(topic, platform, aspect)

    # Execute web search
    web_results = await web_search(query, max_results=5)

    if not web_results:
        return {
            "web_results": [],
            "summary": f"No web results found for '{topic}'. Using topic knowledge only.",
            "key_insights": [],
            "suggested_angles": [],
            "source_urls": [],
        }

    # Build context from search results for LLM analysis
    results_text = "\n".join(
        f"- {r['title']}: {r['snippet']}" for r in web_results
    )

    # Use LLM to analyze and extract insights
    from app.services.llm import call_llm_json

    analysis_prompt = f"""Analyze these web search results about "{topic}" for {platform} content creation.

Search results:
{results_text}

Extract:
1. A 2-3 sentence summary of the topic's current state
2. 3-5 key insights that would make good content
3. 2-3 specific content angles to explore
4. Any trending subtopics or controversies

Return JSON with: summary, key_insights (array of strings), suggested_angles (array of strings)"""

    analysis = await call_llm_json(
        prompt=analysis_prompt,
        system_prompt="You are a content research analyst. Extract actionable insights from search results. Return ONLY valid JSON.",
        temperature=0.3,
        max_tokens=1000,
    )

    if not analysis or not isinstance(analysis, dict):
        # Fallback: construct insights from raw results
        analysis = {
            "summary": web_results[0]["snippet"] if web_results else "",
            "key_insights": [r["snippet"][:100] for r in web_results[:3]],
            "suggested_angles": [f"Write about: {r['title'][:60]}" for r in web_results[:2]],
        }

    return {
        "web_results": web_results,
        "summary": analysis.get("summary", ""),
        "key_insights": analysis.get("key_insights", []),
        "suggested_angles": analysis.get("suggested_angles", []),
        "source_urls": [r["url"] for r in web_results if r.get("url")],
    }


def _build_search_query(topic: str, platform: str, aspect: str) -> str:
    """Build a search query based on the research aspect."""
    platform_names = {
        "linkedin": "LinkedIn",
        "x": "Twitter X",
        "instagram": "Instagram",
        "facebook": "Facebook",
        "youtube": "YouTube",
    }
    platform_name = platform_names.get(platform, platform)

    if aspect == "trends":
        return f"{topic} trends {platform_name} 2026"
    elif aspect == "competitors":
        return f"{topic} top {platform_name} posts strategies"
    elif aspect == "hooks":
        return f"{topic} viral hooks {platform_name} engagement"
    else:
        return f"{topic} {platform_name} content ideas strategies"
