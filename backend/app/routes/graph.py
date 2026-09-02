"""
routes/graph.py — Proxy routes for the Digital Twin Graph Engine.

These endpoints let the frontend call the backend for graph data
instead of calling the digital-twin service directly.

GET  /graph/nodes         → full graph (nodes + edges)
GET  /graph/risk          → risk score + breakdown
GET  /graph/attack-paths  → multi-hop attack chains
GET  /graph/shortest-path → shortest path between two nodes
POST /graph/build         → push component data into graph
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Query

from auth.dependencies import get_current_user
from models.schemas import UserOut
from services import graph_engine

router = APIRouter()


@router.get("/nodes", summary="Get the full Digital Twin graph (nodes + edges)")
async def get_graph(_: UserOut = Depends(get_current_user)) -> Dict[str, Any]:
    return await graph_engine.get_graph()


@router.get("/risk", summary="Get risk score from Digital Twin")
async def get_risk(
    chatbot: Optional[str] = Query(default=None, description="Scope to one chatbot node"),
    _: UserOut = Depends(get_current_user),
) -> Dict[str, Any]:
    return await graph_engine.get_risk(chatbot=chatbot)


@router.get("/attack-paths", summary="Get attack chains from Digital Twin")
async def get_attack_paths(
    max_hops: int = Query(default=6, ge=1, le=15),
    _: UserOut = Depends(get_current_user),
) -> Any:
    return await graph_engine.get_attack_paths(max_hops=max_hops)


@router.get("/shortest-path", summary="Shortest attack path between two nodes")
async def get_shortest_path(
    start: str = Query(..., example="External Attacker"),
    end: str = Query(..., example="CEO"),
    _: UserOut = Depends(get_current_user),
) -> Dict[str, Any]:
    return await graph_engine.get_shortest_path(start=start, end=end)


@router.get("/critical-nodes", summary="Most connected nodes in the graph")
async def get_critical_nodes(
    limit: int = Query(default=10, ge=1, le=50),
    _: UserOut = Depends(get_current_user),
) -> Any:
    return await graph_engine.get_critical_nodes(limit=limit)


@router.post("/build", summary="Push component metadata into the Digital Twin")
async def build_graph(
    data: Dict[str, Any],
    _: UserOut = Depends(get_current_user),
) -> Dict[str, Any]:
    return await graph_engine.build_graph(data)
