"""
Shared base for HTTP-based provider adapters (OpenAI, Anthropic, Gemini,
Ollama). Each adapter owns its own request/response shape but shares
client lifecycle handling. The httpx.AsyncClient is injectable so tests
can substitute a mock transport instead of making real network calls.
"""
from __future__ import annotations

from typing import Optional

import httpx


class HttpProviderAdapter:
    def __init__(self, base_url: str, client: Optional[httpx.AsyncClient] = None) -> None:
        self._base_url = base_url.rstrip("/")
        self._client = client or httpx.AsyncClient(base_url=self._base_url)

    async def _post(self, path: str, *, json: dict, headers: dict, timeout_seconds: float) -> dict:
        response = await self._client.post(path, json=json, headers=headers, timeout=timeout_seconds)
        response.raise_for_status()
        return response.json()

    async def close(self) -> None:
        await self._client.aclose()
