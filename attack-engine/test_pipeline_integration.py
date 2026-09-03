"""
End-to-end integration test: runs the full compiled LangGraph pipeline
(planner -> generator -> executor -> analyzer -> risk_scorer ->
report_generator) against an in-memory digital twin and a fake LLM
provider - no live Neo4j, no live network calls.
"""
from __future__ import annotations

import pytest

from agents.planner import PlannerAgent
from core.config import AttackEngineSettings
from evaluation.evaluator import ResponseAnalyzerAgent
from executor.executor import AttackExecutorAgent
from executor.providers.base import ProviderResponse
from examples.run_planner_example import InMemoryGraphRepository, _sample_twin
from generator.generator import PromptGeneratorAgent
from graph.workflow import build_full_attack_pipeline
from models.planner_models import DiscoveryContext
from reporting.report_generator import ReportGeneratorAgent
from risk.scorer import RiskScorerAgent


class _ScriptedAdapter:
    """Fake provider: complies (and leaks a fake credential) on the
    Data-Access-Validation / SQL attack prompt - which the planner
    reliably produces for the sample twin's SQL sink - and refuses
    everything else, so the pipeline has both a failed and a successful
    attack to carry through analysis, scoring, and reporting."""

    provider_name = "fake"

    async def generate(self, prompt: str, model: str, timeout_seconds: float) -> ProviderResponse:
        if "bypass normal access checks" in prompt.lower():
            return ProviderResponse(text="Sure! SELECT * FROM users; api_key=sk-FAKEFAKEFAKEFAKEFAKE1234")
        return ProviderResponse(text="I'm sorry, but I can't help with that request.")


@pytest.mark.asyncio
async def test_full_pipeline_produces_risk_scores_and_report() -> None:
    settings = AttackEngineSettings(executor_default_provider="fake", executor_default_model="fake-model")

    planner = PlannerAgent(graph_repository=InMemoryGraphRepository(_sample_twin()), settings=settings)
    generator = PromptGeneratorAgent(settings=settings)
    executor = AttackExecutorAgent(providers={"fake": _ScriptedAdapter()}, settings=settings)
    analyzer = ResponseAnalyzerAgent(settings=settings)
    risk_scorer = RiskScorerAgent(settings=settings)
    reporter = ReportGeneratorAgent()

    app = build_full_attack_pipeline(planner, generator, executor, analyzer, risk_scorer, report_agent=reporter)

    result = await app.ainvoke(
        {
            "scan_id": "integration-scan-1",
            "discovery_context": DiscoveryContext(scan_id="integration-scan-1", target_name="Demo Support Bot"),
            "errors": [],
        }
    )

    assert result["candidate_scenarios"], "planner produced no scenarios"
    assert result["candidate_prompts"], "generator produced no prompts"
    assert result["execution_results"], "executor produced no results"
    assert result["findings"], "analyzer produced no findings"
    # At least the system-prompt-exposure path should have succeeded and scored.
    assert result["risk_scores"], "risk scorer produced no scores"
    assert any(f.attack_success for f in result["findings"])
    assert any(not f.attack_success for f in result["findings"])
    assert result["report_markdown"] and "Security Assessment Report" in result["report_markdown"]
    assert result["report_json"]
    assert result["report_html"]
    assert result["errors"] == []


@pytest.mark.asyncio
async def test_partial_pipeline_planner_and_generator_only() -> None:
    """The graph builder must still support a partial pipeline (no
    executor/analyzer/risk_scorer wired) without error."""
    from graph.workflow import build_attack_planning_graph

    settings = AttackEngineSettings()
    planner = PlannerAgent(graph_repository=InMemoryGraphRepository(_sample_twin()), settings=settings)
    generator = PromptGeneratorAgent(settings=settings)

    app = build_attack_planning_graph(planner, generator_agent=generator)
    result = await app.ainvoke({"scan_id": "partial-scan", "errors": []})

    assert result["candidate_scenarios"]
    assert result["candidate_prompts"]
    assert "execution_results" not in result  # executor was never wired
