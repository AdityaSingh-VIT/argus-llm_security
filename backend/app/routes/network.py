"""
routes/network.py — Wireshark-Style Live Packet & Flow Inspector Endpoints.

Provides:
  - WebSocket streaming endpoint for low-latency packet flow dispatch
  - Live capture start / stop / interface selection
  - Safe attack & benign traffic simulation
  - PCAP trace analysis ingestion
  - Real-time network throughput and anomaly stats
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, status
from pydantic import BaseModel

from services.packet_inspector import capture_engine

logger = logging.getLogger("argus.network")
router = APIRouter()


class CaptureStartRequest(BaseModel):
    interface: str = "default"
    bpf_filter: str = "ip or ip6"


class SimulationRequest(BaseModel):
    scenario: str = "port_scan" # 'port_scan', 'syn_flood', 'brute_force', 'dns_tunnel', 'benign'


# WebSocket Active Client Manager
class PacketStreamManager:
    def __init__(self):
        self.active_sockets: List[WebSocket] = []
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def set_loop(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active_sockets.append(ws)
        # Send initial capture state & recent buffered packets
        stats = capture_engine.get_stats()
        await ws.send_json({
            "type": "INITIAL_STATE",
            "stats": stats,
            "recent_packets": capture_engine.packet_buffer[-100:]
        })

    def disconnect(self, ws: WebSocket):
        if ws in self.active_sockets:
            self.active_sockets.remove(ws)

    def broadcast(self, message: Dict[str, Any]):
        """Thread-safe broadcast helper for background sniffer and simulator threads."""
        if not self.active_sockets:
            return
        if self._loop and not self._loop.is_closed():
            asyncio.run_coroutine_threadsafe(self._broadcast_coro(message), self._loop)

    async def _broadcast_coro(self, message: Dict[str, Any]):
        dead = []
        for ws in self.active_sockets:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


stream_manager = PacketStreamManager()

# Hook the engine's packet emission into the WebSocket broadcast manager
capture_engine.broadcast_callback = stream_manager.broadcast


@router.websocket("/ws")
async def websocket_packet_stream(websocket: WebSocket):
    """Real-time bi-directional packet stream for Wireshark inspector."""
    stream_manager.set_loop(asyncio.get_event_loop())
    await stream_manager.connect(websocket)
    try:
        while True:
            # Listen for client command messages (e.g. pause, clear, simulate)
            data = await websocket.receive_json()
            action = data.get("action")
            if action == "pause":
                capture_engine.is_paused = True
            elif action == "resume":
                capture_engine.is_paused = False
            elif action == "clear":
                capture_engine.clear_buffer()
                await websocket.send_json({"type": "BUFFER_CLEARED"})
            elif action == "simulate":
                scenario = data.get("scenario", "port_scan")
                capture_engine.simulate_attack(scenario)
    except WebSocketDisconnect:
        stream_manager.disconnect(websocket)
    except Exception as exc:
        logger.warning("WebSocket stream error: %s", exc)
        stream_manager.disconnect(websocket)


@router.get("/interfaces", summary="List host network adapters")
async def get_network_interfaces():
    """Returns detected system network interfaces for capture selection."""
    return {
        "interfaces": capture_engine.get_interfaces(),
        "active_interface": capture_engine.interface,
        "is_capturing": capture_engine.is_capturing
    }


@router.post("/capture/start", summary="Start live packet capture")
async def start_packet_capture(body: CaptureStartRequest):
    """Starts live packet capture or synthetic traffic generation on interface."""
    capture_engine.start_capture(interface=body.interface, bpf_filter=body.bpf_filter)
    stream_manager.broadcast({
        "type": "CAPTURE_STATE",
        "is_capturing": True,
        "interface": body.interface,
        "filter": body.bpf_filter
    })
    return {
        "status": "started",
        "interface": body.interface,
        "filter": body.bpf_filter
    }


@router.post("/capture/stop", summary="Stop live packet capture")
async def stop_packet_capture():
    """Stops active sniffer thread."""
    capture_engine.stop_capture()
    stream_manager.broadcast({
        "type": "CAPTURE_STATE",
        "is_capturing": False
    })
    return {"status": "stopped"}


@router.post("/capture/clear", summary="Clear packet stream buffer")
async def clear_packet_buffer():
    """Clears buffered packets in memory."""
    capture_engine.clear_buffer()
    stream_manager.broadcast({"type": "BUFFER_CLEARED"})
    return {"status": "cleared"}


@router.post("/simulate", summary="Trigger safe lab simulation attack")
async def simulate_attack(body: SimulationRequest):
    """Safely injects synthetic attack or benign flows for verification."""
    capture_engine.simulate_attack(body.scenario)
    return {
        "status": "simulation_triggered",
        "scenario": body.scenario
    }


@router.get("/packets", summary="Get recent captured packets")
async def get_recent_packets(limit: int = 150):
    """Returns the most recent packets from the in-memory buffer."""
    return {
        "total": len(capture_engine.packet_buffer),
        "packets": capture_engine.packet_buffer[-limit:]
    }


@router.get("/stats", summary="Get real-time capture throughput statistics")
async def get_capture_stats():
    """Returns PPS, Bps, total volume, and anomaly counts."""
    return capture_engine.get_stats()
