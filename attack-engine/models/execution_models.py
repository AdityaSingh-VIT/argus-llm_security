"""
Pydantic models owned by the Attack Executor stage.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ExecutionStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"


class ExecutionResult(BaseModel):
    """One record per prompt sent to a provider. Persists everything the
    Response Analyzer / Risk Scorer / Report Generator need downstream,
    plus everything an operator needs to debug a failed call."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    prompt_id: str
    scenario_id: str
    provider: str
    model: str
    request_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    response_text: str
    latency_ms: float
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    status: ExecutionStatus
    error: Optional[str] = None
