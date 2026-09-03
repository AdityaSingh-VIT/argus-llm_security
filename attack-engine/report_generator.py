"""
Report Generator.

Assembles the full attack-engine pipeline output (scenarios, prompts,
execution results, findings, risk scores) into a human-readable Markdown
report, a machine-readable JSON report, and a lightweight HTML report.

NOTE ON SCOPE: like risk/, there was no pre-existing stub reserved for
this stage - it's new, added as a sibling to the existing stage folders.

`ReportGenerator` is a plain service class usable outside of LangGraph
(report generation typically happens once, after a scan completes, not
on every state transition). `ReportGeneratorAgent` is provided as an
optional graph node wrapper for pipelines that want it as the final
LangGraph step instead.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone

from agents.base import BaseAgent
from graph.state import WorkflowState
from models.analysis_models import ResponseAnalysis
from models.execution_models import ExecutionResult
from models.planner_models import AttackScenario
from models.prompt_models import GeneratedPrompt
from models.risk_models import RiskLevel, RiskScore

# Lightweight, category-keyed remediation guidance. This intentionally
# stays inside the Report Generator rather than becoming a separate
# Mitigation Generator agent, which was not part of this change's scope.
_RECOMMENDATIONS: dict[str, str] = {
    "indirect_prompt_injection": "Sanitize and clearly delimit retrieved content; never let retrieved text carry instruction-level authority.",
    "rag_poisoning": "Validate and provenance-check documents before ingestion into the vector store; monitor for anomalous entries.",
    "tool_misuse": "Require explicit user confirmation before invoking side-effecting tools; scope tool credentials tightly.",
    "function_calling_misuse": "Validate function arguments server-side; never trust LLM-issued parameters directly.",
    "data_access_validation": "Enforce row/column-level authorization independent of the LLM layer.",
    "agent_workflow_manipulation": "Add hard-coded workflow checkpoints that cannot be skipped via prompt content.",
    "memory_manipulation": "Sanitize content written to long-term memory; treat memory writes as untrusted input.",
    "system_prompt_exposure": "Avoid relying on system-prompt secrecy for security; treat it as potentially public.",
    "excessive_agency": "Apply least-privilege scoping and human-in-the-loop approval for high-impact actions.",
    "data_exfiltration": "Apply output filtering/DLP on responses that reference internal identifiers or records.",
    "sql_injection_via_llm": "Never interpolate LLM output directly into SQL; use parameterized queries exclusively.",
}
_DEFAULT_RECOMMENDATION = "Review the affected component's trust boundary and add explicit authorization checks."


@dataclass
class ReportContext:
    scan_id: str
    scenarios: list[AttackScenario] = field(default_factory=list)
    prompts: list[GeneratedPrompt] = field(default_factory=list)
    execution_results: list[ExecutionResult] = field(default_factory=list)
    findings: list[ResponseAnalysis] = field(default_factory=list)
    risk_scores: list[RiskScore] = field(default_factory=list)
    target_name: str = "the target system"
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ReportGenerator:
    def __init__(self, context: ReportContext) -> None:
        self._ctx = context

    def _stats(self) -> dict:
        successful = [f for f in self._ctx.findings if f.attack_success]
        models_used = sorted({r.model for r in self._ctx.execution_results})
        providers_used = sorted({r.provider for r in self._ctx.execution_results})
        return {
            "scan_id": self._ctx.scan_id,
            "target": self._ctx.target_name,
            "scenarios_planned": len(self._ctx.scenarios),
            "prompts_generated": len(self._ctx.prompts),
            "executions": len(self._ctx.execution_results),
            "findings": len(self._ctx.findings),
            "successful_attacks": len(successful),
            "failed_attacks": len(self._ctx.findings) - len(successful),
            "risk_scores": len(self._ctx.risk_scores),
            "critical_count": sum(1 for r in self._ctx.risk_scores if r.level == RiskLevel.CRITICAL),
            "high_count": sum(1 for r in self._ctx.risk_scores if r.level == RiskLevel.HIGH),
            "medium_count": sum(1 for r in self._ctx.risk_scores if r.level == RiskLevel.MEDIUM),
            "low_count": sum(1 for r in self._ctx.risk_scores if r.level == RiskLevel.LOW),
            "providers": providers_used,
            "models": models_used,
            "generated_at": self._ctx.generated_at.isoformat(),
        }

    def _recommendations(self) -> list[dict]:
        categories = {s.category.value for s in self._ctx.scenarios}
        return [
            {"category": cat, "recommendation": _RECOMMENDATIONS.get(cat, _DEFAULT_RECOMMENDATION)}
            for cat in sorted(categories)
        ]

    def _attack_chain(self) -> list[dict]:
        """One row per scenario, in the order the pipeline processed it,
        showing how it flowed from plan -> finding -> risk score."""
        risk_by_scenario = {r.scenario_id: r for r in self._ctx.risk_scores}
        finding_by_scenario = {f.scenario_id: f for f in self._ctx.findings if f.attack_success}
        chain = []
        for scenario in self._ctx.scenarios:
            finding = finding_by_scenario.get(scenario.id)
            risk = risk_by_scenario.get(scenario.id)
            chain.append(
                {
                    "scenario": scenario.title,
                    "category": scenario.category.value,
                    "attack_path": scenario.target_path.summary(),
                    "succeeded": finding is not None,
                    "risk_score": risk.score if risk else None,
                    "risk_level": risk.level.value if risk else None,
                }
            )
        return chain

    def _successful_attacks_grouped(self) -> list[dict]:
        """One entry per scenario (not per mutation-variant finding) for
        the report's narrative sections. A scenario is typically tested
        via several GeneratedPrompt variants (paraphrase, synonym
        replacement, etc.); without grouping, a scenario where 5 variants
        all succeeded would appear as 5 near-identical report entries."""
        scenario_by_id = {s.id: s for s in self._ctx.scenarios}
        risk_by_finding = {r.finding_id: r for r in self._ctx.risk_scores}

        findings_by_scenario: dict[str, list] = {}
        analyzed_by_scenario: dict[str, int] = {}
        for finding in self._ctx.findings:
            analyzed_by_scenario[finding.scenario_id] = analyzed_by_scenario.get(finding.scenario_id, 0) + 1
            if finding.attack_success:
                findings_by_scenario.setdefault(finding.scenario_id, []).append(finding)

        grouped = []
        for scenario_id, findings in findings_by_scenario.items():
            scenario = scenario_by_id.get(scenario_id)
            scored = [(f, risk_by_finding.get(f.id)) for f in findings]
            # Represent the scenario by its highest-risk-scoring variant
            # (falling back to highest confidence if scores are missing).
            best_finding, best_risk = max(
                scored, key=lambda pair: (pair[1].score if pair[1] else 0, pair[0].confidence)
            )
            evidence = sorted({item for f in findings for item in f.evidence})
            grouped.append(
                {
                    "title": scenario.title if scenario else scenario_id,
                    "category": scenario.category.value if scenario else "unknown",
                    "variants_succeeded": len(findings),
                    "variants_analyzed": analyzed_by_scenario.get(scenario_id, len(findings)),
                    "risk": best_risk,
                    "explanation": best_finding.explanation,
                    "evidence": evidence,
                }
            )
        grouped.sort(key=lambda g: (g["risk"].score if g["risk"] else 0), reverse=True)
        return grouped

    def to_json(self) -> str:
        payload = {
            "stats": self._stats(),
            "attack_chain": self._attack_chain(),
            "successful_attacks": [
                {**{k: v for k, v in g.items() if k != "risk"}, "risk_score": g["risk"].score if g["risk"] else None,
                 "risk_level": g["risk"].level.value if g["risk"] else None}
                for g in self._successful_attacks_grouped()
            ],
            "scenarios": [s.model_dump(mode="json") for s in self._ctx.scenarios],
            "findings": [f.model_dump(mode="json") for f in self._ctx.findings],
            "risk_scores": [r.model_dump(mode="json") for r in self._ctx.risk_scores],
            "recommendations": self._recommendations(),
        }
        return json.dumps(payload, indent=2, default=str)

    def to_markdown(self) -> str:
        stats = self._stats()
        lines = [
            f"# Security Assessment Report - {stats['target']}",
            "",
            f"_Scan ID: `{stats['scan_id']}` | Generated: {stats['generated_at']}_",
            f"_Providers: {', '.join(stats['providers']) or 'n/a'} | Models: {', '.join(stats['models']) or 'n/a'}_",
            "",
            "## Executive Summary",
            "",
            f"- Scenarios planned: **{stats['scenarios_planned']}**",
            f"- Prompts executed: **{stats['executions']}**",
            f"- Findings analyzed: **{stats['findings']}**",
            f"- Successful attacks: **{stats['successful_attacks']}**",
            f"- Failed attacks: **{stats['failed_attacks']}**",
            f"- Risk distribution: Critical **{stats['critical_count']}** / High **{stats['high_count']}** / "
            f"Medium **{stats['medium_count']}** / Low **{stats['low_count']}**",
            "",
            "## Attack Chain",
            "",
            "| Scenario | Category | Succeeded | Risk |",
            "|---|---|---|---|",
        ]
        for row in self._attack_chain():
            risk_cell = f"{row['risk_score']}/100 ({row['risk_level'].upper()})" if row["risk_score"] is not None else "-"
            lines.append(f"| {row['scenario']} | {row['category']} | {'Yes' if row['succeeded'] else 'No'} | {risk_cell} |")

        lines += ["", "## Successful Attacks (Risk Findings)", ""]
        grouped = self._successful_attacks_grouped()
        if not grouped:
            lines.append("_No successful attacks were recorded for this scan._")
        for entry in grouped:
            lines.append(f"### {entry['title']}")
            lines.append(
                f"**Variants succeeded:** {entry['variants_succeeded']}/{entry['variants_analyzed']} tested"
            )
            if entry["risk"]:
                lines.append(f"**Risk score:** {entry['risk'].score}/100 ({entry['risk'].level.value.upper()})")
            lines.append(f"**Explanation:** {entry['explanation']}")
            if entry["evidence"]:
                lines.append(f"**Evidence:** {'; '.join(entry['evidence'])}")
            lines.append("")

        failed_count = stats["failed_attacks"]
        lines += ["## Failed Attacks", "", f"{failed_count} attack attempt(s) did not succeed (target refused or no unsafe behavior was detected).", ""]

        lines += ["## Recommendations", ""]
        for rec in self._recommendations():
            lines.append(f"- **{rec['category']}**: {rec['recommendation']}")

        return "\n".join(lines)

    def to_html(self) -> str:
        stats = self._stats()
        chain_rows = "".join(
            f"<tr><td>{row['scenario']}</td><td>{row['category']}</td>"
            f"<td>{'Yes' if row['succeeded'] else 'No'}</td>"
            f"<td>{row['risk_score'] if row['risk_score'] is not None else '-'}</td></tr>"
            for row in self._attack_chain()
        )
        return (
            "<html><head><meta charset='utf-8'><title>Security Assessment Report</title></head><body>"
            f"<h1>Security Assessment Report - {stats['target']}</h1>"
            f"<p>Scan ID: {stats['scan_id']} | Generated: {stats['generated_at']}</p>"
            "<h2>Summary</h2>"
            f"<ul><li>Scenarios: {stats['scenarios_planned']}</li>"
            f"<li>Executions: {stats['executions']}</li>"
            f"<li>Successful attacks: {stats['successful_attacks']}</li>"
            f"<li>Critical: {stats['critical_count']} | High: {stats['high_count']} | "
            f"Medium: {stats['medium_count']} | Low: {stats['low_count']}</li></ul>"
            "<h2>Attack Chain</h2>"
            f"<table border='1' cellpadding='4'><tr><th>Scenario</th><th>Category</th><th>Succeeded</th><th>Risk Score</th></tr>{chain_rows}</table>"
            "</body></html>"
        )


class ReportGeneratorAgent(BaseAgent[WorkflowState]):
    """Optional LangGraph node wrapper around ReportGenerator."""

    name = "report_generator"

    async def __call__(self, state: WorkflowState) -> WorkflowState:
        discovery_context = state.get("discovery_context")
        context = ReportContext(
            scan_id=state.get("scan_id", ""),
            scenarios=state.get("candidate_scenarios", []) or [],
            prompts=state.get("candidate_prompts", []) or [],
            execution_results=state.get("execution_results", []) or [],
            findings=state.get("findings", []) or [],
            risk_scores=state.get("risk_scores", []) or [],
            target_name=(discovery_context.target_name if discovery_context else None) or "the target system",
        )
        generator = ReportGenerator(context)
        self.logger.info("report_generated", extra={"scan_id": context.scan_id})
        return {
            **state,
            "report_markdown": generator.to_markdown(),
            "report_json": generator.to_json(),
            "report_html": generator.to_html(),
        }
