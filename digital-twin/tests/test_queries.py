from unittest.mock import MagicMock, patch

from queries import graph_queries
from graph.builder import build_digital_twin


@patch("queries.graph_queries.get_session")
def test_get_graph_json_shape(mock_get_session):
    fake_session = MagicMock()
    fake_session.run.side_effect = [
        MagicMock(data=lambda: [
            {"id": "n1", "name": "Argus", "address": None, "label": "Chatbot"},
            {"id": "n2", "name": "GPT-5", "address": None, "label": "LLM"},
        ]),
        MagicMock(data=lambda: [
            {"id": "e1", "source": "n1", "target": "n2", "relationship": "CALLS"},
        ]),
    ]
    mock_get_session.return_value.__enter__.return_value = fake_session

    result = graph_queries.get_graph_json()

    assert "nodes" in result and "edges" in result
    assert result["nodes"][0]["id"] == "n1"
    assert result["nodes"][0]["label"] == "Chatbot"
    assert result["edges"][0]["relationship"] == "CALLS"


@patch("graph.builder.get_session")
def test_build_digital_twin_requires_data(mock_get_session):
    try:
        build_digital_twin({})
        assert False, "expected ValueError for empty data"
    except ValueError:
        pass
    mock_get_session.assert_not_called()


@patch("graph.builder.get_session")
def test_build_digital_twin_runs_write_transaction(mock_get_session):
    fake_session = MagicMock()
    mock_get_session.return_value.__enter__.return_value = fake_session

    result = build_digital_twin({"user": "Admin", "chatbot": "Argus"})

    fake_session.execute_write.assert_called_once()
    assert result["status"] == "graph updated"
    assert "user" in result["nodes_touched"]
