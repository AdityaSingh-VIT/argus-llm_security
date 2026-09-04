"""
Service-layer abstractions. The Attack Planner depends on these
protocols, never on a concrete driver, so it can be unit-tested with a
fake repository and swapped onto a different backing store later
without touching agent code (Dependency Inversion Principle).
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from models.graph_models import DigitalTwinGraph


@runtime_checkable
class GraphRepository(Protocol):
    """Read-only accessor for the persisted Digital Twin graph.

    Concrete implementation: `services.neo4j_client.Neo4jGraphRepository`.
    Test/example double: see `examples/run_planner_example.py`.
    """

    async def get_digital_twin(self, scan_id: str) -> DigitalTwinGraph:
        ...

    async def close(self) -> None:
        ...
