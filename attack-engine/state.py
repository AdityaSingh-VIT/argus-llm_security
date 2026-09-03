"""
Shared LangGraph state for the attack-engine pipeline.

Previously, only the Attack Planner's fields were populated and the rest
were declared as `Optional[list[Any]]` placeholders reserved for later
implementation. Prompt Generator, Attack Executor, Response Analyzer, and
Risk Scorer are now implemented, so their fields below carry real types.

One consolidation: the earlier reserved `test_cases` field is dropped in
favor of `candidate_prompts` (Prompt Generator's actual output) - nothing
in the codebase ever read or wrote `test_cases`, so this is not a
breaking change to any real functionality, just tidying an unused
placeholder into the field that now actually exists.

Mitigation Generator remains Pending and its field stays reserved.
"""
from __future__ import annotations

from typing import Any, Optional, TypedDict

from models.analysis_models import ResponseAnalysis
from models.execution_models import ExecutionResult
from models.planner_models import AttackScenario, DiscoveryContext
from models.prompt_models import GeneratedPrompt
from models.risk_models import RiskScore


class WorkflowState(TypedDict, total=False):
    # --- Inputs (from Discovery Engine / Digital Twin, both already built) ---
    scan_id: str
    discovery_context: Optional[DiscoveryContext]

    # --- Attack Planner output ---
    candidate_scenarios: list[AttackScenario]
    planner_warnings: list[str]

    # --- Prompt Generator output ---
    candidate_prompts: list[GeneratedPrompt]
    generator_warnings: list[str]

    # --- Attack Executor output ---
    execution_results: list[ExecutionResult]

    # --- Response Analyzer output ---
    findings: list[ResponseAnalysis]

    # --- Risk Scorer output ---
    risk_scores: list[RiskScore]

    # --- Report Generator output ---
    report_markdown: Optional[str]
    report_json: Optional[str]
    report_html: Optional[str]

    # --- Cross-cutting ---
    errors: list[str]

    # --- Reserved for the (still Pending) Mitigation Generator ---
    mitigations: Optional[list[Any]]
