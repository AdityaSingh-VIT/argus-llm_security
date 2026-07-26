"""
graph/builder.py

Builds/updates the Digital Twin graph in Neo4j from chatbot metadata.

FIXES vs. original build_digital_twin():
1. Generic File node added: File -[:IS_A]-> PDF, and Chatbot -[:READS]-> File
   (previously Chatbot only READS PDF directly, which didn't satisfy the
   "Files" node requirement).
2. Prompt Injection is now actually created as a node + wired into the
   attack chain: Attacker -[:USES]-> PromptInjection -[:AFFECTS]-> Chatbot.
   Previously the risk engine referenced "Prompt Injection" as a string
   but the builder never created the node, so the risk reason and the
   graph disagreed with each other.
3. Person node (e.g. CEO) added as the actual email recipient:
   Chatbot -[:WRITES]-> Email -[:SENDS_TO]-> Person.
   Previously the chain stopped at Email with no recipient node, so
   "attack path to the CEO" wasn't a real traversable path -- it was
   just implied in a diagram.
4. Tool node added for generic tool access scoring (see risk_engine.py):
   Chatbot -[:ACCESSES]-> Tool. Database/VectorDB counted as tools too.
5. All labels/relationship types now pulled from graph/schema.py so a
   typo can't silently create an orphan label.
6. MERGE is still used throughout (idempotent -- rerunning with the same
   data does not create duplicates), but now runs as ONE transaction
   instead of many auto-committed statements, so a partial failure can't
   leave the graph half-updated.
"""

import logging
from typing import Optional

from graph.schema import NodeLabel, RelType
from neo4jk.connection import get_session

logger = logging.getLogger("digital_twin.builder")


def _build_tx(tx, data: dict):
    user = data.get("user")
    chatbot = data.get("chatbot")
    llm = data.get("llm")
    pdf = data.get("pdf")
    database = data.get("database")
    vector_db = data.get("vector_db")
    email = data.get("email")
    recipient = data.get("recipient")          # NEW, e.g. "CEO"
    attacker = data.get("attacker")
    prompt_injection = data.get("prompt_injection")  # NEW, e.g. "Malicious PDF Instruction"
    tool = data.get("tool")                     # NEW, e.g. "Internal Search API"

    # --- Core actors -----------------------------------------------------
    if user and chatbot:
        tx.run(
            f"""
            MERGE (u:{NodeLabel.USER} {{name:$user}})
            MERGE (c:{NodeLabel.CHATBOT} {{name:$chatbot}})
            MERGE (u)-[:{RelType.USES}]->(c)
            """,
            user=user, chatbot=chatbot,
        )

    if chatbot and llm:
        tx.run(
            f"""
            MERGE (c:{NodeLabel.CHATBOT} {{name:$chatbot}})
            MERGE (l:{NodeLabel.LLM} {{name:$llm}})
            MERGE (c)-[:{RelType.CALLS}]->(l)
            """,
            chatbot=chatbot, llm=llm,
        )

    # --- File / PDF (fixed: generic File node now exists) ---------------
    if chatbot and pdf:
        tx.run(
            f"""
            MERGE (c:{NodeLabel.CHATBOT} {{name:$chatbot}})
            MERGE (f:{NodeLabel.FILE} {{name:$pdf}})
            MERGE (p:{NodeLabel.PDF} {{name:$pdf}})
            MERGE (f)-[:{RelType.IS_A}]->(p)
            MERGE (c)-[:{RelType.READS}]->(f)
            """,
            chatbot=chatbot, pdf=pdf,
        )

    # --- Database ----------------------------------------------------------
    if chatbot and database:
        tx.run(
            f"""
            MERGE (c:{NodeLabel.CHATBOT} {{name:$chatbot}})
            MERGE (d:{NodeLabel.DATABASE} {{name:$database}})
            MERGE (c)-[:{RelType.CALLS}]->(d)
            """,
            chatbot=chatbot, database=database,
        )

    # --- Vector DB -----------------------------------------------------
    if chatbot and vector_db:
        tx.run(
            f"""
            MERGE (c:{NodeLabel.CHATBOT} {{name:$chatbot}})
            MERGE (v:{NodeLabel.VECTOR_DB} {{name:$vector_db}})
            MERGE (c)-[:{RelType.READS}]->(v)
            """,
            chatbot=chatbot, vector_db=vector_db,
        )

    # --- Email + recipient (fixed: recipient/Person node now exists) ----
    if chatbot and email:
        tx.run(
            f"""
            MERGE (c:{NodeLabel.CHATBOT} {{name:$chatbot}})
            MERGE (e:{NodeLabel.EMAIL} {{address:$email}})
            MERGE (c)-[:{RelType.WRITES}]->(e)
            """,
            chatbot=chatbot, email=email,
        )
        if recipient:
            tx.run(
                f"""
                MERGE (e:{NodeLabel.EMAIL} {{address:$email}})
                MERGE (p:{NodeLabel.PERSON} {{name:$recipient}})
                MERGE (e)-[:{RelType.SENDS_TO}]->(p)
                """,
                email=email, recipient=recipient,
            )

    # --- Attacker -> PDF (existing) -------------------------------------
    if attacker and pdf:
        tx.run(
            f"""
            MERGE (a:{NodeLabel.ATTACKER} {{name:$attacker}})
            MERGE (p:{NodeLabel.PDF} {{name:$pdf}})
            MERGE (a)-[:{RelType.EXPLOITS}]->(p)
            """,
            attacker=attacker, pdf=pdf,
        )

    # --- Prompt Injection (fixed: node now actually created) -----------
    if attacker and prompt_injection and chatbot:
        tx.run(
            f"""
            MERGE (a:{NodeLabel.ATTACKER} {{name:$attacker}})
            MERGE (pi:{NodeLabel.PROMPT_INJECTION} {{name:$prompt_injection}})
            MERGE (c:{NodeLabel.CHATBOT} {{name:$chatbot}})
            MERGE (a)-[:{RelType.USES}]->(pi)
            MERGE (pi)-[:{RelType.AFFECTS}]->(c)
            """,
            attacker=attacker, prompt_injection=prompt_injection, chatbot=chatbot,
        )

    # --- Tool access (fixed: generic Tool Access category now exists) --
    if chatbot and tool:
        tx.run(
            f"""
            MERGE (c:{NodeLabel.CHATBOT} {{name:$chatbot}})
            MERGE (t:{NodeLabel.TOOL} {{name:$tool}})
            MERGE (c)-[:{RelType.ACCESSES}]->(t)
            """,
            chatbot=chatbot, tool=tool,
        )


def build_digital_twin(data: dict) -> dict:
    """
    Idempotently MERGE the given metadata into the graph, as one
    transaction. Returns a small summary so callers/API responses have
    something concrete to show, instead of a bare {"status": "ok"}.
    """
    if not isinstance(data, dict) or not data:
        raise ValueError("build_digital_twin requires a non-empty dict")

    with get_session() as session:
        session.execute_write(_build_tx, data)

    logger.info("Digital twin updated from metadata: %s", list(data.keys()))
    return {
        "status": "graph updated",
        "nodes_touched": [k for k in data.keys() if data.get(k)],
    }
