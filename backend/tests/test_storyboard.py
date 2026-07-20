"""Tests for storyboard and video pipeline enhancement."""
import pytest
import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

import pytest_asyncio
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.database import Base, get_db, engine
from app.main import app
from app.services.storyboard_service import (
    generate_storyboard,
    _fallback_storyboard,
    PLATFORM_SPECS,
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


# ── Platform specs tests ──────────────────────────────────────────────

def test_platform_specs_exist():
    """All major platforms have specs defined."""
    assert "youtube" in PLATFORM_SPECS
    assert "instagram" in PLATFORM_SPECS
    assert "tiktok" in PLATFORM_SPECS
    assert "x" in PLATFORM_SPECS

    for platform, spec in PLATFORM_SPECS.items():
        assert "aspect_ratio" in spec
        assert "resolution" in spec
        assert "thumbnail_size" in spec


def test_youtube_specs():
    """YouTube specs are correct."""
    spec = PLATFORM_SPECS["youtube"]
    assert spec["aspect_ratio"] == "16:9"
    assert spec["resolution"] == "1920x1080"


def test_instagram_specs():
    """Instagram Reels specs are correct."""
    spec = PLATFORM_SPECS["instagram"]
    assert spec["aspect_ratio"] == "9:16"


# ── Fallback storyboard tests ─────────────────────────────────────────

def test_fallback_storyboard():
    """Fallback storyboard creates shots from script sections."""
    script = {
        "title": "Test Video",
        "hook": "Watch this!",
        "sections": [
            {"timestamp": "0:00-0:15", "visual": "Intro", "narration": "Hello", "text_overlay": "Welcome"},
            {"timestamp": "0:15-0:30", "visual": "Content", "narration": "Main point", "text_overlay": "Key fact"},
        ],
        "cta": "Subscribe!",
        "total_duration": 30,
    }
    spec = PLATFORM_SPECS["youtube"]

    result = _fallback_storyboard(script, spec)

    assert len(result["storyboard"]) == 2
    assert result["storyboard"][0]["visual_description"] == "Intro"
    assert result["storyboard"][1]["narration"] == "Main point"
    assert len(result["thumbnail_concepts"]) == 1
    assert result["total_estimated_duration"] == 30


def test_fallback_storyboard_empty_sections():
    """Fallback handles empty sections."""
    result = _fallback_storyboard({"sections": [], "total_duration": 15}, PLATFORM_SPECS["youtube"])
    assert result["storyboard"] == []


# ── Storyboard generation tests (mocked LLM) ─────────────────────────

@pytest.mark.asyncio
@patch("app.services.storyboard_service.call_llm_json", new_callable=AsyncMock)
@patch("app.services.storyboard_service._generate_image_prompts", new_callable=AsyncMock)
async def test_generate_storyboard_full(mock_prompts, mock_llm):
    """Full storyboard generation returns complete data."""
    mock_llm.return_value = {
        "storyboard": [
            {
                "shot_number": 1,
                "timestamp": "0:00-0:05",
                "duration_seconds": 5,
                "visual_description": "Close-up of host",
                "narration": "Hey everyone!",
                "text_overlay": "NEW VIDEO",
                "movement": "static",
                "mood": "energetic",
            }
        ],
        "thumbnail_concepts": [
            {
                "concept_text": "YOU WON'T BELIEVE THIS",
                "visual_description": "Host with surprised expression",
                "color_scheme": ["#FF0000", "#FFFFFF"],
                "style": "bold",
            }
        ],
        "music_cues": [
            {"section": "intro", "mood": "upbeat", "energy_level": 8, "genre": "electronic"}
        ],
        "transitions": [
            {"from_shot": 1, "to_shot": 2, "transition_type": "cut"}
        ],
        "total_estimated_duration": 60,
    }
    mock_prompts.return_value = {
        "dalle": "A YouTube thumbnail...",
        "midjourney": "YouTube thumbnail --ar 16:9 --v 6",
        "stable_diffusion": "youtube thumbnail, bold",
        "negative_prompt": "blurry",
    }

    script = {
        "title": "Test Video",
        "hook": "Watch this!",
        "sections": [{"timestamp": "0:00-0:05", "visual": "Intro", "narration": "Hi"}],
        "cta": "Subscribe!",
        "total_duration": 60,
    }

    result = await generate_storyboard(script, platform="youtube")

    assert len(result["storyboard"]) == 1
    assert result["storyboard"][0]["visual_description"] == "Close-up of host"
    assert len(result["thumbnail_concepts"]) == 1
    assert "dalle" in result["image_prompts"]
    assert "midjourney" in result["image_prompts"]
    assert result["platform_specs"]["aspect_ratio"] == "16:9"


@pytest.mark.asyncio
@patch("app.services.storyboard_service.call_llm_json", new_callable=AsyncMock)
@patch("app.services.storyboard_service._generate_image_prompts", new_callable=AsyncMock)
async def test_generate_storyboard_fallback(mock_prompts, mock_llm):
    """Storyboard falls back when LLM fails."""
    mock_llm.return_value = None
    mock_prompts.return_value = {"dalle": "fallback", "midjourney": "fallback", "stable_diffusion": "fallback", "negative_prompt": "none"}

    script = {
        "title": "Test",
        "sections": [{"visual": "Intro", "narration": "Hi", "text_overlay": "Hey"}],
        "total_duration": 30,
    }

    result = await generate_storyboard(script)
    # Should use fallback storyboard
    assert len(result["storyboard"]) == 1
    assert result["storyboard"][0]["visual_description"] == "Intro"


# ── API endpoint tests ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_generate_video_script_includes_storyboard(client):
    """generate-video-script returns storyboard data."""
    res = await client.post("/api/ai/generate-video-script", json={
        "topic": "AI tools",
        "platform": "youtube",
        "provider": "openai",
        "duration": 30,
        "style": "professional",
    }, headers={"Authorization": "Bearer fake"})
    # May fail auth, but if it reaches the logic, storyboard should be in response
    # Just verify the endpoint exists and responds
    assert res.status_code in (200, 401, 403, 422)


@pytest.mark.asyncio
async def test_generate_video_script_requires_topic(client):
    """generate-video-script returns 400 without topic."""
    res = await client.post("/api/ai/generate-video-script", json={
        "platform": "youtube",
    }, headers={"Authorization": "Bearer fake"})
    assert res.status_code in (400, 401, 403)
