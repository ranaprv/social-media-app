"""Tests for the prompt evolution (self-improving prompts) system."""
import pytest
import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.database import Base, get_db, engine
from app.main import app
from app.services.prompt_evolution import (
    seed_prompt_versions,
    get_best_prompt,
    log_prompt_usage,
    update_prompt_performance,
    create_prompt_version,
    get_prompt_analytics,
)
from app.models.prompt_versions import PromptVersion, PromptUsageLog


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


# ── Seed tests ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_seed_prompt_versions():
    """Seeding creates prompt versions for all content types."""
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as db:
        created = await seed_prompt_versions(db)
        assert created > 0

        # Verify they exist
        from sqlalchemy import select, func
        result = await db.execute(select(func.count(PromptVersion.id)))
        count = result.scalar()
        assert count == created


@pytest.mark.asyncio
async def test_seed_is_idempotent():
    """Seeding twice doesn't create duplicates."""
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as db:
        created1 = await seed_prompt_versions(db)
        created2 = await seed_prompt_versions(db)
        assert created2 == 0  # Second seed creates nothing


# ── Get best prompt tests ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_best_prompt_returns_active():
    """get_best_prompt returns the active prompt for content_type + platform."""
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as db:
        await seed_prompt_versions(db)

        pv = await get_best_prompt(db, "linkedin_post", "linkedin")
        assert pv is not None
        assert pv.content_type == "linkedin_post"
        assert pv.platform == "linkedin"
        assert pv.is_active is True


@pytest.mark.asyncio
async def test_get_best_prompt_returns_none_when_no_match():
    """get_best_prompt returns None when no prompt exists for the combination."""
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as db:
        pv = await get_best_prompt(db, "nonexistent_type", "nonexistent_platform")
        assert pv is None


@pytest.mark.asyncio
async def test_get_best_prompt_ranks_by_performance():
    """get_best_prompt picks the higher-scoring prompt."""
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as db:
        # Create two versions — one with higher score
        low = PromptVersion(
            id="low-score", content_type="reel", platform="instagram",
            version=1, system_prompt="low", user_prompt_template="low",
            is_active=True, performance_score=30.0, usage_count=10,
        )
        high = PromptVersion(
            id="high-score", content_type="reel", platform="instagram",
            version=2, system_prompt="high", user_prompt_template="high",
            is_active=True, performance_score=85.0, usage_count=5,
        )
        db.add_all([low, high])
        await db.flush()

        best = await get_best_prompt(db, "reel", "instagram")
        assert best.id == "high-score"


# ── Log usage tests ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_log_prompt_usage_increments_count():
    """Logging usage increments the prompt version's usage_count."""
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as db:
        await seed_prompt_versions(db)
        pv = await get_best_prompt(db, "linkedin_post", "linkedin")
        initial_count = pv.usage_count or 0

        await log_prompt_usage(
            db=db,
            prompt_version_id=pv.id,
            workspace_id="ws-test",
            topic="test topic",
            provider="openai",
            model="gpt-4o",
        )

        # Refresh
        from sqlalchemy import select
        result = await db.execute(select(PromptVersion).where(PromptVersion.id == pv.id))
        updated = result.scalar_one()
        assert updated.usage_count == initial_count + 1


@pytest.mark.asyncio
async def test_log_prompt_usage_creates_log_entry():
    """Logging usage creates a PromptUsageLog entry."""
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as db:
        await seed_prompt_versions(db)
        pv = await get_best_prompt(db, "reel", "instagram")

        log = await log_prompt_usage(
            db=db,
            prompt_version_id=pv.id,
            workspace_id="ws-test",
            topic="reel topic",
        )

        assert log.id is not None
        assert log.prompt_version_id == pv.id
        assert log.workspace_id == "ws-test"


