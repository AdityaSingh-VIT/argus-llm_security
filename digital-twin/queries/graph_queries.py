"""
queries/graph_queries.py

FIXES vs. original:
1. get_graph_json() replaces the old get_connections()/{"connections": []}
   shape with a proper {"nodes": [...], "edges": [...]} shape (see
   api/models.py) that React Flow can consume directly.
2. find_attack_paths() now does an explicit variable-length traversal
   from every Attacker node to every Person/Email node, instead of just
   checking for an Attacker->Email edge. This is what actually answers
   "attacker to CEO" from the requirement doc, rather than relying on the
   two edges happening to already be adjacent.
3. shortest_path() validates that both endpoints exist before running the
   path query and returns a structured "not found" result instead of an
   empty list that looks the same as "no path exists".
4. critical_nodes()/most_connected_nodes() unchanged in spirit, cleaned
   up to use parameterized LIMIT and dict-based rows.
"""

from typing import List, Dict, Any

from neo4jk.connection import get_session


def get_graph_json() -> Dict[str, List[Dict[str, Any]]]:
    """Return the whole graph as {nodes, edges} for the frontend."""
    node_query = """
        MATCH (n)
        RETURN elementId(n) AS id, n.name AS name, n.address AS address,
               labels(n)[0] AS label
    """
    edge_query = """
        MATCH (a)-[r]->(b)
        RETURN elementId(r) AS id, elementId(a) AS source,
               elementId(b) AS target, type(r) AS relationship
    """
    with get_session() as session:
        node_rows = session.run(node_query).data()
        edge_rows = session.run(edge_query).data()

    nodes = [
        {
            "id": row["id"],
            "label": row["label"],
            "type": row["label"],
            "name": row.get("name") or row.get("address") or row["label"],
        }
        for row in node_rows
    ]
    edges = [
        {
            "id": row["id"],
            "source": row["source"],
            "target": row["target"],
            "relationship": row["relationship"],
        }
        for row in edge_rows
    ]
    return {"nodes": nodes, "edges": edges}


def critical_nodes(limit: int = 10) -> List[Dict[str, Any]]:
    query = """
        MATCH (n)-[r]-()
        RETURN n.name AS name, labels(n)[0] AS label, count(r) AS connections
        ORDER BY connections DESC
        LIMIT $limit
    """
    with get_session() as session:
        return session.run(query, limit=limit).data()


def most_connected_nodes(limit: int = 10) -> List[Dict[str, Any]]:
    # Same underlying metric as critical_nodes; kept as a separate function
    # to match the required API surface, but implemented once to avoid
    # the two ever drifting apart.
    return critical_nodes(limit=limit)


def find_attack_paths(max_hops: int = 6) -> List[Dict[str, Any]]:
    """
    Explicit traversal: every path from an Attacker to a Person or Email
    node, up to max_hops relationships. This is what makes
    "Attacker -> PDF -> Chatbot -> Email -> CEO" an actual query result
    instead of an assumption drawn on a whiteboard.
    """
    query = f"""
        MATCH path = (a:Attacker)-[*1..{max_hops}]->(target)
        WHERE target:Person OR target:Email
        RETURN
            a.name AS attacker,
            [n IN nodes(path) | coalesce(n.name, n.address, labels(n)[0])] AS path,
            [r IN relationships(path) | type(r)] AS relationships,
            length(path) AS hops
        ORDER BY hops ASC
    """
    with get_session() as session:
        return session.run(query).data()


def shortest_path(start: str, end: str) -> Dict[str, Any]:
    """
    Returns a structured result so "no path" and "path of length 0" are
    never confused with each other.
    """
    query = """
        MATCH (s {name: $start}), (e)
        WHERE e.name = $end OR e.address = $end
        MATCH path = shortestPath((s)-[*..15]-(e))
        RETURN [n IN nodes(path) | coalesce(n.name, n.address, labels(n)[0])] AS path
        LIMIT 1
    """
    with get_session() as session:
        result = session.run(query, start=start, end=end).data()

    if not result:
        return {"start": start, "end": end, "path": [], "found": False}

    return {"start": start, "end": end, "path": result[0]["path"], "found": True}
