"""
Unit tests for PlannerAgent.

Run from inside attack-engine/:
    pytest tests -q
"""
from __future__ import annotations

import pytest

from agents.planner import PlannerAgent
from core.exceptions import PlannerError
from models.enums import AttackCategory, ComponentType
from models.graph_models import DigitalTwinGraph, GraphEdge, GraphNode
from models.planner_models import DiscoveryContext
from services.interfaces import GraphRepository


class _FakeRepository(GraphRepository):
    def __init__(self, twin: DigitalTwinGraph) -> None:
        self._twin = twin

    async def get_digital_twin(self, scan_id: str) -> DigitalTwinGraph:
        return self._twin

    async def close(self) -> None:
        return None


def _graph_with_sql_write_sink() -> DigitalTwinGraph:
    nodes = [
        GraphNode(id="u", type=ComponentType.USER, name="User"),
        GraphNode(id="a", type=ComponentType.ASSISTANT, name="Assistant"),
        GraphNode(id="s", type=ComponentType.SQL, name="OrdersDB", properties={"write_access": True}),
    ]
    edges = [
        GraphEdge(source_id="u", target_id="a", relationship="MESSAGES"),
        GraphEdge(source_id="a", target_id="s", relationship="QUERIES"),
    ]
    return DigitalTwinGraph(nodes=nodes, edges=edges)


@pytest.mark.asyncio
async def test_plan_generates_sql_data_access_scenario() -> None:
    planner = PlannerAgent(graph_repository=_FakeRepository(_graph_with_sql_write_sink()))
    output = await planner.plan("scan-1")

    assert output.graph_node_count == 3
    categories = {scenario.category for scenario in output.scenarios}
    assert AttackCategory.DATA_ACCESS_VALIDATION in categories


@pytest.mark.asyncio
async def test_plan_bumps_severity_for_write_access_sink() -> None:
    planner = PlannerAgent(graph_repository=_FakeRepository(_graph_with_sql_write_sink()))
    output = await planner.plan("scan-1b")

    sql_scenarios = [s for s in output.scenarios if s.category == AttackCategory.DATA_ACCESS_VALIDATION]
    assert sql_scenarios
    # base severity for the SQL rule is CRITICAL, and direct 3-node paths
    # plus write_access both escalate further, but severity is clamped -
    # this just asserts it lands at the top of the scale.
    assert sql_scenarios[0].severity_estimate.value == "critical"


@pytest.mark.asyncio
async def test_plan_empty_graph_returns_warning_without_raising() -> None:
    planner = PlannerAgent(graph_repository=_FakeRepository(DigitalTwinGraph()))
    output = await planner.plan("scan-2")

    assert output.scenarios == []
    assert output.warnings


@pytest.mark.asyncio
async def test_plan_rejects_blank_scan_id() -> None:
    planner = PlannerAgent(graph_repository=_FakeRepository(_graph_with_sql_write_sink()))
    with pytest.raises(PlannerError):
        await planner.plan("   ")


@pytest.mark.asyncio
async def test_plan_respects_excluded_categories() -> None:
    planner = PlannerAgent(graph_repository=_FakeRepository(_graph_with_sql_write_sink()))
    output = await planner.plan(
        "scan-3",
        discovery_context=DiscoveryContext(
            scan_id="scan-3", excluded_categories=[AttackCategory.DATA_ACCESS_VALIDATION]
        ),
    )
    assert all(s.category != AttackCategory.DATA_ACCESS_VALIDATION for s in output.scenarios)


@pytest.mark.asyncio
async def test_call_as_langgraph_node_records_errors_on_failure() -> None:
    planner = PlannerAgent(graph_repository=_FakeRepository(_graph_with_sql_write_sink()))
    state = {"scan_id": "", "errors": [], "planner_warnings": []}

    result = await planner(state)

    assert result["candidate_scenarios"] == []
    assert any("attack_planner" in err for err in result["errors"])
