"""Tests for billing endpoints."""
import pytest


@pytest.mark.asyncio
async def test_get_plans(client):
    res = await client.get("/api/billing/plans")
    assert res.status_code == 200
    data = res.json()
    assert "plans" in data
    assert len(data["plans"]) == 4
    plan_ids = [p["id"] for p in data["plans"]]
    assert "free" in plan_ids
    assert "pro" in plan_ids
    assert "business" in plan_ids
    assert "enterprise" in plan_ids


@pytest.mark.asyncio
async def test_get_subscription(client, auth_headers):
    res = await client.get("/api/billing/subscription", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "plan" in data
    assert "status" in data


@pytest.mark.asyncio
async def test_get_usage(client, auth_headers):
    res = await client.get("/api/billing/usage", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "credits" in data


@pytest.mark.asyncio
async def test_get_invoices(client, auth_headers):
    res = await client.get("/api/billing/invoices", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "invoices" in data
