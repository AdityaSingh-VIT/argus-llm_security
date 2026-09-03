"""
Attack Planner agent.

Consumes the persisted Digital Twin graph for a scan and produces a
ranked list of candidate AttackScenario objects with severity estimates.
Deliberately rule-based/deterministic (no LLM call) so planning output is
reproducible and independently unit-testable; narrative prompt authoring
is delegated to the (Pending) Prompt Generator agent downstream.
"""
from __future__ import annotations

from typing import Optional

from agents.base import BaseAgent
from core.config import AttackEngineSettings, get_settings
from core.exceptions import GraphRepositoryError, PlannerError
from graph.state import WorkflowState
from knowledge.attack_patterns import AttackPatternCatalog, AttackPatternRule
from models.enums import ComponentType, Severity, bump_severity, severity_rank
from models.graph_models import GraphNode
from models.planner_models import AttackPath, AttackScenario, DiscoveryContext, PlannerOutput
from services.interfaces import GraphRepository

_ENTRY_TYPES: tuple[ComponentType, ...] = (ComponentType.USER, ComponentType.ASSISTANT)

_SINK_TYPES: tuple[ComponentType, ...] = (
    ComponentType.SQL,
    ComponentType.EMAIL,
    ComponentType.SLACK,
    ComponentType.GOOGLE_DRIVE,
    ComponentType.API,
    ComponentType.DOCUMENT,
    ComponentType.FUNCTION,
    ComponentType.MEMORY,
    ComponentType.VECTOR_DB,
    ComponentType.PROMPT,
)

_SIDE_EFFECTING_TYPES = {
    ComponentType.SQL,
    ComponentType.EMAIL,
    ComponentType.SLACK,
    ComponentType.GOOGLE_DRIVE,
    ComponentType.FUNCTION,
    ComponentType.API,
}


