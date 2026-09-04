"""
Builds the default provider registry from AttackEngineSettings.

A provider is only registered if its credentials/config are present -
this keeps unconfigured providers cleanly absent from the registry
instead of present-but-broken, and the Executor already handles an
unregistered provider name as a clear ExecutorError.
"""
from __future__ import annotations

from core.config import AttackEngineSettings
from executor.providers.anthropic_adapter import AnthropicAdapter
from executor.providers.base import ProviderAdapter
from executor.providers.gemini_adapter import GeminiAdapter
from executor.providers.huggingface_adapter import HuggingFaceLocalAdapter
from executor.providers.ollama_adapter import OllamaAdapter
from executor.providers.openai_adapter import OpenAIAdapter


def build_default_registry(settings: AttackEngineSettings) -> dict[str, ProviderAdapter]:
    registry: dict[str, ProviderAdapter] = {}

    if settings.executor_openai_api_key:
        registry["openai"] = OpenAIAdapter(api_key=settings.executor_openai_api_key)
    if settings.executor_anthropic_api_key:
        registry["anthropic"] = AnthropicAdapter(api_key=settings.executor_anthropic_api_key)
    if settings.executor_gemini_api_key:
        registry["gemini"] = GeminiAdapter(api_key=settings.executor_gemini_api_key)

    # Ollama and the local HuggingFace adapter need no API key, so they are
    # always registered; they simply fail per-request if unreachable.
    registry["ollama"] = OllamaAdapter(base_url=settings.executor_ollama_base_url)
    registry["huggingface_local"] = HuggingFaceLocalAdapter(default_model=settings.executor_huggingface_default_model)

    return registry
