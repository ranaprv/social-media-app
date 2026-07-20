"""Tests for multi-variant content generation."""
import pytest
import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

import pytest_asyncio
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.database import Base, get_db, engine
from app.main import app
from app.services.multi_variant_generator import generate_variants
from app.services.content_quality_rubric import score_content_rubric
from app.services.viral_score import predict_viral_score


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


# ── Scoring tests (existing functions now wired in) ───────────────────

def test_rubric_scoring_works():
    """score_content_rubric returns valid scores."""
    result = score_content_rubric(
        content="Hey everyone! ?\n\nHere's something I learned about AI:\n\n1. It's evolving fast\n2. You need to stay updated\n3. The best time to start is now\n\nWhat do you think? Drop a comment below!",
        platform="linkedin",
        media_count=2,
        has_cta=True,
    )
    assert 0 <= result["overall_score"] <= 100
    assert result["rating"] in ("excellent", "good", "fair", "needs_work")
    assert len(result["dimensions"]) == 10


def test_viral_scoring_works():
    """predict_viral_score returns valid scores."""
    result = predict_viral_score(
        content="Stop scrolling! Here's the secret to going viral on LinkedIn that nobody tells you...",
        platform="linkedin",
        media_count=1,
    )
    assert 0 <= result["score"] <= 100
    assert len(result["factors"]) > 0


def test_rubric_penalizes_over_limit():
    """Rubric penalizes content exceeding platform limits."""
    short = score_content_rubric("Hi!", "x")
    long = score_content_rubric("x" * 5000, "x")
    assert short["dimensions"]["compliance"]["score"] >= long["dimensions"]["compliance"]["score"]


def test_viral_rewards_hooks():
    """Viral score rewards strong hooks."""
    weak = predict_viral_score("Here is some content about stuff.", "linkedin")
    strong = predict_viral_score("Stop scrolling! The secret to success nobody tells you...", "linkedin")
    assert strong["score"] >= weak["score"]


# ── Multi-variant generation tests ────────────────────────────────────

@pytest.mark.asyncio
@patch("app.services.multi_variant_generator.call_llm", new_callable=AsyncMock)
async def test_generate_variants_returns_ranked(mock_llm):
    """generate_variants returns variants ranked by combined score."""
    # Mock LLM to return different content for each variant
    mock_llm.side_effect = [
        "Great post about AI! Here are 3 tips to get started.",
        "Everyone talks about AI but nobody mentions the real cost. Let me break it down.",
        "I spent 6 months building with AI. Here's what nobody tells you about the journey.",
    ]

    result = await generate_variants(
        system_prompt="You are a social media writer.",
        user_prompt="Write about AI",
        platform="linkedin",
        variant_count=3,
    )

    assert len(result["variants"]) == 3
    assert result["best_index"] == 0
    assert result["best_content"] != ""
    assert result["scores_summary"]["total_scored"] == 3
    # Variants should be sorted by combined_score descending
    scores = [v["combined_score"] for v in result["variants"]]
    assert scores == sorted(scores, reverse=True)


@pytest.mark.asyncio
@patch("app.services.multi_variant_generator.call_llm", new_callable=AsyncMock)
async def test_generate_variants_handles_failure(mock_llm):
    """generate_variants handles LLM failures gracefully."""
    mock_llm.side_effect = [
        "Good content here.",
        Exception("API error"),
        "More content here.",
    ]

    result = await generate_variants(
        system_prompt="Write content",
        user_prompt="About AI",
        platform="linkedin",
        variant_count=3,
    )

    # Should have 2 variants (one failed)
    assert len(result["variants"]) == 2
    assert result["scores_summary"]["total_generated"] == 3
    assert result["scores_summary"]["total_scored"] == 2


@pytest.mark.asyncio
@patch("app.services.multi_variant_generator.call_llm", new_callable=AsyncMock)
async def test_generate_variants_clamps_count(mock_llm):
    """generate_variants clamps variant_count to 1-5."""
    mock_llm.return_value = "Content"

    result = await generate_variants(
        system_prompt="Write",
        user_prompt="About topic",
        platform="linkedin",
        variant_count=10,  # should clamp to 5
    )

    assert len(result["variants"]) <= 5


@pytest.mark.asyncio
@patch("app.services.multi_variant_generator.call_llm", new_callable=AsyncMock)
async def test_generate_variants_single(mock_llm):
    """generate_variants works with variant_count=1."""
    mock_llm.return_value = "Single variant content."

    result = await generate_variants(
        system_prompt="Write",
        user_prompt="About topic",
        platform="linkedin",
        variant_count=1,
    )

    assert len(result["variants"]) == 1
    assert result["best_index"] == 0


# ── API endpoint tests ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_generate_content_variants_endpoint(client):
    """generate-content-variants endpoint works."""
    res = await client.post("/api/ai/generate-content-variants", json={
        "content_type": "linkedin_post",
        "topic": "AI trends in 2026",
        "platform": "linkedin",
        "provider": "openai",
        "variant_count": 2,
    })
    assert res.status_code == 200
    data = res.json()
    assert "variants" in data
    assert "best_index" in data
    assert "best_content" in data
    assert "scores_summary" in data
    assert "hashtags" in data
    assert data["content_type"] == "linkedin_post"


@pytest.mark.asyncio
async def test_generate_content_variants_requires_topic(client):
    """generate-content-variants returns 400 without topic."""
    res = await client.post("/api/ai/generate-content-variants", json={
        "content_type": "linkedin_post",
    })
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_generate_content_still_works(client):
    """Original generate-content endpoint still works (backward compatible)."""
    res = await client.post("/api/ai/generate-content", json={
        "content_type": "linkedin_post",
        "topic": "Test topic",
        "platform": "linkedin",
        "provider": "openai",
    })
    assert res.status_code == 200
    data = res.json()
    assert "content" in data
    assert "prompt_version_id" in data
