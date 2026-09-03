"""
Pydantic models owned by the Attack Planner stage.

Note on scope: models for downstream stages (AttackResult, RiskFinding,
Mitigation, ConversationTrace, ExecutionState) are intentionally NOT
defined here - they belong to the Prompt Generator / Execution
Coordinator / Response Analyzer / Risk Scorer / Mitigation Generator
agents, which are still Pending per the project ProgressLog. Defining
them now without an implementation would be a placeholder, which this
codebase's standards explicitly disallow.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field

from models.enums import AttackCategory, ComponentType, OwaspLlmCategory, Severity
from models.graph_models import GraphNode


class AttackPathStep(BaseModel):
    node_id: str
    component_type: ComponentType
    name: str


class AttackPath(BaseModel):
    steps: list[AttackPathStep]

    @classmethod
    def from_nodes(cls, nodes: list[GraphNode]) -> "AttackPath":
        return cls(
            steps=[
                AttackPathStep(node_id=node.id, component_type=node.type, name=node.name)
                for node in nodes
            ]
        )

    def summary(self) -> str:
        return " -> ".join(f"{step.name}:{step.component_type.value}" for step in self.steps)


class AttackScenario(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    category: AttackCategory
    owasp_category: OwaspLlmCategory
    objective: str
    rationale: str
    target_path: AttackPath
    affected_components: list[str]
    severity_estimate: Severity
    confidence: float = Field(ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DiscoveryContext(BaseModel):
    """Supplementary scan-scope metadata supplied by the caller (e.g. the
    orchestration layer or API request). The Digital Twin graph itself
    remains the single source of truth for discovered tools, APIs, vector
    stores, memory, and plugins per the project spec ("Do NOT recreate
    the graph. Consume it."); this model only carries scope/constraint
    information the graph does not encode.
    """

    scan_id: str
    target_name: Optional[str] = None
    included_categories: Optional[list[AttackCategory]] = None
    excluded_categories: Optional[list[AttackCategory]] = None
    notes: Optional[str] = None


class PlannerOutput(BaseModel):
    scan_id: str
    scenarios: list[AttackScenario]
    graph_node_count: int
    graph_edge_count: int
    warnings: list[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
