"""
Unit tests for RiskScorerAgent.
"""
from __future__ import annotations

import pytest

from core.config import AttackEngineSettings
from core.exceptions import RiskScoringError
from models.analysis_models import ResponseAnalysis
from models.enums import AttackCategory, ComponentType, OwaspLlmCategory, Severity
from models.planner_models import AttackPath, AttackPathStep, AttackScenario
from risk.scorer import RiskScorerAgent


def _scenario(severity: Severity = Severity.CRITICAL, path_len: int = 2, category: AttackCategory = AttackCategory.DATA_ACCESS_VALIDATION) -> AttackScenario:
    steps = [
        AttackPathStep(node_id=f"n{i}", component_type=ComponentType.USER, name=f"n{i}")
        for i in range(path_len)
    ]
    return AttackScenario(
        title="scenario",
        category=category,
        owasp_category=OwaspLlmCategory.LLM06_SENSITIVE_INFORMATION_DISCLOSURE,
        objective="obj",
        rationale="rationale",
        target_path=AttackPath(steps=steps),
        affected_components=[s.node_id for s in steps],
        severity_estimate=severity,
        confidence=0.8,
    )


def _finding(attack_success: bool = True, confidence: float = 0.9, scenario_id: str = "s1") -> ResponseAnalysis:
    return ResponseAnalysis(
        execution_result_id="exec-1",
        scenario_id=scenario_id,
        prompt_id="prompt-1",
        attack_success=attack_success,
        confidence=confidence,
        explanation="test",
    )


def test_score_findings_only_scores_successful_attacks() -> None:
    scorer = RiskScorerAgent(settings=AttackEngineSettings())
    scenario = _scenario()
    findings = [_finding(attack_success=True, scenario_id=scenario.id), _finding(attack_success=False, scenario_id=scenario.id)]

    scores = scorer.score_findings(findings, {scenario.id: scenario})

    assert len(scores) == 1


def test_critical_severity_high_confidence_yields_critical_or_high_level() -> None:
    scorer = RiskScorerAgent(settings=AttackEngineSettings())
    scenario = _scenario(severity=Severity.CRITICAL, path_len=2)
    finding = _finding(attack_success=True, confidence=0.95, scenario_id=scenario.id)

    scores = scorer.score_findings([finding], {scenario.id: scenario})

    assert scores[0].level.value in {"critical", "high"}
    assert scores[0].score >= 60


def test_low_severity_low_confidence_yields_lower_score() -> None:
    scorer = RiskScorerAgent(settings=AttackEngineSettings())
    high = _scenario(severity=Severity.CRITICAL, path_len=2)
    low = _scenario(severity=Severity.LOW, path_len=6, category=AttackCategory.SAFETY_BOUNDARY)
    high_finding = _finding(attack_success=True, confidence=0.95, scenario_id=high.id)
    low_finding = _finding(attack_success=True, confidence=0.3, scenario_id=low.id)

    scores = scorer.score_findings(
        [high_finding, low_finding], {high.id: high, low.id: low}
    )

    scores_by_scenario = {s.scenario_id: s.score for s in scores}
    assert scores_by_scenario[high.id] > scores_by_scenario[low.id]


def test_scores_sorted_descending() -> None:
    scorer = RiskScorerAgent(settings=AttackEngineSettings())
    s1, s2 = _scenario(severity=Severity.LOW), _scenario(severity=Severity.CRITICAL)
    findings = [_finding(scenario_id=s1.id, confidence=0.3), _finding(scenario_id=s2.id, confidence=0.95)]

    scores = scorer.score_findings(findings, {s1.id: s1, s2.id: s2})

    assert scores[0].score >= scores[1].score


def test_zero_weights_raise_risk_scoring_error() -> None:
    settings = AttackEngineSettings(
        risk_weight_severity=0, risk_weight_confidence=0, risk_weight_exploitability=0, risk_weight_business_impact=0
    )
    scorer = RiskScorerAgent(settings=settings)
    scenario = _scenario()
    with pytest.raises(RiskScoringError):
        scorer.score_findings([_finding(scenario_id=scenario.id)], {scenario.id: scenario})


@pytest.mark.asyncio
async def test_call_as_langgraph_node_populates_state() -> None:
    scorer = RiskScorerAgent(settings=AttackEngineSettings())
    scenario = _scenario()
    state = {
        "findings": [_finding(scenario_id=scenario.id)],
        "candidate_scenarios": [scenario],
        "errors": [],
    }

    result = await scorer(state)

    assert len(result["risk_scores"]) == 1
    assert result["errors"] == []
