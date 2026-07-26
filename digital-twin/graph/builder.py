"""
graph/builder.py

Builds/updates the Digital Twin graph in Neo4j from chatbot metadata.
"""

import logging

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
    recipient = data.get("recipient")
    attacker = data.get("attacker")
    prompt_injection = data.get("prompt_injection")
    tool = data.get("tool")

    # --- User -> Chatbot ---------------------------------------------

    if user and chatbot:
        tx.run(
            f"""
            MERGE (u:{NodeLabel.USER.value} {{name:$user}})
            MERGE (c:{NodeLabel.CHATBOT.value} {{name:$chatbot}})
            MERGE (u)-[:{RelType.USES.value}]->(c)
            """,
            user=user,
            chatbot=chatbot,
        )

    # --- Chatbot -> LLM ----------------------------------------------

    if chatbot and llm:
        tx.run(
            f"""
            MERGE (c:{NodeLabel.CHATBOT.value} {{name:$chatbot}})
            MERGE (l:{NodeLabel.LLM.value} {{name:$llm}})
            MERGE (c)-[:{RelType.CALLS.value}]->(l)
            """,
            chatbot=chatbot,
            llm=llm,
        )

    # --- File / PDF --------------------------------------------------

    if chatbot and pdf:
        tx.run(
            f"""
            MERGE (c:{NodeLabel.CHATBOT.value} {{name:$chatbot}})
            MERGE (f:{NodeLabel.FILE.value} {{name:$pdf}})
            MERGE (p:{NodeLabel.PDF.value} {{name:$pdf}})
            MERGE (f)-[:{RelType.IS_A.value}]->(p)
            MERGE (c)-[:{RelType.READS.value}]->(f)
            """,
            chatbot=chatbot,
            pdf=pdf,
        )

    # --- Database ----------------------------------------------------

    if chatbot and database:
        tx.run(
            f"""
            MERGE (c:{NodeLabel.CHATBOT.value} {{name:$chatbot}})
            MERGE (d:{NodeLabel.DATABASE.value} {{name:$database}})
            MERGE (c)-[:{RelType.CALLS.value}]->(d)
            """,
            chatbot=chatbot,
            database=database,
        )

    # --- Vector DB ---------------------------------------------------

    if chatbot and vector_db:
        tx.run(
            f"""
            MERGE (c:{NodeLabel.CHATBOT.value} {{name:$chatbot}})
            MERGE (v:{NodeLabel.VECTOR_DB.value} {{name:$vector_db}})
            MERGE (c)-[:{RelType.READS.value}]->(v)
            """,
            chatbot=chatbot,
            vector_db=vector_db,
        )

    # --- Email -> Person ---------------------------------------------

    if chatbot and email:
        tx.run(
            f"""
            MERGE (c:{NodeLabel.CHATBOT.value} {{name:$chatbot}})
            MERGE (e:{NodeLabel.EMAIL.value} {{address:$email}})
            MERGE (c)-[:{RelType.WRITES.value}]->(e)
            """,
            chatbot=chatbot,
            email=email,
        )

        if recipient:
            tx.run(
                f"""
                MERGE (e:{NodeLabel.EMAIL.value} {{address:$email}})
                MERGE (p:{NodeLabel.PERSON.value} {{name:$recipient}})
                MERGE (e)-[:{RelType.SENDS_TO.value}]->(p)
                """,
                email=email,
                recipient=recipient,
            )

    # --- Attacker -> PDF ---------------------------------------------

    if attacker and pdf:
        tx.run(
            f"""
            MERGE (a:{NodeLabel.ATTACKER.value} {{name:$attacker}})
            MERGE (p:{NodeLabel.PDF.value} {{name:$pdf}})
            MERGE (a)-[:{RelType.EXPLOITS.value}]->(p)
            """,
            attacker=attacker,
            pdf=pdf,
        )

    # --- Prompt Injection --------------------------------------------

    if attacker and prompt_injection and chatbot:
        tx.run(
            f"""
            MERGE (a:{NodeLabel.ATTACKER.value} {{name:$attacker}})
            MERGE (pi:{NodeLabel.PROMPT_INJECTION.value} {{name:$prompt_injection}})
            MERGE (c:{NodeLabel.CHATBOT.value} {{name:$chatbot}})

            MERGE (a)-[:{RelType.USES.value}]->(pi)
            MERGE (pi)-[:{RelType.AFFECTS.value}]->(c)
            """,
            attacker=attacker,
            prompt_injection=prompt_injection,
            chatbot=chatbot,
        )

    # --- Tool Access -------------------------------------------------

    if chatbot and tool:
        tx.run(
            f"""
            MERGE (c:{NodeLabel.CHATBOT.value} {{name:$chatbot}})
            MERGE (t:{NodeLabel.TOOL.value} {{name:$tool}})
            MERGE (c)-[:{RelType.ACCESSES.value}]->(t)
            """,
            chatbot=chatbot,
            tool=tool,
        )


def build_digital_twin(data: dict) -> dict:
    """
    Idempotently MERGE metadata into Neo4j.
    """

    if not isinstance(data, dict) or not data:
        raise ValueError("build_digital_twin requires a non-empty dict")

    with get_session() as session:
        session.execute_write(_build_tx, data)

    logger.info(
        "Digital twin updated from metadata: %s",
        list(data.keys())
    )

    return {
        "status": "graph updated",
        "nodes_touched": [
            k for k in data.keys()
            if data.get(k)
        ],
    }
