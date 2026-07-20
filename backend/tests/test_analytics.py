"""Tests for analytics endpoints."""
import pytest


@pytest.mark.asyncio
async def test_analytics_dashboard(client, auth_headers):
    res = await client.get("/api/analytics/dashboard?period=30d", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "summary" in data
    assert "reachTrend" in data


@pytest.mark.asyncio
async def test_analytics_platform_comparison(client, auth_headers):
    res = await client.get("/api/analytics/platform-comparison", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "platforms" in data
    # platforms may be empty when no posts exist


@pytest.mark.asyncio
async def test_analytics_top_posts(client, auth_headers):
    res = await client.get("/api/analytics/top-posts", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "posts" in data


@pytest.mark.asyncio
async def test_analytics_best_times(client, auth_headers):
    res = await client.get("/api/analytics/best-times", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "bestTimes" in data
    assert "heatmap" in data
