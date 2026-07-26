"""
Tests for graph algorithm queries. Neo4j sessions are mocked so these
run without a live database -- they verify our query-building and
result-shaping logic, not Neo4j itself.
"""

from unittest.mock import MagicMock, patch

from queries import graph_queries


@patch("queries.graph_queries.get_session")
def test_critical_nodes_returns_sorted_rows(mock_get_session):
    fake_session = MagicMock()
    fake_session.run.return_value.data.return_value = [
        {"name": "Argus", "label": "Chatbot", "connections": 5},
        {"name": "GPT-5", "label": "LLM", "connections": 2},
    ]
    mock_get_session.return_value.__enter__.return_value = fake_session

    result = graph_queries.critical_nodes(limit=10)

    assert result[0]["name"] == "Argus"
    assert result[0]["connections"] == 5
    fake_session.run.assert_called_once()


@patch("queries.graph_queries.get_session")
def test_most_connected_nodes_delegates_to_critical_nodes(mock_get_session):
    fake_session = MagicMock()
    fake_session.run.return_value.data.return_value = []
    mock_get_session.return_value.__enter__.return_value = fake_session

    result = graph_queries.most_connected_nodes(limit=5)

    assert result == []
    fake_session.run.assert_called_once()
