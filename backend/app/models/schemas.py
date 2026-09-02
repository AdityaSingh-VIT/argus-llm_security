"""
models/schemas.py — Pydantic request/response schemas for all API endpoints.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


# ── Auth ──────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    email: str
    created_at: datetime


# ── Scan ──────────────────────────────────────────────────────────────────────

class ScanRequest(BaseModel):
    target_url: str
    project_name: str
    num_attacks: int = 5


class ScanJobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_name: str
    target_url: str
    status: str
    started_at: datetime
    finished_at: Optional[datetime] = None


# ── Attack Results ────────────────────────────────────────────────────────────

class AttackResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    scan_id: str
    prompt: str
    response: str
    score: float
    category: str
    timestamp: datetime


# ── Report ────────────────────────────────────────────────────────────────────

class ReportRequest(BaseModel):
    scan_id: str


class ReportOut(BaseModel):
    scan_id: str
    file_path: str
    created_at: datetime


# ── Dashboard ─────────────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_scans: int
    total_attacks: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    avg_risk_score: float
    recent_scans: List[ScanJobOut]
    recent_attacks: List[AttackResultOut]
    graph_summary: Dict[str, Any] = {}
    risk_breakdown: Dict[str, Any] = {}
