"""
services/chatbot.py — Chatbot service client.

MOCK MODE: returns canned chatbot responses.
REAL MODE: calls chatbot service at CHATBOT_URL.

Chatbot API contract (for when it's ready):
    POST /chat   body: { "message": str }
                 resp: { "response": str, "session_id": str }
"""

import logging
import os
from typing import Dict, Any

import httpx
from dotenv import load_dotenv

load_dotenv()

MOCK_SERVICES: bool = os.getenv("MOCK_SERVICES", "true").lower() == "true"
CHATBOT_URL: str = os.getenv("CHATBOT_URL", "http://chatbot:7003")
TIMEOUT = httpx.Timeout(30.0)
logger = logging.getLogger("argus.services.chatbot")


async def send_message(message: str) -> Dict[str, Any]:
    """Send a message to the chatbot and get a response."""
    if MOCK_SERVICES:
        from services.mock_data import mock_chatbot_response
        logger.info("[MOCK] Chatbot responding to: %.60s", message)
        return {
            "response": mock_chatbot_response(message),
            "session_id": "mock-session-001",
        }
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.post(f"{CHATBOT_URL}/chat", json={"message": message})
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPError as exc:
        logger.warning("Chatbot unreachable, falling back to mock: %s", exc)
        from services.mock_data import mock_chatbot_response
        return {"response": mock_chatbot_response(message), "session_id": "fallback-session"}
