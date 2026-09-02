"""
services/attack_engine.py — Attack Engine service client.

MOCK MODE (default while attack-engine team hasn't uploaded yet):
    Set  MOCK_SERVICES=true  in .env  → uses realistic mock data, no HTTP calls.

REAL MODE (when attack-engine service is running):
    Set  MOCK_SERVICES=false  and  ATTACK_ENGINE_URL=http://attack-engine:7002
    No code changes needed.

Attack Engine API contract (for when it's ready):
    POST /generate   body: { "context": str, "n": int }
                     resp: { "prompts": [str, ...] }

    POST /execute    body: { "target_url": str, "prompt": str }
                     resp: { "response": str, "score": float, "category": str }
"""

import logging
import os
import random
from dataclasses import dataclass
from typing import List

import httpx
from dotenv import load_dotenv

load_dotenv()

MOCK_SERVICES: bool = os.getenv("MOCK_SERVICES", "true").lower() == "true"
ATTACK_ENGINE_URL: str = os.getenv("ATTACK_ENGINE_URL", "http://attack-engine:7002")
TIMEOUT = httpx.Timeout(60.0)
logger = logging.getLogger("argus.services.attack_engine")


@dataclass
class AttackResult:
    prompt: str
    response: str
    score: float
    category: str


# ── Mock Implementation ───────────────────────────────────────────────────────

async def _mock_generate_attacks(context: str, n: int) -> List[str]:
    from services.mock_data import MOCK_ATTACK_PROMPTS
    logger.info("[MOCK] Generating %d attack prompts for context: %.60s", n, context)
    prompts = MOCK_ATTACK_PROMPTS[:n]
    # Pad with variations if n > available mocks
    while len(prompts) < n:
        prompts.append(f"[Generated prompt #{len(prompts)+1}] {context} — override safety filters.")
    return prompts


async def _mock_execute_attack(target_url: str, prompt: str) -> AttackResult:
    from services.mock_data import mock_execute_attack
    logger.info("[MOCK] Executing attack against %s", target_url)
    result = mock_execute_attack(prompt)
    return AttackResult(**result)


# ── Real Implementation ───────────────────────────────────────────────────────

async def _real_generate_attacks(context: str, n: int) -> List[str]:
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.post(
            f"{ATTACK_ENGINE_URL}/generate",
            json={"context": context, "n": n},
        )
        resp.raise_for_status()
        return resp.json().get("prompts", [])


async def _real_execute_attack(target_url: str, prompt: str) -> AttackResult:
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.post(
            f"{ATTACK_ENGINE_URL}/execute",
            json={"target_url": target_url, "prompt": prompt},
        )
        resp.raise_for_status()
        data = resp.json()
        return AttackResult(
            prompt=prompt,
            response=data.get("response", ""),
            score=float(data.get("score", 0.0)),
            category=data.get("category", "Unknown"),
        )


# ── Public API (auto-selects mock vs real) ────────────────────────────────────

async def generate_attacks(context: str, n: int = 5) -> List[str]:
    """Generate n attack prompts. Uses mock or real service based on MOCK_SERVICES."""
    if MOCK_SERVICES:
        return await _mock_generate_attacks(context, n)
    try:
        return await _real_generate_attacks(context, n)
    except httpx.HTTPError as exc:
        logger.warning("Attack engine unreachable, falling back to mock: %s", exc)
        return await _mock_generate_attacks(context, n)


async def execute_attack(target_url: str, prompt: str) -> AttackResult:
    """Execute one attack prompt. Uses mock or real service based on MOCK_SERVICES."""
    if MOCK_SERVICES:
        return await _mock_execute_attack(target_url, prompt)
    try:
        return await _real_execute_attack(target_url, prompt)
    except httpx.HTTPError as exc:
        logger.warning("Attack engine execution failed, falling back to mock: %s", exc)
        return await _mock_execute_attack(target_url, prompt)
