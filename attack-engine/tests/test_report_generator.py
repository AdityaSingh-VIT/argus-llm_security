"""
Unit tests for ReportGenerator (Markdown / JSON / HTML output).
"""
from __future__ import annotations

import json

from models.analysis_models import ResponseAnalysis
from models.enums import AttackCategory, ComponentType, OwaspLlmCategory, Severity
from models.planner_models import AttackPath, AttackPathStep, AttackScenario
from models.risk_models import RiskLevel, RiskScore
from reporting.report_generator import ReportContext, ReportGenerator


def _scenario() -> AttackScenario:
    path = AttackPath(steps=[AttackPathStep(node_id="u", component_type=ComponentType.USER, name="User")])
    return AttackScenario(
        title="System Prompt Exposure: Prompt",
        category=AttackCategory.SYSTEM_PROMPT_EXPOSURE,
        owasp_category=OwaspLlmCategory.LLM07_SYSTEM_PROMPT_LEAKAGE,
        objective="reveal the system prompt",
        rationale="directly attached",
        target_path=path,
        affected_components=["u"],
        severity_estimate=Severity.MEDIUM,
        confidence=0.7,
    )


def _context() -> ReportContext:
    scenario = _scenario()
    finding = ResponseAnalysis(
        execution_result_id="exec-1",
        scenario_id=scenario.id,
        prompt_id="prompt-1",
        attack_success=True,
        confidence=0.8,
        evidence=["you are a helpful assistant"],
        explanation="Target leaked its system prompt.",
    )
    risk = RiskScore(
        finding_id=finding.id,
        scenario_id=scenario.id,
        score=72.5,
        level=RiskLevel.HIGH,
        severity_component=0.5,
        confidence_component=0.8,
        exploitability_component=0.9,
        business_impact_component=0.6,
    )
    return ReportContext(
        scan_id="scan-report-1",
        scenarios=[scenario],
        findings=[finding],
        risk_scores=[risk],
        target_name="Demo Bot",
    )


def test_to_markdown_includes_key_sections() -> None:
    report = ReportGenerator(_context()).to_markdown()
    assert "# Security Assessment Report - Demo Bot" in report
    assert "## Executive Summary" in report
    assert "## Attack Chain" in report
    assert "## Successful Attacks (Risk Findings)" in report
    assert "## Recommendations" in report
    assert "72.5/100 (HIGH)" in report


def test_to_json_is_valid_and_contains_stats() -> None:
    report = ReportGenerator(_context()).to_json()
    payload = json.loads(report)
    assert payload["stats"]["scan_id"] == "scan-report-1"
    assert payload["stats"]["successful_attacks"] == 1
    assert len(payload["risk_scores"]) == 1


def test_to_html_is_well_formed_and_contains_data() -> None:
    report = ReportGenerator(_context()).to_html()
    assert report.startswith("<html>")
    assert report.endswith("</html>")
    assert "Demo Bot" in report
    assert "<table" in report


def test_report_with_no_findings_does_not_crash() -> None:
    empty_context = ReportContext(scan_id="empty-scan")
    generator = ReportGenerator(empty_context)
    assert "No successful attacks" in generator.to_markdown()
    json.loads(generator.to_json())  # must still be valid JSON
    assert "<html>" in generator.to_html()


def test_multiple_successful_variants_of_same_scenario_collapse_to_one_entry() -> None:
    """Regression test: a scenario tested via several mutation-variant
    prompts, where multiple variants succeed, must appear once in the
    report - not once per successful variant."""
    scenario = _scenario()
    findings = [
        ResponseAnalysis(
            execution_result_id=f"exec-{i}",
            scenario_id=scenario.id,
            prompt_id=f"prompt-{i}",
            attack_success=True,
            confidence=0.7 + i * 0.05,
            evidence=[f"evidence-{i}"],
            explanation=f"Variant {i} leaked data.",
        )
        for i in range(3)
    ]
    risk_scores = [
        RiskScore(
            finding_id=f.id, scenario_id=scenario.id, score=50 + i * 5, level=RiskLevel.HIGH,
            severity_component=0.5, confidence_component=f.confidence,
            exploitability_component=0.5, business_impact_component=0.5,
        )
        for i, f in enumerate(findings)
    ]
    context = ReportContext(scan_id="dup-scan", scenarios=[scenario], findings=findings, risk_scores=risk_scores)

    markdown = ReportGenerator(context).to_markdown()
    json_payload = json.loads(ReportGenerator(context).to_json())

    # The scenario title should appear exactly once as a section heading,
    # not once per successful variant.
    assert markdown.count(f"### {scenario.title}") == 1
    assert "3/3 tested" in markdown
    assert len(json_payload["successful_attacks"]) == 1
    assert json_payload["successful_attacks"][0]["variants_succeeded"] == 3
