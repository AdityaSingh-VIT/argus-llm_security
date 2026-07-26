from unittest.mock import MagicMock, patch

from queries import graph_queries
from risk import risk_engine


@patch("queries.graph_queries.get_session")
def test_find_attack_paths_returns_full_chain(mock_get_session):
    fake_session = MagicMock()
    fake_session.run.return_value.data.return_value = [
        {
            "attacker": "External Attacker",
            "path": ["External Attacker", "security_report.pdf", "Argus", "ceo@company.com", "CEO"],
            "relationships": ["EXPLOITS", "READS", "WRITES", "SENDS_TO"],
            "hops": 4,
        }
    ]
    mock_get_session.return_value.__enter__.return_value = fake_session

    paths = graph_queries.find_attack_paths(max_hops=6)

    assert len(paths) == 1
    assert paths[0]["path"][0] == "External Attacker"
    assert paths[0]["path"][-1] == "CEO"


@patch("risk.risk_engine.get_session")
def test_calculate_risk_full_chain_hits_critical(mock_get_session):
    fake_session = MagicMock()
    fake_record = {
        "has_prompt_injection": True,
        "has_tool_access": True,
        "has_sensitive_data": True,
        "has_email_access": True,
    }
    fake_session.run.return_value.single.return_value = fake_record
    mock_get_session.return_value.__enter__.return_value = fake_session

    result = risk_engine.calculate_risk()

    assert result["risk"] == 100  # capped at MAX_SCORE (20+30+40+20=110)
    assert result["level"] == "Critical"
    assert set(result["reasons"]) == {
        "Prompt Injection", "Tool Access", "Sensitive Data", "Email Access"
    }


@patch("risk.risk_engine.get_session")
def test_calculate_risk_no_factors_is_low(mock_get_session):
    fake_session = MagicMock()
    fake_record = {
        "has_prompt_injection": False,
        "has_tool_access": False,
        "has_sensitive_data": False,
        "has_email_access": False,
    }
    fake_session.run.return_value.single.return_value = fake_record
    mock_get_session.return_value.__enter__.return_value = fake_session

    result = risk_engine.calculate_risk()

    assert result["risk"] == 0
    assert result["level"] == "Low"
    assert result["reasons"] == []