class PlannerAgent(BaseAgent[WorkflowState]):
    """LangGraph node + standalone service for attack-path planning."""

    name = "attack_planner"

    def __init__(
        self,
        graph_repository: GraphRepository,
        pattern_catalog: Optional[AttackPatternCatalog] = None,
        settings: Optional[AttackEngineSettings] = None,
    ) -> None:
        super().__init__()
        self._graph_repository = graph_repository
        self._catalog = pattern_catalog or AttackPatternCatalog()
        self._settings = settings or get_settings()

    # ------------------------------------------------------------------
    # Public service API (usable outside of LangGraph, e.g. from tests,
    # the example script, or a future FastAPI endpoint).
    # ------------------------------------------------------------------
    async def plan(
        self, scan_id: str, discovery_context: Optional[DiscoveryContext] = None
    ) -> PlannerOutput:
        if not scan_id or not scan_id.strip():
            raise PlannerError("scan_id must be a non-empty string")

        self.logger.info("planning_started", extra={"scan_id": scan_id})
        warnings: list[str] = []

        try:
            twin = await self._graph_repository.get_digital_twin(scan_id)
        except GraphRepositoryError:
            raise
        except Exception as exc:  # pragma: no cover - defensive boundary
            self.logger.exception("planner_graph_fetch_failed", extra={"scan_id": scan_id})
            raise PlannerError(f"Unable to load digital twin for scan {scan_id}: {exc}") from exc

        if not twin.nodes:
            self.logger.warning("empty_digital_twin", extra={"scan_id": scan_id})
            return PlannerOutput(
                scan_id=scan_id,
                scenarios=[],
                graph_node_count=0,
                graph_edge_count=0,
                warnings=["Digital twin graph is empty; no attack paths could be planned."],
            )

        raw_paths = twin.find_attack_paths(
            entry_types=_ENTRY_TYPES,
            sink_types=_SINK_TYPES,
            max_depth=self._settings.planner_max_path_depth,
            max_paths=self._settings.planner_max_paths,
        )
        if not raw_paths:
            warnings.append("No reachable attack paths were found from entry points to known sinks.")

        scenarios = self._build_scenarios(raw_paths)
        scenarios = self._filter_by_scope(scenarios, discovery_context)
        scenarios = self._deduplicate(scenarios)
        scenarios = [s for s in scenarios if s.confidence >= self._settings.planner_min_confidence]
        scenarios.sort(key=lambda s: (severity_rank(s.severity_estimate), s.confidence), reverse=True)
        scenarios = scenarios[: self._settings.planner_max_scenarios_per_scan]

        self.logger.info(
            "planning_completed",
            extra={"scan_id": scan_id, "scenario_count": len(scenarios), "path_count": len(raw_paths)},
        )

        return PlannerOutput(
            scan_id=scan_id,
            scenarios=scenarios,
            graph_node_count=len(twin.nodes),
            graph_edge_count=len(twin.edges),
            warnings=warnings,
        )

    # ------------------------------------------------------------------
    # Scenario construction & scoring
    # ------------------------------------------------------------------
    def _build_scenarios(self, paths: list[list[GraphNode]]) -> list[AttackScenario]:
        scenarios: list[AttackScenario] = []
        for path in paths:
            for rule in self._catalog.match(path):
                attack_path = AttackPath.from_nodes(path)
                sink = path[-1]
                severity = self._estimate_severity(rule.base_severity, path, sink)
                confidence = self._estimate_confidence(path)
                objective, rationale = self._render_rule_text(rule, sink, attack_path)

                scenarios.append(
                    AttackScenario(
                        title=f"{rule.name}: {sink.name}",
                        category=rule.category,
                        owasp_category=rule.owasp_category,
                        objective=objective,
                        rationale=rationale,
                        target_path=attack_path,
                        affected_components=[node.id for node in path],
                        severity_estimate=severity,
                        confidence=confidence,
                    )
                )
        return scenarios

    @staticmethod
    def _render_rule_text(
        rule: AttackPatternRule, sink: GraphNode, attack_path: AttackPath
    ) -> tuple[str, str]:
        try:
            objective = rule.objective_template.format(sink_name=sink.name, path_summary=attack_path.summary())
            rationale = rule.rationale_template.format(sink_name=sink.name, path_summary=attack_path.summary())
        except (KeyError, IndexError):
            # A malformed template must never break planning - fall back to
            # the raw template text rather than raising.
            objective, rationale = rule.objective_template, rule.rationale_template
        return objective, rationale

    @staticmethod
    def _estimate_severity(base_severity: Severity, path: list[GraphNode], sink: GraphNode) -> Severity:
        """Heuristic severity escalation on top of the rule's base
        severity. Each signal below independently indicates increased
        real-world risk and is additive (capped at CRITICAL by
        bump_severity)."""
        severity = base_severity
        if sink.type in _SIDE_EFFECTING_TYPES and bool(sink.properties.get("write_access")):
            severity = bump_severity(severity, 1)
        if len(path) <= 2:
            # Direct exposure with no intermediate control is more dangerous.
            severity = bump_severity(severity, 1)
        if bool(sink.properties.get("external")) or bool(sink.properties.get("internet_facing")):
            severity = bump_severity(severity, 1)
        return severity

    @staticmethod
    def _estimate_confidence(path: list[GraphNode]) -> float:
        """Shorter, more direct paths are estimated with higher confidence;
        long, indirect paths are noisier and scored more conservatively.
        Presence of an explicitly untrusted source nudges confidence up."""
        base = 0.9 - (max(len(path) - 2, 0) * 0.08)
        if any(bool(node.properties.get("untrusted_source")) for node in path):
            base += 0.05
        return max(0.1, min(base, 0.95))

    @staticmethod
    def _filter_by_scope(
        scenarios: list[AttackScenario], discovery_context: Optional[DiscoveryContext]
    ) -> list[AttackScenario]:
        if discovery_context is None:
            return scenarios
        result = scenarios
        if discovery_context.included_categories:
            included = set(discovery_context.included_categories)
            result = [s for s in result if s.category in included]
        if discovery_context.excluded_categories:
            excluded = set(discovery_context.excluded_categories)
            result = [s for s in result if s.category not in excluded]
        return result

    @staticmethod
    def _deduplicate(scenarios: list[AttackScenario]) -> list[AttackScenario]:
        """Collapse scenarios that share a category + terminal sink,
        keeping the highest-severity representative."""
        best: dict[tuple[str, str], AttackScenario] = {}
        for scenario in scenarios:
            key = (scenario.category.value, scenario.affected_components[-1])
            existing = best.get(key)
            if existing is None or severity_rank(scenario.severity_estimate) > severity_rank(
                existing.severity_estimate
            ):
                best[key] = scenario
        return list(best.values())

    # ------------------------------------------------------------------
    # LangGraph node adapter
    # ------------------------------------------------------------------
    async def __call__(self, state: WorkflowState) -> WorkflowState:
        scan_id = state.get("scan_id", "")
        discovery_context = state.get("discovery_context")
        errors = list(state.get("errors", []))
        warnings = list(state.get("planner_warnings", []))

        try:
            output = await self.plan(scan_id, discovery_context)
            warnings.extend(output.warnings)
            return {
                **state,
                "candidate_scenarios": output.scenarios,
                "planner_warnings": warnings,
                "errors": errors,
            }
        except PlannerError as exc:
            # Graceful degradation: a Planner failure is recorded on the
            # shared state rather than crashing the whole LangGraph run,
            # so the dashboard can surface it instead of losing the scan.
            self.logger.error("planner_node_failed", extra={"scan_id": scan_id, "error": str(exc)})
            errors.append(f"[{self.name}] {exc}")
            return {
                **state,
                "candidate_scenarios": [],
                "planner_warnings": warnings,
                "errors": errors,
            }
