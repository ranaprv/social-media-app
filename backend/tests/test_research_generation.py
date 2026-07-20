"""Tests for research-backed content generation."""
import pytest
import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

import pytest_asyncio
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.database import Base, get_db, engine
from app.main import app
from app.services.web_search import (
    web_search,
    research_topic,
    _parse_html_results,
    _build_search_query,
)


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# ── HTML parsing tests ────────────────────────────────────────────────

def test_parse_html_results_basic():
    """HTML parser extracts titles, snippets, and URLs."""
    html = '''
    <a class="result__a" href="https://example.com?uddg=https://real-url.com">Test Title</a>
    <a class="result__snippet">This is a test snippet about the topic.</a>
    '''
    results = _parse_html_results(html, 5)
    assert len(results) == 1
    assert results[0]["title"] == "Test Title"
    assert "test snippet" in results[0]["snippet"]
    assert "real-url.com" in results[0]["url"]


def test_parse_html_results_empty():
    """HTML parser returns empty for no results."""
    results = _parse_html_results("<html><body>No results</body></html>", 5)
    assert results == []


def test_parse_html_results_multiple():
    """HTML parser handles multiple results."""
    html = '''
    <a class="result__a" href="https://a.com">Title A</a>
    <a class="result__snippet">Snippet A</a>
    <a class="result__a" href="https://b.com">Title B</a>
    <a class="result__snippet">Snippet B</a>
    '''
    results = _parse_html_results(html, 5)
    assert len(results) == 2


def test_parse_html_results_strips_tags():
    """HTML parser strips HTML tags from results."""
    html = '''
    <a class="result__a" href="https://x.com"><b>Bold Title</b></a>
    <a class="result__snippet"><i>Italic snippet</i></a>
    '''
    results = _parse_html_results(html, 5)
    assert len(results) == 1
    assert "<b>" not in results[0]["title"]
    assert "<i>" not in results[0]["snippet"]


# ── Search query building tests ───────────────────────────────────────

def test_build_search_query_general():
    """General query includes topic and platform."""
    query = _build_search_query("AI marketing", "linkedin", "general")
    assert "AI marketing" in query
    assert "LinkedIn" in query


def test_build_search_query_trends():
    """Trends query includes year."""
    query = _build_search_query("AI", "youtube", "trends")
    assert "trends" in query
    assert "2026" in query


def test_build_search_query_hooks():
    """Hooks query includes engagement term."""
    query = _build_search_query("productivity", "x", "hooks")
    assert "hooks" in query
    assert "engagement" in query


# ── Web search tests (mocked) ─────────────────────────────────────────

@pytest.mark.asyncio
@patch("app.services.web_search._search_duckduckgo", new_callable=AsyncMock)
async def test_web_search_returns_results(mock_search):
    """web_search returns parsed results."""
    mock_search.return_value = [
        {"title": "AI Trends", "snippet": "AI is growing fast", "url": "https://example.com"},
    ]

    results = await web_search("AI trends", max_results=3)
    assert len(results) == 1
    assert results[0]["title"] == "AI Trends"


@pytest.mark.asyncio
@patch("app.services.web_search._search_duckduckgo", new_callable=AsyncMock)
async def test_web_search_caches_results(mock_search):
    """web_search caches results for 5 minutes."""
    mock_search.return_value = [
        {"title": "Cached", "snippet": "Result", "url": "https://x.com"},
    ]

    # First call
    results1 = await web_search("cache test")
    assert mock_search.call_count == 1

    # Second call — should use cache
    results2 = await web_search("cache test")
    assert mock_search.call_count == 1  # Not called again
    assert results1 == results2


@pytest.mark.asyncio
@patch("app.services.web_search._search_duckduckgo", new_callable=AsyncMock)
async def test_web_search_handles_failure(mock_search):
    """web_search handles search failures gracefully."""
    mock_search.side_effect = Exception("Network error")

    results = await web_search("failing query")
    assert results == []


# ── Research topic tests ──────────────────────────────────────────────

@pytest.mark.asyncio
@patch("app.services.web_search.web_search", new_callable=AsyncMock)
@patch("app.services.llm.call_llm_json", new_callable=AsyncMock)
async def test_research_topic_with_results(mock_llm, mock_search):
    """research_topic combines web search + LLM analysis."""
    mock_search.return_value = [
        {"title": "AI Trends 2026", "snippet": "AI is transforming marketing", "url": "https://a.com"},
        {"title": "Content Strategy", "snippet": "Video content dominates", "url": "https://b.com"},
    ]
    mock_llm.return_value = {
        "summary": "AI is rapidly changing content creation.",
        "key_insights": ["AI tools save 50% time", "Video content gets 3x engagement"],
        "suggested_angles": ["How AI helps creators", "Video vs text performance"],
    }

    result = await research_topic("AI content creation", "linkedin")

    assert result["summary"] == "AI is rapidly changing content creation."
    assert len(result["key_insights"]) == 2
    assert len(result["suggested_angles"]) == 2
    assert len(result["source_urls"]) == 2


@pytest.mark.asyncio
@patch("app.services.web_search.web_search", new_callable=AsyncMock)
async def test_research_topic_no_results(mock_search):
    """research_topic handles no search results."""
    mock_search.return_value = []

    result = await research_topic("nonexistent topic xyz", "linkedin")

    assert result["web_results"] == []
    assert "No web results" in result["summary"]


# ── API endpoint tests ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_quick_research_endpoint(client):
    """quick-research endpoint works."""
    with patch("app.services.web_search.research_topic", new_callable=AsyncMock) as mock_research:
        mock_research.return_value = {
            "web_results": [],
            "summary": "Test summary",
            "key_insights": ["Insight 1"],
            "suggested_angles": ["Angle 1"],
            "source_urls": [],
        }

        res = await client.post("/api/ai/quick-research", json={
            "topic": "AI trends",
            "platform": "linkedin",
        })
        assert res.status_code == 200
        data = res.json()
        assert "summary" in data
        assert "key_insights" in data


@pytest.mark.asyncio
async def test_quick_research_requires_topic(client):
    """quick-research returns 400 without topic."""
    res = await client.post("/api/ai/quick-research", json={})
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_generate_content_still_works(client):
    """generate-content endpoint still works after research wiring."""
    res = await client.post("/api/ai/generate-content", json={
        "content_type": "linkedin_post",
        "topic": "Test",
        "platform": "linkedin",
        "provider": "openai",
    })
    assert res.status_code == 200
