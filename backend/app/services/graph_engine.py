"""
services/graph_engine.py — Digital Twin / Graph Engine service client.

MOCK MODE (default while digital-twin team hasn't uploaded yet):
    Set  MOCK_SERVICES=true  in .env  → returns static graph + risk data.

REAL MODE (when digital-twin service is running):
    Set  MOCK_SERVICES=false  and  DIGITAL_TWIN_URL=http://digital-twin:7001

Digital Twin API contract (for reference):
    GET  /graph           → { nodes: [...], edges: [...] }
    POST /build-graph     → { status, nodes_touched }
    GET  /risk            → { risk, level, reasons, breakdown }
    GET  /attack-paths    → [ { attacker, path, relationships, hops } ]
    GET  /critical-nodes  → [ { name, label, connections } ]
    GET  /shortest-path   → { start, end, path, found }
"""

import logging
import os
from typing import Any, Dict, Optional

import httpx
from dotenv import load_dotenv

load_dotenv()

MOCK_SERVICES: bool = os.getenv("MOCK_SERVICES", "true").lower() == "true"
DIGITAL_TWIN_URL: str = os.getenv("DIGITAL_TWIN_URL", "http://digital-twin:7001")
TIMEOUT = httpx.Timeout(30.0)
logger = logging.getLogger("argus.services.graph_engine")


# ── Mock Implementation ───────────────────────────────────────────────────────

async def _mock_get_graph() -> Dict[str, Any]:
    from services.mock_data import MOCK_GRAPH
    logger.info("[MOCK] Returning static graph data")
    return MOCK_GRAPH


async def _mock_build_graph(data: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("[MOCK] Simulating graph build with keys: %s", list(data.keys()))
    return {"status": "graph updated (mock)", "nodes_touched": list(data.keys())}


async def _mock_get_risk(chatbot: Optional[str] = None) -> Dict[str, Any]:
    from services.mock_data import MOCK_RISK
    logger.info("[MOCK] Returning static risk data")
    return MOCK_RISK


async def _mock_get_attack_paths(max_hops: int = 6) -> Any:
    from services.mock_data import MOCK_ATTACK_PATHS
    logger.info("[MOCK] Returning static attack paths")
    return MOCK_ATTACK_PATHS


async def _mock_get_shortest_path(start: str, end: str) -> Dict[str, Any]:
    logger.info("[MOCK] Returning mock shortest path from %s to %s", start, end)
    return {
        "start": start,
        "end": end,
        "path": [start, "Prompt Injection", "Chatbot", end],
        "found": True,
    }


async def _mock_get_critical_nodes(limit: int = 10) -> Any:
    from services.mock_data import MOCK_GRAPH
    nodes = MOCK_GRAPH["nodes"][:limit]
    return [{"name": n["label"], "label": n["type"], "connections": 3} for n in nodes]


# ── Real Implementation ───────────────────────────────────────────────────────

async def _real_get_graph() -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.get(f"{DIGITAL_TWIN_URL}/graph")
        resp.raise_for_status()
        return resp.json()


async def _real_build_graph(data: Dict[str, Any]) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.post(f"{DIGITAL_TWIN_URL}/build-graph", json=data)
        resp.raise_for_status()
        return resp.json()


async def _real_get_risk(chatbot: Optional[str] = None) -> Dict[str, Any]:
    params = {"chatbot": chatbot} if chatbot else {}
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.get(f"{DIGITAL_TWIN_URL}/risk", params=params)
        resp.raise_for_status()
        return resp.json()


async def _real_get_attack_paths(max_hops: int = 6) -> Any:
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.get(f"{DIGITAL_TWIN_URL}/attack-paths", params={"max_hops": max_hops})
        resp.raise_for_status()
        return resp.json()


async def _real_get_shortest_path(start: str, end: str) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.get(f"{DIGITAL_TWIN_URL}/shortest-path", params={"start": start, "end": end})
        resp.raise_for_status()
        return resp.json()


async def _real_get_critical_nodes(limit: int = 10) -> Any:
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.get(f"{DIGITAL_TWIN_URL}/critical-nodes", params={"limit": limit})
        resp.raise_for_status()
        return resp.json()


# ── Public API (auto-selects mock vs real) ────────────────────────────────────

async def get_graph() -> Dict[str, Any]:
    if MOCK_SERVICES:
        return await _mock_get_graph()
    try:
        return await _real_get_graph()
    except httpx.HTTPError as exc:
        logger.warning("Digital twin unreachable, falling back to mock: %s", exc)
        return await _mock_get_graph()


async def build_graph(data: Dict[str, Any]) -> Dict[str, Any]:
    if MOCK_SERVICES:
        return await _mock_build_graph(data)
    try:
        return await _real_build_graph(data)
    except httpx.HTTPError as exc:
        logger.warning("Digital twin build-graph failed, falling back to mock: %s", exc)
        return await _mock_build_graph(data)


async def get_risk(chatbot: Optional[str] = None) -> Dict[str, Any]:
    if MOCK_SERVICES:
        return await _mock_get_risk(chatbot)
    try:
        return await _real_get_risk(chatbot)
    except httpx.HTTPError as exc:
        logger.warning("Digital twin risk failed, falling back to mock: %s", exc)
        return await _mock_get_risk(chatbot)


async def get_attack_paths(max_hops: int = 6) -> Any:
    if MOCK_SERVICES:
        return await _mock_get_attack_paths(max_hops)
    try:
        return await _real_get_attack_paths(max_hops)
    except httpx.HTTPError as exc:
        logger.warning("Digital twin attack-paths failed, falling back to mock: %s", exc)
        return await _mock_get_attack_paths(max_hops)


async def get_shortest_path(start: str, end: str) -> Dict[str, Any]:
    if MOCK_SERVICES:
        return await _mock_get_shortest_path(start, end)
    try:
        return await _real_get_shortest_path(start, end)
    except httpx.HTTPError as exc:
        logger.warning("Digital twin shortest-path failed, falling back to mock: %s", exc)
        return await _mock_get_shortest_path(start, end)


async def get_critical_nodes(limit: int = 10) -> Any:
    if MOCK_SERVICES:
        return await _mock_get_critical_nodes(limit)
    try:
        return await _real_get_critical_nodes(limit)
    except httpx.HTTPError as exc:
        logger.warning("Digital twin critical-nodes failed, falling back to mock: %s", exc)
        return await _mock_get_critical_nodes(limit)
