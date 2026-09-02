"""
tests/conftest.py — Shared fixtures for pytest.

Uses an in-memory SQLite database so tests never touch the real DB.
"""

import os
import pytest
import pytest_asyncio

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("DIGITAL_TWIN_URL", "http://localhost:7001")
os.environ.setdefault("ATTACK_ENGINE_URL", "http://localhost:7002")

from httpx import AsyncClient, ASGITransport
from main import app
from database.connection import init_db


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    await init_db()


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
