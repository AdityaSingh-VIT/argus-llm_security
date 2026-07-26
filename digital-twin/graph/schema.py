"""
graph/schema.py

Single source of truth for node labels and relationship types.

WHY THIS FILE EXISTS
---------------------
In the original implementation, labels like "PDF", "VectorDB", "Database"
and relationships like "CALLS", "READS" were typed as raw strings in
multiple files (builder.py, graph_queries.py, risk_engine.py). That's how
schema drift happens silently -- a typo in one file doesn't create an
error, it just creates a node/edge that the rest of the system can't see.

Everything in this project should import from here instead of typing
label/relationship strings by hand.
"""

from enum import Enum


class NodeLabel(str, Enum):
    USER = "User"
    CHATBOT = "Chatbot"
    LLM = "LLM"
    FILE = "File"          # NEW: generic file node (was missing)
    PDF = "PDF"
    DATABASE = "Database"
    VECTOR_DB = "VectorDB"
    EMAIL = "Email"
    PERSON = "Person"      # NEW: covers CEO / any human email recipient
    ATTACKER = "Attacker"
    PROMPT_INJECTION = "PromptInjection"
    TOOL = "Tool"          # NEW: generic "Tool Access" target


class RelType(str, Enum):
    USES = "USES"
    CALLS = "CALLS"
    READS = "READS"
    WRITES = "WRITES"
    EXPLOITS = "EXPLOITS"
    AFFECTS = "AFFECTS"
    IS_A = "IS_A"          # File -[:IS_A]-> PDF  (type hierarchy)
    SENDS_TO = "SENDS_TO"  # Email -[:SENDS_TO]-> Person
    ACCESSES = "ACCESSES"  # Chatbot -[:ACCESSES]-> Tool


# Risk weighting lives here too so builder/risk engine can't drift apart
# on what a "sensitive" or "tool" relationship means.
SENSITIVE_READ_TARGETS = {NodeLabel.PDF, NodeLabel.FILE, NodeLabel.VECTOR_DB}
TOOL_ACCESS_TARGETS = {NodeLabel.DATABASE, NodeLabel.TOOL, NodeLabel.VECTOR_DB}
