"""
Pydantic models owned by the Risk Scorer stage.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskScore(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    finding_id: str
    scenario_id: str
    score: float = Field(ge=0.0, le=100.0)
    level: RiskLevel
    severity_component: float
    confidence_component: float
    exploitability_component: float
    business_impact_component: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
