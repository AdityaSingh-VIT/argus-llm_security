import pytest
from httpx import AsyncClient, ASGITransport
import sys
import os

sys.path.insert(0, os.path.abspath("D:/Study/capstone/backend/app"))
from main import app


@pytest.mark.asyncio
async def test_network_interfaces():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/network/interfaces")
        assert resp.status_code == 200
        data = resp.json()
        assert "interfaces" in data
        assert len(data["interfaces"]) > 0


@pytest.mark.asyncio
async def test_network_simulation_and_packets():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Trigger safe port scan simulation
        resp = await client.post("/network/simulate", json={"scenario": "port_scan"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "simulation_triggered"

        import asyncio
        await asyncio.sleep(0.4)
        resp = await client.get("/network/packets?limit=50")
        assert resp.status_code == 200
        data = resp.json()
        assert "packets" in data
        assert len(data["packets"]) > 0

        first_pkt = data["packets"][0]
        assert "src" in first_pkt
        assert "dst" in first_pkt
        assert "proto" in first_pkt
        assert "flags" in first_pkt
        assert "verdict" in first_pkt
        assert "hex_dump" in first_pkt
        assert len(first_pkt["hex_dump"]) > 10

        # Check stats
        resp = await client.get("/network/stats")
        assert resp.status_code == 200
        stats = resp.json()
        assert stats["total_packets"] > 0
