"""
Read-only Neo4j repository for the Attack Planner.

INTEGRATION ASSUMPTION (flagged as a risk in the accompanying integration
notes): `digital-twin/neo4j/connection.py` and `digital-twin/graph/builder.py`
are not yet implemented in this codebase, so the exact persisted schema is
unknown. This client assumes:

  1. Every Digital Twin node and relationship carries a `scan_id` property
     that scopes it to one assessment/twin instance.
  2. Node labels match `models.enums.ComponentType` values (User, Assistant,
     Prompt, Retriever, VectorDB, SQL, Email, Slack, GoogleDrive, API,
     Document, Function, Memory).

Once the Digital Twin Builder lands, `_LABEL_TO_COMPONENT` and the Cypher
query below must be reconciled against its actual schema.
"""
from __future__ import annotations

import asyncio
from typing import Optional

from neo4j import AsyncDriver, AsyncGraphDatabase
from neo4j.exceptions import Neo4jError, ServiceUnavailable
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from core.config import AttackEngineSettings
from core.exceptions import GraphRepositoryError
from core.logging_config import get_logger
from models.enums import ComponentType
from models.graph_models import DigitalTwinGraph, GraphEdge, GraphNode

logger = get_logger(__name__)

_LABEL_TO_COMPONENT: dict[str, ComponentType] = {
    "User": ComponentType.USER,
    "Assistant": ComponentType.ASSISTANT,
    "Prompt": ComponentType.PROMPT,
    "Retriever": ComponentType.RETRIEVER,
    "VectorDB": ComponentType.VECTOR_DB,
    "SQL": ComponentType.SQL,
    "Email": ComponentType.EMAIL,
    "Slack": ComponentType.SLACK,
    "GoogleDrive": ComponentType.GOOGLE_DRIVE,
    "API": ComponentType.API,
    "Document": ComponentType.DOCUMENT,
    "Function": ComponentType.FUNCTION,
    "Memory": ComponentType.MEMORY,
}

_DIGITAL_TWIN_QUERY = """
MATCH (n {scan_id: $scan_id})
OPTIONAL MATCH (n)-[r]->(m {scan_id: $scan_id})
RETURN n, labels(n) AS n_labels, elementId(n) AS n_id,
       r, type(r) AS r_type,
       m, labels(m) AS m_labels, elementId(m) AS m_id
"""


class Neo4jGraphRepository:
    """Consumes the Digital Twin graph already persisted in Neo4j.

    Strictly READ-ONLY: this repository must never create, mutate, or
    delete Digital Twin data. Graph ownership belongs to the
    `digital-twin` module; the attack-engine only reads from it.
    """

    def __init__(self, settings: AttackEngineSettings) -> None:
        self._settings = settings
        self._driver: Optional[AsyncDriver] = None
        self._lock = asyncio.Lock()

    async def _get_driver(self) -> AsyncDriver:
        if self._driver is None:
            async with self._lock:
                if self._driver is None:
                    self._driver = AsyncGraphDatabase.driver(
                        self._settings.neo4j_uri,
                        auth=(self._settings.neo4j_user, self._settings.neo4j_password),
                    )
        return self._driver

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=5),
        retry=retry_if_exception_type((ServiceUnavailable, Neo4jError)),
    )
    async def get_digital_twin(self, scan_id: str) -> DigitalTwinGraph:
        if not scan_id or not scan_id.strip():
            raise GraphRepositoryError("scan_id must be a non-empty string")

        driver = await self._get_driver()
        nodes: dict[str, GraphNode] = {}
        edges: list[GraphEdge] = []

        try:
            async with driver.session(database=self._settings.neo4j_database) as session:
                result = await session.run(_DIGITAL_TWIN_QUERY, scan_id=scan_id)
                async for record in result:
                    n_id = record["n_id"]
                    if n_id not in nodes:
                        nodes[n_id] = self._to_graph_node(n_id, record["n_labels"], record["n"])

                    m_record = record["m"]
                    if m_record is not None:
                        m_id = record["m_id"]
                        if m_id not in nodes:
                            nodes[m_id] = self._to_graph_node(m_id, record["m_labels"], m_record)
                        edges.append(
                            GraphEdge(
                                source_id=n_id,
                                target_id=m_id,
                                relationship=record["r_type"] or "RELATED_TO",
                                properties=dict(record["r"]) if record["r"] is not None else {},
                            )
                        )
        except (ServiceUnavailable, Neo4jError) as exc:
            logger.error("neo4j_query_failed", extra={"scan_id": scan_id, "error": str(exc)})
            raise
        except GraphRepositoryError:
            raise
        except Exception as exc:  # defensive boundary: never let an unexpected driver error propagate raw
            logger.exception("unexpected_neo4j_error", extra={"scan_id": scan_id})
            raise GraphRepositoryError(f"Failed to load digital twin graph: {exc}") from exc

        graph = DigitalTwinGraph(nodes=list(nodes.values()), edges=edges)
        logger.info(
            "digital_twin_loaded",
            extra={"scan_id": scan_id, "node_count": len(graph.nodes), "edge_count": len(graph.edges)},
        )
        return graph

    @staticmethod
    def _to_graph_node(node_id: str, labels: list[str], record_node: object) -> GraphNode:
        component_type = ComponentType.UNKNOWN
        for label in labels or []:
            if label in _LABEL_TO_COMPONENT:
                component_type = _LABEL_TO_COMPONENT[label]
                break
        properties = dict(record_node) if record_node is not None else {}
        name = properties.get("name") or properties.get("id") or node_id
        return GraphNode(id=node_id, type=component_type, name=str(name), properties=properties)

    async def close(self) -> None:
        if self._driver is not None:
            await self._driver.close()
            self._driver = None
