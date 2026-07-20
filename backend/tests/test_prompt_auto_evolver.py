"""Tests for prompt auto-evolution."""
import pytest
import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

import pytest_asyncio
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.database import Base, get_db, engine
from app.main import app
from app.services.prompt_evolution import seed_prompt_versions, get_best_prompt, log_prompt_usage, update_prompt_performance
from app.services.prompt_auto_evolver import analyze_prompt_performance, suggest_prompt_improvements
from app.models.prompt_versions import PromptVersion


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


async def _setup_with_usage(db, content_type="linkedin_post", platform="linkedin", uses=5, scored=3):
    """Helper: seed prompts and add usage data."""
    await seed_prompt_versions(db)
    pv = await get_best_prompt(db, content_type, platform)

    for i in range(uses):
        log = await log_prompt_usage(
            db=db,
            prompt_version_id=pv.id,
            workspace_id="ws-test",
            topic=f"topic-{i}",
            provider="openai",
            model="gpt-4o",
            post_id=f"post-{i}" if i < scored else None,
        )

    # Score some of them
    for i in range(scored):
        await update_prompt_performance(db, f"post-{i}", engagement_rate=3.0 + i * 2)

    return pv


# ── Analysis tests ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_analyze_prompt_performance():
    """Analysis returns structured performance data."""
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as db:
        pv = await _setup_with_usage(db)
        analysis = await analyze_prompt_performance(db, "linkedin_post", "linkedin")

        assert "current_prompt" in analysis
        assert "performance" in analysis
        assert "usage_history" in analysis
        assert "version_history" in analysis
        assert analysis["performance"]["usage_count"] == 5
        assert analysis["performance"]["scored_uses"] == 3
        assert len(analysis["usage_history"]["high_performers"]) > 0


@pytest.mark.asyncio
async def test_analyze_prompt_performance_no_prompt():
    """Analysis returns error when no prompt exists."""
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as db:
        analysis = await analyze_prompt_performance(db, "nonexistent", "nonexistent")
        assert "error" in analysis


# ── Evolution guard tests ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_evolution_blocked_insufficient_uses():
    """Evolution is blocked when usage is below minimum."""
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as db:
        await seed_prompt_versions(db)
        pv = await get_best_prompt(db, "linkedin_post", "linkedin")

        # Only 1 use — below MIN_USES_FOR_EVOLUTION (3)
        await log_prompt_usage(db=db, prompt_version_id=pv.id, workspace_id="ws", topic="t")

        result = await suggest_prompt_improvements(db, "linkedin_post", "linkedin")
        assert result["auto_applied"] is False
        assert "reason" in result


@pytest.mark.asyncio
async def test_evolution_blocked_insufficient_scores():
    """Evolution is blocked when scored engagements are below minimum."""
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as db:
        await _setup_with_usage(db, uses=5, scored=1)  # only 1 scored

        result = await suggest_prompt_improvements(db, "linkedin_post", "linkedin")
        assert result["auto_applied"] is False


# ── Full evolution test ───────────────────────────────────────────────

@pytest.mark.asyncio
@patch("app.services.prompt_auto_evolver.call_llm_json", new_callable=AsyncMock)
async def test_suggest_prompt_improvements(mock_llm):
    """Full evolution flow creates a new prompt version."""
    mock_llm.return_value = {
        "system_prompt": "Improved system prompt with better role definition.",
        "user_prompt_template": "Write about {topic} for {platform} with {tone} tone.",
        "changes_made": [
            "Added specific role expertise",
            "Tightened output constraints",
        ],
        "confidence": 0.8,
        "reasoning": "The original prompt was too generic. Adding specific expertise and constraints should improve engagement.",
    }

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as db:
        pv = await _setup_with_usage(db, uses=5, scored=3)
        initial_version = pv.version

        result = await suggest_prompt_improvements(db, "linkedin_post", "linkedin")

        assert result["auto_applied"] is True
        assert result["new_version_id"] is not None
        assert result["new_version"] == initial_version + 1

        # Verify new version is active
        new_pv = await get_best_prompt(db, "linkedin_post", "linkedin")
        assert new_pv.id == result["new_version_id"]
        assert new_pv.version == initial_version + 1
        assert new_pv.created_by == "auto-evolver"


@pytest.mark.asyncio
@patch("app.services.prompt_auto_evolver.call_llm_json", new_callable=AsyncMock)
async def test_evolution_preserves_template_variables(mock_llm):
    """Evolution preserves required template variables."""
    mock_llm.return_value = {
        "system_prompt": "New prompt",
        "user_prompt_template": "Write about stuff",  # missing {topic}
        "changes_made": ["Simplified template"],
        "confidence": 0.7,
        "reasoning": "Simpler is better",
    }

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as db:
        pv = await _setup_with_usage(db, uses=5, scored=3)

        result = await suggest_prompt_improvements(db, "linkedin_post", "linkedin")

        # Should revert user_prompt_template because {topic} was missing
        assert result["auto_applied"] is True
        new_pv = await get_best_prompt(db, "linkedin_post", "linkedin")
        # The template should still have {topic} from the original
        assert "{topic}" in new_pv.user_prompt_template


@pytest.mark.asyncio
@patch("app.services.prompt_auto_evolver.call_llm_json", new_callable=AsyncMock)
async def test_evolution_handles_llm_failure(mock_llm):
    """Evolution handles LLM returning invalid response."""
    mock_llm.return_value = None

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as db:
        await _setup_with_usage(db, uses=5, scored=3)

        result = await suggest_prompt_improvements(db, "linkedin_post", "linkedin")
        assert result["auto_applied"] is False


# ── API endpoint tests ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_auto_evolve_endpoint(client):
    """auto-evolve endpoint works."""
    # Seed prompts first
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as db:
        await seed_prompt_versions(db)

    res = await client.post("/api/ai/prompt-auto-evolve", json={
        "content_type": "linkedin_post",
        "platform": "linkedin",
        "provider": "openai",
    })
    assert res.status_code == 200
    data = res.json()
    assert "auto_applied" in data


@pytest.mark.asyncio
async def test_auto_evolve_requires_params(client):
    """auto-evolve returns 400 without required params."""
    res = await client.post("/api/ai/prompt-auto-evolve", json={})
    assert res.status_code == 400
