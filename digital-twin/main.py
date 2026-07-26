"""
main.py

FIXES vs. original:
1. Adds POST /build-graph -- the "Automatic Graph Updates" gap. Chatbot
   events can now push metadata straight into the twin instead of only
   being buildable by manually running builder.py.
2. GET /graph now returns {nodes, edges} (see api/models.py,
   queries/graph_queries.py) instead of {"connections": []}.
3. GET /shortest-path takes start/end as query params (the original
   listed the route but the params weren't wired to the function
   signature).
4. Adds startup/shutdown hooks that open the Neo4j driver once and close
   it cleanly, instead of relying on ad-hoc driver creation per request.
5. Adds CORS middleware -- the React frontend (a different origin in
   dev) cannot call this API at all without it.
6. Wraps Neo4j errors as HTTP 503s instead of letting them surface as
   raw 500 stack traces to the frontend.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from neo4j.exceptions import Neo4jError

from graph.builder import build_digital_twin
from api.models import BuildGraphRequest, GraphJSON, RiskResponse, ShortestPathResponse
from queries import graph_queries
from risk.risk_engine import calculate_risk
from neo4jk.connection import get_driver, close_driver

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("digital_twin.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_driver()  # verifies connectivity at startup, fails fast if bad
    yield
    close_driver()


app = FastAPI(title="Digital Twin API", lifespan=lifespan)

# Dev-friendly CORS. Tighten allow_origins to the real frontend origin(s)
# before this goes anywhere near production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _wrap_neo4j_errors(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Neo4jError as e:
        logger.exception("Neo4j query failed")
        raise HTTPException(status_code=503, detail=f"Graph database error: {e}")


@app.get("/")
def health():
    return {"message": "Digital Twin API running"}


@app.post("/build-graph")
def build_graph(payload: BuildGraphRequest):
    """
    Ingests chatbot metadata/events and MERGEs them into the graph.
    This is the endpoint the chatbot (or any upstream event source)
    should call after every relevant action, closing the gap called
    out as 'Automatic Graph Updates' in the requirements review.
    """
    data = payload.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(status_code=400, detail="Request body had no fields set")
    return _wrap_neo4j_errors(build_digital_twin, data)


@app.get("/graph", response_model=GraphJSON)
def get_graph():
    return _wrap_neo4j_errors(graph_queries.get_graph_json)


@app.get("/risk", response_model=RiskResponse)
def get_risk(chatbot: str | None = Query(default=None, description="Scope risk to one Chatbot node")):
    return _wrap_neo4j_errors(calculate_risk, chatbot=chatbot)


@app.get("/attack-paths")
def get_attack_paths(max_hops: int = Query(default=6, ge=1, le=15)):
    return _wrap_neo4j_errors(graph_queries.find_attack_paths, max_hops=max_hops)


@app.get("/critical-nodes")
def get_critical_nodes(limit: int = Query(default=10, ge=1, le=100)):
    return _wrap_neo4j_errors(graph_queries.critical_nodes, limit=limit)


@app.get("/most-connected")
def get_most_connected(limit: int = Query(default=10, ge=1, le=100)):
    return _wrap_neo4j_errors(graph_queries.most_connected_nodes, limit=limit)


@app.get("/shortest-path", response_model=ShortestPathResponse)
def get_shortest_path(
    start: str = Query(..., description="Start node name, e.g. 'External Attacker'"),
    end: str = Query(..., description="End node name/email, e.g. 'CEO' or 'ceo@company.com'"),
):
    return _wrap_neo4j_errors(graph_queries.shortest_path, start=start, end=end)
