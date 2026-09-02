"""
database/crud.py — Database create/read/update helpers.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from models.db_models import User, ScanJob, AttackResult, Report


# ── Users ─────────────────────────────────────────────────────────────────────

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    username: str,
    email: str,
    hashed_password: str,
) -> User:
    user = User(
        id=str(uuid.uuid4()),
        username=username,
        email=email,
        hashed_password=hashed_password,
        created_at=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# ── Scan Jobs ─────────────────────────────────────────────────────────────────

async def create_scan(
    db: AsyncSession,
    target_url: str,
    project_name: str,
    user_id: str,
) -> ScanJob:
    scan = ScanJob(
        id=str(uuid.uuid4()),
        user_id=user_id,
        project_name=project_name,
        target_url=target_url,
        status="pending",
        started_at=datetime.now(timezone.utc),
    )
    db.add(scan)
    await db.commit()
    await db.refresh(scan)
    return scan


async def update_scan_status(
    db: AsyncSession,
    scan_id: str,
    status: str,
) -> Optional[ScanJob]:
    result = await db.execute(select(ScanJob).where(ScanJob.id == scan_id))
    scan = result.scalar_one_or_none()
    if scan:
        scan.status = status
        if status in ("completed", "failed"):
            scan.finished_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(scan)
    return scan


async def get_scans(
    db: AsyncSession,
    user_id: str,
    limit: int = 20,
) -> List[ScanJob]:
    result = await db.execute(
        select(ScanJob)
        .where(ScanJob.user_id == user_id)
        .order_by(desc(ScanJob.started_at))
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_scan_by_id(db: AsyncSession, scan_id: str) -> Optional[ScanJob]:
    result = await db.execute(select(ScanJob).where(ScanJob.id == scan_id))
    return result.scalar_one_or_none()


# ── Attack Results ────────────────────────────────────────────────────────────

async def log_attack(
    db: AsyncSession,
    scan_id: str,
    prompt: str,
    response: str,
    score: float,
    category: str,
) -> AttackResult:
    attack = AttackResult(
        id=str(uuid.uuid4()),
        scan_id=scan_id,
        prompt=prompt,
        response=response,
        score=score,
        category=category,
        timestamp=datetime.now(timezone.utc),
    )
    db.add(attack)
    await db.commit()
    await db.refresh(attack)
    return attack


async def get_attacks_by_scan(
    db: AsyncSession,
    scan_id: str,
) -> List[AttackResult]:
    result = await db.execute(
        select(AttackResult)
        .where(AttackResult.scan_id == scan_id)
        .order_by(desc(AttackResult.timestamp))
    )
    return list(result.scalars().all())


async def get_recent_attacks(
    db: AsyncSession,
    user_id: str,
    limit: int = 50,
) -> List[AttackResult]:
    """All attacks across all scans belonging to user_id, newest first."""
    result = await db.execute(
        select(AttackResult)
        .join(ScanJob, AttackResult.scan_id == ScanJob.id)
        .where(ScanJob.user_id == user_id)
        .order_by(desc(AttackResult.timestamp))
        .limit(limit)
    )
    return list(result.scalars().all())


# ── Reports ───────────────────────────────────────────────────────────────────

async def save_report(
    db: AsyncSession,
    scan_id: str,
    file_path: str,
) -> Report:
    rpt = Report(
        id=str(uuid.uuid4()),
        scan_id=scan_id,
        file_path=file_path,
        created_at=datetime.now(timezone.utc),
    )
    db.add(rpt)
    await db.commit()
    await db.refresh(rpt)
    return rpt


async def get_report_by_scan(db: AsyncSession, scan_id: str) -> Optional[Report]:
    result = await db.execute(select(Report).where(Report.scan_id == scan_id))
    return result.scalar_one_or_none()
