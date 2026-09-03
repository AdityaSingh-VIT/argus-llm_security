"""
Pydantic models owned by the Prompt Generator stage.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from models.enums import AttackCategory, MutationStrategy, Severity


class GeneratedPrompt(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    scenario_id: str
    category: AttackCategory
    title: str
    content: str
    mutation_strategy: MutationStrategy
    variant_index: int
    expected_behavior: str
    success_criteria: str
    severity: Severity
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PromptGenerationOutput(BaseModel):
    scan_id: str
    prompts: list[GeneratedPrompt]
    warnings: list[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
