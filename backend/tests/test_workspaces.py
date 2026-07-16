"""Tests for workspace endpoints."""
import pytest


@pytest.mark.asyncio
async def test_create_workspace(client, auth_headers):
    res = await client.post("/api/workspaces/", json={
        "name": "Test Workspace",
        "slug": "test-workspace",
    }, headers=auth_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Test Workspace"
    assert data["slug"] == "test-workspace"


@pytest.mark.asyncio
async def test_list_workspaces(client, auth_headers):
    await client.post("/api/workspaces/", json={
        "name": "Workspace 1",
        "slug": "ws-1",
    }, headers=auth_headers)
    res = await client.get("/api/workspaces/", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_create_workspace_duplicate_slug(client, auth_headers):
    await client.post("/api/workspaces/", json={
        "name": "WS",
        "slug": "dup-slug",
    }, headers=auth_headers)
    res = await client.post("/api/workspaces/", json={
        "name": "WS2",
        "slug": "dup-slug",
    }, headers=auth_headers)
    assert res.status_code == 400
