"""
Pydantic models owned by the Response Analyzer stage.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field

from models.enums import OwaspLlmCategory


class DetectorResult(BaseModel):
    """Output of a single detector run over one response."""

    name: str
    triggered: bool
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: Optional[str] = None


class ResponseAnalysis(BaseModel):
    """Structured finding produced by combining all detector results for
    one ExecutionResult into a single verdict."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    execution_result_id: str
    scenario_id: str
    prompt_id: str
    attack_success: bool
    confidence: float = Field(ge=0.0, le=1.0)
    violated_policy: Optional[OwaspLlmCategory] = None
    evidence: list[str] = Field(default_factory=list)
    explanation: str
    detector_results: list[DetectorResult] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
