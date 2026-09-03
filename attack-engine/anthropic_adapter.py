"""
Anthropic Messages API provider adapter.
"""
from __future__ import annotations

from typing import Optional

import httpx

from executor.providers.base import ProviderResponse
from executor.providers.http_base import HttpProviderAdapter


class AnthropicAdapter(HttpProviderAdapter):
    provider_name = "anthropic"

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.anthropic.com/v1",
        client: Optional[httpx.AsyncClient] = None,
        max_tokens: int = 1024,
    ) -> None:
        super().__init__(base_url, client)
        self._api_key = api_key
        self._max_tokens = max_tokens

    async def generate(self, prompt: str, model: str, timeout_seconds: float) -> ProviderResponse:
        payload = {
            "model": model,
            "max_tokens": self._max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        data = await self._post("/messages", json=payload, headers=headers, timeout_seconds=timeout_seconds)
        text = "".join(block.get("text", "") for block in data.get("content", []))
        usage = data.get("usage", {})
        input_tokens = usage.get("input_tokens")
        output_tokens = usage.get("output_tokens")
        total = (input_tokens or 0) + (output_tokens or 0)
        return ProviderResponse(
            text=text,
            raw=data,
            prompt_tokens=input_tokens,
            completion_tokens=output_tokens,
            total_tokens=total or None,
        )
