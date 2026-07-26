"""
risk/risk_engine.py

FIXES vs. original calculate_risk():
1. Adds the missing "Tool Access" category (30 pts) required by the spec,
   distinct from "Sensitive Data". Original code only ever scored
   Database access under a 30-point bucket and had no generic notion of
   "tool" -- this reads Chatbot-[:ACCESSES]->Tool and
   Chatbot-[:CALLS]->Database/VectorDB as tool access.
2. Prompt Injection is now detected from the actual graph
   (Attacker-[:USES]->PromptInjection-[:AFFECTS]->Chatbot) instead of a
   string check like `if "Prompt Injection" in target`, which had no
   corresponding node in the original builder and so could never
   actually fire against real graph data.
3. Sensitive Data now checks Chatbot-[:READS]->File/PDF/VectorDB
   generically instead of only PDF.
4. Score is per-chatbot (a real deployment has more than one chatbot in
   the twin eventually), with a `chatbot` parameter; defaults to
   aggregating across the whole graph if not given, to preserve the
   original single-chatbot behavior.
5. Returns a `breakdown` dict (category -> points) instead of just a
   `reasons` list, so the dashboard can show a real bar chart instead of
   just text.
"""

from typing import Optional, Dict, Any

from neo4jk.connection import get_session

MAX_SCORE = 100

WEIGHTS = {
    "prompt_injection": 20,
    "tool_access": 30,
    "sensitive_data": 40,
    "email_access": 20,
}

LEVEL_THRESHOLDS = [
    (80, "Critical"),
    (50, "High"),
    (25, "Medium"),
    (0, "Low"),
]


def _level_for(score: int) -> str:
    for threshold, label in LEVEL_THRESHOLDS:
        if score >= threshold:
            return label
    return "Low"


_RISK_QUERY = """
// Prompt Injection: Attacker -[:USES]-> PromptInjection -[:AFFECTS]-> Chatbot
OPTIONAL MATCH (:Attacker)-[:USES]->(:PromptInjection)-[:AFFECTS]->(c1:Chatbot)
WHERE $chatbot IS NULL OR c1.name = $chatbot
WITH count(DISTINCT c1) > 0 AS has_prompt_injection

// Tool Access: Chatbot -[:ACCESSES]->Tool  OR  Chatbot-[:CALLS]->(Database|VectorDB)
OPTIONAL MATCH (c2:Chatbot)-[:ACCESSES]->(:Tool)
WHERE $chatbot IS NULL OR c2.name = $chatbot
WITH has_prompt_injection, count(DISTINCT c2) AS tool_hits_1
OPTIONAL MATCH (c3:Chatbot)-[:CALLS]->(t)
WHERE (t:Database OR t:VectorDB) AND ($chatbot IS NULL OR c3.name = $chatbot)
WITH has_prompt_injection, tool_hits_1, count(DISTINCT c3) AS tool_hits_2
WITH has_prompt_injection, (tool_hits_1 + tool_hits_2) > 0 AS has_tool_access

// Sensitive Data: Chatbot -[:READS]-> (File|PDF|VectorDB)
OPTIONAL MATCH (c4:Chatbot)-[:READS]->(d)
WHERE (d:File OR d:PDF OR d:VectorDB) AND ($chatbot IS NULL OR c4.name = $chatbot)
WITH has_prompt_injection, has_tool_access, count(DISTINCT c4) > 0 AS has_sensitive_data

// Email Access: Chatbot -[:WRITES]-> Email
OPTIONAL MATCH (c5:Chatbot)-[:WRITES]->(:Email)
WHERE $chatbot IS NULL OR c5.name = $chatbot
WITH has_prompt_injection, has_tool_access, has_sensitive_data,
     count(DISTINCT c5) > 0 AS has_email_access

RETURN has_prompt_injection, has_tool_access, has_sensitive_data, has_email_access
"""


def calculate_risk(chatbot: Optional[str] = None) -> Dict[str, Any]:
    """
    chatbot: optional name to scope the score to one Chatbot node.
             If omitted, scores whether ANY chatbot in the graph exhibits
             each risk factor (matches original whole-graph behavior).
    """
    with get_session() as session:
        record = session.run(_RISK_QUERY, chatbot=chatbot).single()

    breakdown = {}
    reasons = []

    if record["has_prompt_injection"]:
        breakdown["Prompt Injection"] = WEIGHTS["prompt_injection"]
        reasons.append("Prompt Injection")
    if record["has_tool_access"]:
        breakdown["Tool Access"] = WEIGHTS["tool_access"]
        reasons.append("Tool Access")
    if record["has_sensitive_data"]:
        breakdown["Sensitive Data"] = WEIGHTS["sensitive_data"]
        reasons.append("Sensitive Data")
    if record["has_email_access"]:
        breakdown["Email Access"] = WEIGHTS["email_access"]
        reasons.append("Email Access")

    score = min(sum(breakdown.values()), MAX_SCORE)

    return {
        "risk": score,
        "level": _level_for(score),
        "reasons": reasons,
        "breakdown": breakdown,
    }