# ── Performance update tests ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_prompt_performance():
    """Updating performance recalculates the prompt's rolling score."""
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as db:
        await seed_prompt_versions(db)
        pv = await get_best_prompt(db, "linkedin_post", "linkedin")

        # Log some usage
        await log_prompt_usage(db=db, prompt_version_id=pv.id, workspace_id="ws", post_id="post-1")
        await log_prompt_usage(db=db, prompt_version_id=pv.id, workspace_id="ws", post_id="post-2")

        # Update performance for post-1
        updated = await update_prompt_performance(db, "post-1", engagement_rate=5.0)
        assert updated == 1

        # Verify score was updated
        from sqlalchemy import select
        result = await db.execute(select(PromptVersion).where(PromptVersion.id == pv.id))
        updated_pv = result.scalar_one()
        assert updated_pv.performance_score > 0


@pytest.mark.asyncio
async def test_update_prompt_performance_noop_for_unknown_post():
    """Updating performance for unknown post returns 0."""
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as db:
        updated = await update_prompt_performance(db, "nonexistent-post", 5.0)
        assert updated == 0


# ── Create prompt version tests ───────────────────────────────────────

@pytest.mark.asyncio
async def test_create_prompt_version():
    """Creating a new version deactivates the old one."""
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as db:
        await seed_prompt_versions(db)

        new_pv = await create_prompt_version(
            db=db,
            content_type="linkedin_post",
            platform="linkedin",
            system_prompt="New system prompt",
            user_prompt_template="New user prompt: {topic}",
            created_by="test-user",
            notes="Testing version creation",
        )

        assert new_pv.version == 2  # seed was v1
        assert new_pv.is_active is True
        assert new_pv.system_prompt == "New system prompt"

        # Old version should be deactivated
        from sqlalchemy import select
        old = await db.execute(
            select(PromptVersion).where(
                PromptVersion.content_type == "linkedin_post",
                PromptVersion.platform == "linkedin",
                PromptVersion.version == 1,
            )
        )
        old_pv = old.scalar_one()
        assert old_pv.is_active is False


# ── Analytics tests ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_prompt_analytics():
    """Analytics endpoint returns prompt performance data."""
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as db:
        await seed_prompt_versions(db)
        analytics = await get_prompt_analytics(db)

        assert "prompts" in analytics
        assert "summary" in analytics
        assert analytics["summary"]["total_versions"] > 0


# ── API endpoint tests ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_generate_content_uses_best_prompt(client):
    """generate-content endpoint uses the best prompt from DB."""
    res = await client.post("/api/ai/generate-content", json={
        "content_type": "linkedin_post",
        "topic": "AI in 2026",
        "platform": "linkedin",
        "provider": "openai",
    })
    assert res.status_code == 200
    data = res.json()
    assert "content" in data
    assert "prompt_version_id" in data
    assert data["content_type"] == "linkedin_post"


@pytest.mark.asyncio
async def test_generate_content_requires_topic(client):
    """generate-content returns 400 when topic is missing."""
    res = await client.post("/api/ai/generate-content", json={
        "content_type": "linkedin_post",
    })
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_prompt_analytics_endpoint(client):
    """prompt-analytics endpoint returns data."""
    res = await client.get("/api/ai/prompt-analytics")
    assert res.status_code == 200
    data = res.json()
    assert "prompts" in data
    assert "summary" in data


@pytest.mark.asyncio
async def test_create_prompt_version_endpoint(client):
    """Creating a prompt version via API works."""
    # Need auth — use a registered user
    await client.post("/api/auth/register", json={
        "email": "prompt-test@example.com",
        "password": "test123",
        "name": "Prompt Tester",
    })
    login_res = await client.post("/api/auth/login", json={
        "email": "prompt-test@example.com",
        "password": "test123",
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = await client.post("/api/ai/prompt-versions", json={
        "content_type": "reel",
        "platform": "instagram",
        "system_prompt": "Custom reel prompt",
        "user_prompt_template": "Write a reel about {topic}",
        "notes": "Testing API creation",
    }, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["content_type"] == "reel"
    assert data["is_active"] is True
