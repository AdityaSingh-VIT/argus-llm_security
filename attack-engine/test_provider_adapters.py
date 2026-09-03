"""
Unit tests for the REST-based provider adapters (OpenAI, Anthropic,
Gemini, Ollama). Every test injects an httpx.AsyncClient built on
httpx.MockTransport, so no real network call is ever made.
"""
from __future__ import annotations

import json

import httpx
import pytest

from executor.providers.anthropic_adapter import AnthropicAdapter
from executor.providers.gemini_adapter import GeminiAdapter
from executor.providers.ollama_adapter import OllamaAdapter
from executor.providers.openai_adapter import OpenAIAdapter


def _mock_client(base_url: str, json_response: dict) -> httpx.AsyncClient:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=json_response)

    return httpx.AsyncClient(base_url=base_url, transport=httpx.MockTransport(handler))


@pytest.mark.asyncio
async def test_openai_adapter_parses_response() -> None:
    client = _mock_client(
        "https://api.openai.com/v1",
        {"choices": [{"message": {"content": "hello from openai"}}], "usage": {"prompt_tokens": 3, "completion_tokens": 2, "total_tokens": 5}},
    )
    adapter = OpenAIAdapter(api_key="test-key", client=client)

    response = await adapter.generate("hi", "gpt-4o", timeout_seconds=5)

    assert response.text == "hello from openai"
    assert response.total_tokens == 5
    await adapter.close()


@pytest.mark.asyncio
async def test_anthropic_adapter_parses_response() -> None:
    client = _mock_client(
        "https://api.anthropic.com/v1",
        {"content": [{"type": "text", "text": "hello from claude"}], "usage": {"input_tokens": 4, "output_tokens": 3}},
    )
    adapter = AnthropicAdapter(api_key="test-key", client=client)

    response = await adapter.generate("hi", "claude-sonnet", timeout_seconds=5)

    assert response.text == "hello from claude"
    assert response.total_tokens == 7
    await adapter.close()


@pytest.mark.asyncio
async def test_gemini_adapter_parses_response() -> None:
    client = _mock_client(
        "https://generativelanguage.googleapis.com/v1beta",
        {"candidates": [{"content": {"parts": [{"text": "hello from gemini"}]}}], "usageMetadata": {"promptTokenCount": 2, "candidatesTokenCount": 3, "totalTokenCount": 5}},
    )
    adapter = GeminiAdapter(api_key="test-key", client=client)

    response = await adapter.generate("hi", "gemini-pro", timeout_seconds=5)

    assert response.text == "hello from gemini"
    assert response.total_tokens == 5
    await adapter.close()


@pytest.mark.asyncio
async def test_ollama_adapter_parses_response() -> None:
    client = _mock_client("http://localhost:11434", {"response": "hello from llama", "prompt_eval_count": 5, "eval_count": 4})
    adapter = OllamaAdapter(client=client)

    response = await adapter.generate("hi", "llama3", timeout_seconds=5)

    assert response.text == "hello from llama"
    assert response.total_tokens == 9
    await adapter.close()


@pytest.mark.asyncio
async def test_openai_adapter_never_leaks_api_key_in_response_model() -> None:
    client = _mock_client(
        "https://api.openai.com/v1", {"choices": [{"message": {"content": "ok"}}], "usage": {}}
    )
    adapter = OpenAIAdapter(api_key="super-secret-key", client=client)

    response = await adapter.generate("hi", "gpt-4o", timeout_seconds=5)

    assert "super-secret-key" not in json.dumps(response.model_dump(mode="json"))
    await adapter.close()
