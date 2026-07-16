"""Tests for security endpoints."""
import pytest


@pytest.mark.asyncio
async def test_get_audit_logs(client, auth_headers):
    res = await client.get("/api/security/audit-logs", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "logs" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_get_roles(client):
    res = await client.get("/api/security/roles")
    assert res.status_code == 200
    data = res.json()
    assert "roles" in data
    assert "owner" in data["roles"]
    assert "admin" in data["roles"]
    assert "editor" in data["roles"]
    assert "viewer" in data["roles"]


@pytest.mark.asyncio
async def test_rbac_check(client, auth_headers):
    res = await client.get("/api/security/rbac/check?permission=view_analytics", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "granted" in data


@pytest.mark.asyncio
async def test_rate_limit_status(client, auth_headers):
    res = await client.get("/api/security/rate-limit/status", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "remaining" in data
    assert "limit" in data


@pytest.mark.asyncio
async def test_oauth_connections(client, auth_headers):
    res = await client.get("/api/security/oauth/connections", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "connections" in data


@pytest.mark.asyncio
async def test_encryption_status(client):
    res = await client.get("/api/security/encryption/status")
    assert res.status_code == 200
    data = res.json()
    assert data["api_keys_encrypted"] is True


@pytest.mark.asyncio
async def test_gdpr_status(client, auth_headers):
    res = await client.get("/api/security/gdpr/status", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["data_processing_agreement"] is True
    assert data["right_to_erasure"] is True
