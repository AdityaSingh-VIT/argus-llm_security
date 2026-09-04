"""
Google Gemini (generativelanguage) provider adapter.
"""
from __future__ import annotations

from typing import Optional

import httpx

from executor.providers.base import ProviderResponse
from executor.providers.http_base import HttpProviderAdapter


class GeminiAdapter(HttpProviderAdapter):
    provider_name = "gemini"

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://generativelanguage.googleapis.com/v1beta",
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        super().__init__(base_url, client)
        self._api_key = api_key

    async def generate(self, prompt: str, model: str, timeout_seconds: float) -> ProviderResponse:
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        path = f"/models/{model}:generateContent?key={self._api_key}"
        data = await self._post(path, json=payload, headers={"Content-Type": "application/json"}, timeout_seconds=timeout_seconds)

        text = ""
        candidates = data.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            text = "".join(part.get("text", "") for part in parts)

        usage = data.get("usageMetadata", {})
        return ProviderResponse(
            text=text,
            raw=data,
            prompt_tokens=usage.get("promptTokenCount"),
            completion_tokens=usage.get("candidatesTokenCount"),
            total_tokens=usage.get("totalTokenCount"),
        )
