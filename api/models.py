"""
api/models.py

Pydantic schemas.

FIXES vs. original:
- The original /graph endpoint returned {"connections": [...]} which is
  not what React Flow (or most graph UIs) consume. React Flow wants
  separate `nodes` and `edges` arrays with stable `id` fields. This file
  defines that shape so builder/query code and the API agree on it.
- BuildGraphRequest gives the missing POST /build-graph endpoint real
  input validation instead of accepting an untyped dict.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class BuildGraphRequest(BaseModel):
    user: Optional[str] = None
    chatbot: Optional[str] = None
    llm: Optional[str] = None
    pdf: Optional[str] = None
    database: Optional[str] = None
    vector_db: Optional[str] = None
    email: Optional[str] = None
    recipient: Optional[str] = None            # e.g. "CEO"
    attacker: Optional[str] = None
    prompt_injection: Optional[str] = None      # e.g. "Malicious instruction in PDF"
    tool: Optional[str] = None                  # e.g. "Internal Search API"


class GraphNode(BaseModel):
    id: str
    label: str          # node type, e.g. "Chatbot", "PDF"
    type: str            # duplicate of label kept for React Flow node "type" field


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    relationship: str


class GraphJSON(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]


class RiskResponse(BaseModel):
    risk: int
    level: str
    reasons: List[str]
    breakdown: dict = Field(default_factory=dict)


class ShortestPathResponse(BaseModel):
    start: str
    end: str
    path: List[str]
    found: bool
