"""Tests for content pattern learning."""
import pytest
import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

import pytest_asyncio
from datetime import datetime, timedelta
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.database import Base, get_db, engine
from app.main import app
from app.services.content_pattern_learner import (
    extract_winning_patterns,
    _extract_hook_patterns,
    _extract_cta_patterns,
    _extract_content_structures,
    _extract_avoid_patterns,
    _build_learning_context,
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


async def _seed_posts_with_analytics(db, workspace_id="ws-1", count=10):
    """Seed posts with analytics data for pattern analysis."""
    from app.models.content import Post, AnalyticsMetric
    import uuid

    now = datetime.utcnow()
    for i in range(count):
        post_id = f"post-{i}"
        eng_rate = 2.0 + (i * 1.5)  # Increasing engagement
        impressions = 1000 + (i * 200)

        post = Post(
            id=post_id,
            workspace_id=workspace_id,
            author_id="user-1",
            title=f"Post {i}",
            content=f"Hook line for post {i}!\n\nHere is the body content with valuable insights.\n\nComment below what you think!",
            platform="linkedin",
            status="published",
            published_at=now - timedelta(days=i),
            media_urls=["img.jpg"] if i % 2 == 0 else [],
        )
        db.add(post)

        metric = AnalyticsMetric(
            id=str(uuid.uuid4()),
            post_id=post_id,
            platform="linkedin",
            impressions=impressions,
            engagement=int(impressions * eng_rate / 100),
            likes=int(impressions * eng_rate / 200),
            comments=i * 3,
            shares=i * 2,
            clicks=i,
        )
        db.add(metric)

    await db.flush()


# ── Unit tests for pattern extraction ─────────────────────────────────

def test_hook_patterns_extraction():
    """Hook pattern extraction classifies hooks correctly."""
    posts = [
        {"content": "Stop scrolling! Here's the truth about AI...", "eng_rate": 8.0, "platform": "linkedin"},
        {"content": "Here is some content about stuff.", "eng_rate": 2.0, "platform": "linkedin"},
        {"content": "Why most marketers get it wrong", "eng_rate": 7.0, "platform": "linkedin"},
        {"content": "3 lessons from scaling to $1M ARR", "eng_rate": 9.0, "platform": "linkedin"},
    ]
    patterns = _extract_hook_patterns(posts)
    assert len(patterns) > 0
    # Should have different hook types
    types = [p["type"] for p in patterns]
    assert "contrarian" in types or "question" in types or "number" in types


def test_cta_patterns_extraction():
    """CTA pattern extraction finds CTAs in content."""
    posts = [
        {"content": "Great post! What do you think? Drop a comment below.", "eng_rate": 8.0, "platform": "linkedin"},
        {"content": "Save this for later!", "eng_rate": 6.0, "platform": "linkedin"},
        {"content": "No CTA here.", "eng_rate": 2.0, "platform": "linkedin"},
    ]
    patterns = _extract_cta_patterns(posts)
    assert len(patterns) >= 2
    cta_types = [p["cta_type"] for p in patterns]
    assert "what do you think" in cta_types or "drop" in cta_types or "save" in cta_types


def test_content_structures_extraction():
    """Content structure extraction returns valid structure data."""
    posts = [
        {"content": "Line 1\nLine 2\nLine 3\n\nMore content here.", "eng_rate": 8.0},
        {"content": "Short post.", "eng_rate": 5.0},
    ]
    structures = _extract_content_structures(posts)
    assert len(structures) == 1
    assert "avg_word_count" in structures[0]
    assert "emoji_usage_pct" in structures[0]


def test_avoid_patterns_extraction():
    """Avoid pattern extraction finds anti-patterns."""
    bottom = [
        {"content": "This is the most amazing incredible best post ever!", "eng_rate": 1.0},
        {"content": "Another amazing post with no CTA", "eng_rate": 0.5},
    ]
    top = [
        {"content": "Real insights about AI with a question at the end?", "eng_rate": 8.0},
    ]
    avoid = _extract_avoid_patterns(bottom, top)
    assert len(avoid) > 0


def test_build_learning_context():
    """Learning context generation produces readable output."""
    context = _build_learning_context(
        hook_patterns=[{"type": "question", "text": "Why does this work?", "eng_rate": 8.0, "platform": "linkedin"}],
        cta_patterns=[{"text": "What do you think?", "cta_type": "what do you think", "eng_rate": 7.0}],
        content_structures=[{"avg_word_count": 150, "emoji_usage_pct": 60, "list_usage_pct": 40, "line_break_usage_pct": 90}],
        avoid_patterns=["Generic buzzwords"],
        length_insights={"optimal_range": "medium (50-200)"},
        media_insights={"media_boost_pct": 25},
        timing_insights={"best_hour": 9},
        top_count=5,
        total_count=25,
    )
    assert "TOP-PERFORMING" in context
    assert "HOOK" in context
    assert "AVOID" in context
    assert len(context) > 100


# ── Integration tests ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_extract_winning_patterns_with_data():
    """Pattern extraction works with seeded data."""
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as db:
        await _seed_posts_with_analytics(db, count=10)
        patterns = await extract_winning_patterns(db, "ws-1")

        assert patterns["stats"]["total_posts"] == 10
        assert patterns["stats"]["analyzed_top"] > 0
        assert isinstance(patterns["learning_context"], str)


@pytest.mark.asyncio
async def test_extract_winning_patterns_insufficient_data():
    """Pattern extraction returns empty when not enough posts."""
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as db:
        patterns = await extract_winning_patterns(db, "ws-nonexistent")

        assert patterns["stats"]["total_posts"] == 0
        assert patterns["learning_context"] == ""


@pytest.mark.asyncio
async def test_content_patterns_endpoint(client):
    """content-patterns endpoint works."""
    res = await client.get("/api/ai/content-patterns?workspace_id=default")
    assert res.status_code == 200
    data = res.json()
    assert "hook_patterns" in data
    assert "learning_context" in data
    assert "stats" in data


@pytest.mark.asyncio
async def test_generate_content_injects_patterns(client):
    """generate-content endpoint injects learning context when workspace_id provided."""
    res = await client.post("/api/ai/generate-content", json={
        "content_type": "linkedin_post",
        "topic": "Test with patterns",
        "platform": "linkedin",
        "provider": "openai",
        "workspace_id": "ws-1",
    })
    assert res.status_code == 200
    data = res.json()
    assert "content" in data
