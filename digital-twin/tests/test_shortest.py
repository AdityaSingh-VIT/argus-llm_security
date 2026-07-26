from unittest.mock import MagicMock, patch

from queries import graph_queries


@patch("queries.graph_queries.get_session")
def test_shortest_path_found(mock_get_session):
    fake_session = MagicMock()
    fake_session.run.return_value.data.return_value = [
        {"path": ["External Attacker", "security_report.pdf", "Argus", "ceo@company.com", "CEO"]}
    ]
    mock_get_session.return_value.__enter__.return_value = fake_session

    result = graph_queries.shortest_path("External Attacker", "CEO")

    assert result["found"] is True
    assert result["path"][0] == "External Attacker"
    assert result["path"][-1] == "CEO"


@patch("queries.graph_queries.get_session")
def test_shortest_path_not_found(mock_get_session):
    fake_session = MagicMock()
    fake_session.run.return_value.data.return_value = []
    mock_get_session.return_value.__enter__.return_value = fake_session

    result = graph_queries.shortest_path("Nonexistent", "AlsoNonexistent")

    assert result["found"] is False
    assert result["path"] == []
