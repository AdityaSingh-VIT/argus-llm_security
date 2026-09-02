"""
main.py — Argus Backend API Gateway & Real-Time Security Operations Center

Integration layer connecting:
  - Frontend (React @ port 3000 / 5173)
  - Network Inspector (Live Packet Sniffer & Wireshark-Style Stream)
  - Attack Engine service (@ port 7002) [MOCK_SERVICES=true by default]
  - Digital Twin service (@ port 7001) [MOCK_SERVICES=true by default]
  - Chatbot service (@ port 7003) [MOCK_SERVICES=true by default]
  - PostgreSQL / SQLite database

Run locally:    uvicorn main:app --reload --port 8000
Docs UI:        http://localhost:8000/docs
"""

import logging
import os
import asyncio
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("argus.backend")

MOCK_SERVICES = os.getenv("MOCK_SERVICES", "true").lower() == "true"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Argus backend starting up...")
    logger.info("Mock services: %s", MOCK_SERVICES)
    try:
        from database.connection import init_db
        await init_db()
        logger.info("Database initialized.")
    except Exception as exc:
        logger.warning("DB init warning (non-fatal): %s", exc)

    # Initialize network stream loop
    try:
        from routes.network import stream_manager
        stream_manager.set_loop(asyncio.get_event_loop())
    except Exception as exc:
        logger.warning("Stream manager loop setup warning: %s", exc)

    yield

    logger.info("Argus backend shutting down...")
    try:
        from services.packet_inspector import capture_engine
        capture_engine.stop_capture()
    except Exception:
        pass


app = FastAPI(
    title="Argus Backend API Gateway & Live Network Inspector",
    description=(
        "Unified backend for Argus: authentication, scan orchestration, "
        "attack history, PDF reports, dashboard aggregation, "
        "digital twin graph proxy, and Wireshark-grade live network packet inspection.\n\n"
        f"**Mock services active:** {MOCK_SERVICES} — "
        "set MOCK_SERVICES=false to use real microservices."
    ),
    version="1.1.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# ── Routers ───────────────────────────────────────────────────────────────────
from routes import login, scan, history, report, dashboard, graph, network  # noqa: E402

app.include_router(login.router,     prefix="/auth",      tags=["Auth"])
app.include_router(scan.router,      prefix="/scan",      tags=["Scan"])
app.include_router(history.router,   prefix="/history",   tags=["History"])
app.include_router(report.router,    prefix="/report",    tags=["Report"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(graph.router,     prefix="/graph",     tags=["Graph / Digital Twin"])
app.include_router(network.router,   prefix="/network",   tags=["Network Inspector"])


@app.get("/", tags=["Health"])
async def health():
    """Health-check endpoint used by Docker Compose and UI health monitors."""
    return {
        "status": "ok",
        "service": "argus-backend",
        "version": "1.1.0",
        "mock_services": MOCK_SERVICES,
    }
