"""tests/test_scan.py — Scan endpoint tests."""

import pytest
from unittest.mock import AsyncMock, patch


async def _get_token(client) -> str:
    r = await client.post("/auth/register", json={"username": "scanuser", "password": "pw"})
    return r.json()["access_token"]


@pytest.mark.asyncio
async def test_trigger_scan_returns_202(client):
    token = await _get_token(client)
    r = await client.post(
        "/scan",
        json={"target_url": "http://example.com/chat", "project_name": "Test", "num_attacks": 2},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 202
    data = r.json()
    assert data["status"] == "pending"
    assert data["target_url"] == "http://example.com/chat"


@pytest.mark.asyncio
async def test_get_scan_status(client):
    token = await _get_token(client)
    create_r = await client.post(
        "/scan",
        json={"target_url": "http://example.com/chat", "project_name": "Test2", "num_attacks": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    scan_id = create_r.json()["id"]
    r = await client.get(f"/scan/{scan_id}", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["id"] == scan_id


@pytest.mark.asyncio
async def test_scan_not_found(client):
    token = await _get_token(client)
    r = await client.get("/scan/nonexistent-id", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 404
