"""
Ollama local provider adapter. No API key by default - Ollama typically
runs unauthenticated on localhost, but a custom base_url (e.g. behind a
reverse proxy) can still be supplied via ATTACK_ENGINE_EXECUTOR_OLLAMA_BASE_URL.
"""
from __future__ import annotations

from typing import Optional

import httpx

from executor.providers.base import ProviderResponse
from executor.providers.http_base import HttpProviderAdapter


class OllamaAdapter(HttpProviderAdapter):
    provider_name = "ollama"

    def __init__(self, base_url: str = "http://localhost:11434", client: Optional[httpx.AsyncClient] = None) -> None:
        super().__init__(base_url, client)

    async def generate(self, prompt: str, model: str, timeout_seconds: float) -> ProviderResponse:
        payload = {"model": model, "prompt": prompt, "stream": False}
        data = await self._post("/api/generate", json=payload, headers={}, timeout_seconds=timeout_seconds)
        return ProviderResponse(
            text=data.get("response", ""),
            raw=data,
            prompt_tokens=data.get("prompt_eval_count"),
            completion_tokens=data.get("eval_count"),
            total_tokens=(data.get("prompt_eval_count") or 0) + (data.get("eval_count") or 0) or None,
        )
