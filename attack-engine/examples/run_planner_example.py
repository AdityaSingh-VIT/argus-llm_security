"""
Standalone example: run the Attack Planner against an in-memory digital
twin graph - no live Neo4j / LangGraph service required.

Run from inside attack-engine/:
    python -m examples.run_planner_example
"""
from __future__ import annotations

import asyncio
import json

from agents.planner import PlannerAgent
from models.enums import ComponentType
from models.graph_models import DigitalTwinGraph, GraphEdge, GraphNode
from models.planner_models import DiscoveryContext
from services.interfaces import GraphRepository


class InMemoryGraphRepository(GraphRepository):
    """Test double satisfying the GraphRepository protocol - useful for
    demos, examples, and unit tests without a live Neo4j instance."""

    def __init__(self, twin: DigitalTwinGraph) -> None:
        self._twin = twin

    async def get_digital_twin(self, scan_id: str) -> DigitalTwinGraph:
        return self._twin

    async def close(self) -> None:
        return None


def _sample_twin() -> DigitalTwinGraph:
    """A small support-bot digital twin: chat -> RAG retriever -> vector
    DB, plus a refund function that writes to an orders SQL database, and
    session memory - enough surface to exercise most planner rules."""
    nodes = [
        GraphNode(id="u1", type=ComponentType.USER, name="EndUser"),
        GraphNode(id="a1", type=ComponentType.ASSISTANT, name="SupportBot"),
        GraphNode(id="r1", type=ComponentType.RETRIEVER, name="KBRetriever"),
        GraphNode(id="v1", type=ComponentType.VECTOR_DB, name="SupportKB", properties={"untrusted_source": True}),
        GraphNode(id="f1", type=ComponentType.FUNCTION, name="refund_customer", properties={"write_access": True}),
        GraphNode(id="sql1", type=ComponentType.SQL, name="OrdersDB", properties={"write_access": True}),
        GraphNode(id="mem1", type=ComponentType.MEMORY, name="SessionMemory"),
    ]
    edges = [
        GraphEdge(source_id="u1", target_id="a1", relationship="SENDS_MESSAGE_TO"),
        GraphEdge(source_id="a1", target_id="r1", relationship="QUERIES"),
        GraphEdge(source_id="r1", target_id="v1", relationship="SEARCHES"),
        GraphEdge(source_id="a1", target_id="f1", relationship="INVOKES"),
        GraphEdge(source_id="f1", target_id="sql1", relationship="WRITES_TO"),
        GraphEdge(source_id="a1", target_id="mem1", relationship="READS_WRITES"),
    ]
    return DigitalTwinGraph(nodes=nodes, edges=edges)


async def main() -> None:
    repository = InMemoryGraphRepository(_sample_twin())
    planner = PlannerAgent(graph_repository=repository)

    output = await planner.plan(
        scan_id="demo-scan-001",
        discovery_context=DiscoveryContext(scan_id="demo-scan-001", target_name="Demo Support Bot"),
    )

    print(json.dumps(json.loads(output.model_dump_json()), indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
