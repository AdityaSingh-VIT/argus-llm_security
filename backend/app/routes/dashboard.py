"""
routes/dashboard.py — Dashboard endpoint.

GET /dashboard → aggregated stats for the frontend.
"""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from database.connection import get_db
from database import crud
from models.db_models import ScanJob, AttackResult
from models.schemas import DashboardStats, UserOut
from services import graph_engine

logger = logging.getLogger("argus.dashboard")
router = APIRouter()


@router.get(
    "",
    response_model=DashboardStats,
    summary="Aggregated dashboard statistics",
)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    """
    Returns:
      - Scan and attack counts
      - Risk level distribution (critical/high/medium/low)
      - Average risk score
      - 5 most recent scans
      - 10 most recent attacks
      - Graph node/edge summary from digital twin
      - Risk breakdown from digital twin
    """
    # ── Count scans ──────────────────────────────────────────────────────────
    total_scans_r = await db.execute(
        select(func.count()).select_from(ScanJob).where(ScanJob.user_id == current_user.id)
    )
    total_scans: int = total_scans_r.scalar() or 0

    # ── All attacks for this user ─────────────────────────────────────────────
    attacks_r = await db.execute(
        select(AttackResult)
        .join(ScanJob, AttackResult.scan_id == ScanJob.id)
        .where(ScanJob.user_id == current_user.id)
    )
    all_attacks = attacks_r.scalars().all()
    total_attacks = len(all_attacks)
    scores = [a.score for a in all_attacks]
    avg_risk_score = round(sum(scores) / len(scores), 1) if scores else 0.0

    critical_count = sum(1 for s in scores if s >= 80)
    high_count     = sum(1 for s in scores if 50 <= s < 80)
    medium_count   = sum(1 for s in scores if 25 <= s < 50)
    low_count      = sum(1 for s in scores if s < 25)

    recent_scans   = await crud.get_scans(db, current_user.id, limit=5)
    recent_attacks = await crud.get_recent_attacks(db, current_user.id, limit=10)

    # ── Graph engine stats (best-effort) ─────────────────────────────────────
    graph_summary: dict = {}
    risk_breakdown: dict = {}
    try:
        graph_data = await graph_engine.get_graph()
        graph_summary = {
            "nodes": len(graph_data.get("nodes", [])),
            "edges": len(graph_data.get("edges", [])),
        }
        risk_data = await graph_engine.get_risk()
        risk_breakdown = risk_data.get("breakdown", {})
    except Exception as exc:
        logger.warning("Graph engine unavailable for dashboard: %s", exc)

    return DashboardStats(
        total_scans=total_scans,
        total_attacks=total_attacks,
        critical_count=critical_count,
        high_count=high_count,
        medium_count=medium_count,
        low_count=low_count,
        avg_risk_score=avg_risk_score,
        recent_scans=recent_scans,
        recent_attacks=recent_attacks,
        graph_summary=graph_summary,
        risk_breakdown=risk_breakdown,
    )
