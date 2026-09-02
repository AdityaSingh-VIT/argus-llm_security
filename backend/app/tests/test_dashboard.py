"""tests/test_dashboard.py — Dashboard endpoint tests."""

import pytest
from unittest.mock import patch, AsyncMock


async def _get_token(client) -> str:
    r = await client.post("/auth/register", json={"username": "dashuser", "password": "pw"})
    return r.json()["access_token"]


@pytest.mark.asyncio
async def test_dashboard_returns_stats(client):
    token = await _get_token(client)
    with patch("routes.dashboard.graph_engine.get_graph", new_callable=AsyncMock) as mg, \
         patch("routes.dashboard.graph_engine.get_risk",  new_callable=AsyncMock) as mr:
        mg.return_value = {"nodes": [], "edges": []}
        mr.return_value = {"breakdown": {}}
        r = await client.get("/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert "total_scans" in data
    assert "total_attacks" in data
    assert "avg_risk_score" in data
