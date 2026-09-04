"""
Typed representation of the Digital Twin graph, as consumed (never
recreated) by the Attack Planner. Traversal logic lives on the model
itself (single responsibility: the graph knows how to walk itself; the
Planner knows how to interpret the resulting paths as attack scenarios).
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from models.enums import ComponentType


class GraphNode(BaseModel):
    id: str
    type: ComponentType
    name: str
    properties: dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    source_id: str
    target_id: str
    relationship: str
    properties: dict[str, Any] = Field(default_factory=dict)


class DigitalTwinGraph(BaseModel):
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)

    def node_index(self) -> dict[str, GraphNode]:
        return {node.id: node for node in self.nodes}

    def adjacency(self) -> dict[str, list[GraphEdge]]:
        index: dict[str, list[GraphEdge]] = {}
        for edge in self.edges:
            index.setdefault(edge.source_id, []).append(edge)
        return index

    def nodes_of_type(self, *types: ComponentType) -> list[GraphNode]:
        return [node for node in self.nodes if node.type in types]

    def find_attack_paths(
        self,
        entry_types: tuple[ComponentType, ...],
        sink_types: tuple[ComponentType, ...],
        max_depth: int = 6,
        max_paths: int = 500,
    ) -> list[list[GraphNode]]:
        """Depth-limited DFS enumerating simple (cycle-free) paths from any
        entry-type node to any sink-type node.

        `max_depth` bounds path length and `max_paths` bounds total paths
        returned, guarding against combinatorial explosion on dense/large
        digital twins - both are configurable via AttackEngineSettings.
        """
        node_index = self.node_index()
        adjacency = self.adjacency()
        entry_nodes = self.nodes_of_type(*entry_types)
        sink_id_set = {node.id for node in self.nodes_of_type(*sink_types)}

        paths: list[list[GraphNode]] = []

        def dfs(current_id: str, visited: set[str], trail: list[str]) -> None:
            if len(paths) >= max_paths or len(trail) > max_depth:
                return
            if current_id in sink_id_set and len(trail) > 1:
                paths.append([node_index[node_id] for node_id in trail])
            for edge in adjacency.get(current_id, []):
                if len(paths) >= max_paths:
                    return
                if edge.target_id in visited or edge.target_id not in node_index:
                    continue
                dfs(edge.target_id, visited | {edge.target_id}, trail + [edge.target_id])

        for entry in entry_nodes:
            if len(paths) >= max_paths:
                break
            dfs(entry.id, {entry.id}, [entry.id])

        return paths
