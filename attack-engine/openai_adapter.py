"""
OpenAI Chat Completions provider adapter.

The API key is passed in explicitly by the caller (see
executor.providers.registry), sourced from AttackEngineSettings, which in
turn reads it only from the environment - never hardcoded here.
"""
from __future__ import annotations

from typing import Optional

import httpx

from executor.providers.base import ProviderResponse
from executor.providers.http_base import HttpProviderAdapter


class OpenAIAdapter(HttpProviderAdapter):
    provider_name = "openai"

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        super().__init__(base_url, client)
        self._api_key = api_key

    async def generate(self, prompt: str, model: str, timeout_seconds: float) -> ProviderResponse:
        payload = {"model": model, "messages": [{"role": "user", "content": prompt}]}
        headers = {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}
        data = await self._post("/chat/completions", json=payload, headers=headers, timeout_seconds=timeout_seconds)
        text = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        return ProviderResponse(
            text=text,
            raw=data,
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
            total_tokens=usage.get("total_tokens"),
        )
