"""tests/test_auth.py — Auth endpoint tests."""

import pytest


@pytest.mark.asyncio
async def test_register_and_login(client):
    # Register
    r = await client.post("/auth/register", json={"username": "testuser", "password": "testpass"})
    assert r.status_code == 201
    token = r.json()["access_token"]
    assert token

    # Login with same credentials
    r2 = await client.post("/auth/login", json={"username": "testuser", "password": "testpass"})
    assert r2.status_code == 200
    assert r2.json()["access_token"]


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post("/auth/register", json={"username": "user2", "password": "correct"})
    r = await client.post("/auth/login", json={"username": "user2", "password": "wrong"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_without_token(client):
    r = await client.get("/dashboard")
    assert r.status_code == 401
