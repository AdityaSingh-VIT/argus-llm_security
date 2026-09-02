"""
database/connection.py — Async SQLAlchemy engine and session factory.

Default:     SQLite (aiosqlite) — zero-config local dev.
Production:  PostgreSQL (asyncpg) — set DATABASE_URL in env.
"""

import os
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./argus.db",
)

engine = create_async_engine(DATABASE_URL, echo=False, future=True)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def init_db() -> None:
    """Create all ORM tables on startup (idempotent)."""
    from models import db_models  # noqa: F401 — imported for side-effect
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """FastAPI dependency: yields an async DB session, always closed after use."""
    async with AsyncSessionLocal() as session:
        yield session
