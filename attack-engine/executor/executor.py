"""
Attack Executor agent.

Sends GeneratedPrompt objects to a configured LLM provider via a
pluggable ProviderAdapter (OpenAI, Anthropic, Gemini, Ollama, or a local
HuggingFace model - see executor.providers), recording a structured
ExecutionResult for every call: response, latency, token usage, and
errors. Concurrency-limited (rate limiting), retried on transient
failures, and never logs or echoes API keys.

This module fills in what was previously an empty stub
(attack-engine/executor/executor.py).
"""
from __future__ import annotations

import asyncio
import time
import uuid
from typing import Optional

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from agents.base import BaseAgent
from core.config import AttackEngineSettings, get_settings
from core.exceptions import ExecutorError
from executor.providers.base import ProviderAdapter
from executor.providers.registry import build_default_registry
from graph.state import WorkflowState
from models.execution_models import ExecutionResult, ExecutionStatus
from models.prompt_models import GeneratedPrompt

# Only transient/networking failures are retried - a 4xx from a provider
# (bad request, invalid model) is a real ExecutionResult.error, not
# something a retry can fix.
_RETRYABLE_EXCEPTIONS = (TimeoutError, ConnectionError, asyncio.TimeoutError)


class AttackExecutorAgent(BaseAgent[WorkflowState]):
    """LangGraph node + standalone service for prompt execution.

    Named `execution_coordinator` to match the stage name used in the
    original project spec's LangGraph workflow diagram, even though the
    implementing file is executor/executor.py per the existing folder
    layout.
    """

    name = "execution_coordinator"

    def __init__(
        self,
        providers: Optional[dict[str, ProviderAdapter]] = None,
        settings: Optional[AttackEngineSettings] = None,
    ) -> None:
        super().__init__()
        self._settings = settings or get_settings()
        self._providers = providers if providers is not None else build_default_registry(self._settings)

    # ------------------------------------------------------------------
    # Public service API
    # ------------------------------------------------------------------
    async def execute_batch(
        self,
        prompts: list[GeneratedPrompt],
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> list[ExecutionResult]:
        provider_name = provider or self._settings.executor_default_provider
        model_name = model or self._settings.executor_default_model
        adapter = self._providers.get(provider_name)
        if adapter is None:
            raise ExecutorError(
                f"Unknown or unconfigured provider '{provider_name}'. "
                f"Configured providers: {sorted(self._providers)}"
            )

        # Rate limiting / batching: bound concurrent in-flight requests
        # rather than firing every prompt at once.
        semaphore = asyncio.Semaphore(self._settings.executor_max_concurrency)

        async def _run(prompt: GeneratedPrompt) -> ExecutionResult:
            async with semaphore:
                return await self._execute_one(adapter, provider_name, model_name, prompt)

        self.logger.info(
            "execution_batch_started",
            extra={"prompt_count": len(prompts), "provider": provider_name, "model": model_name},
        )
        results = await asyncio.gather(*(_run(p) for p in prompts))
        self.logger.info("execution_batch_completed", extra={"result_count": len(results)})
        return list(results)

    async def _execute_one(
        self, adapter: ProviderAdapter, provider_name: str, model_name: str, prompt: GeneratedPrompt
    ) -> ExecutionResult:
        request_id = str(uuid.uuid4())
        started = time.perf_counter()
        timeout = self._settings.executor_timeout_seconds

        @retry(
            reraise=True,
            stop=stop_after_attempt(self._settings.executor_max_retries),
            wait=wait_exponential(multiplier=0.5, min=0.5, max=8),
            retry=retry_if_exception_type(_RETRYABLE_EXCEPTIONS),
        )
        async def _call():
            return await asyncio.wait_for(adapter.generate(prompt.content, model_name, timeout), timeout=timeout)

        try:
            response = await _call()
            latency_ms = (time.perf_counter() - started) * 1000
            return ExecutionResult(
                prompt_id=prompt.id,
                scenario_id=prompt.scenario_id,
                provider=provider_name,
                model=model_name,
                request_id=request_id,
                response_text=response.text,
                latency_ms=latency_ms,
                prompt_tokens=response.prompt_tokens,
                completion_tokens=response.completion_tokens,
                total_tokens=response.total_tokens,
                status=ExecutionStatus.SUCCESS,
            )
        except Exception as exc:
            # A single prompt's failure (timeout, provider error, rate
            # limit) is recorded on its own ExecutionResult, never raised -
            # one bad request must not abort the rest of the batch.
            latency_ms = (time.perf_counter() - started) * 1000
            self.logger.error(
                "execution_failed",
                extra={"prompt_id": prompt.id, "provider": provider_name, "request_id": request_id, "error": str(exc)},
            )
            return ExecutionResult(
                prompt_id=prompt.id,
                scenario_id=prompt.scenario_id,
                provider=provider_name,
                model=model_name,
                request_id=request_id,
                response_text="",
                latency_ms=latency_ms,
                status=ExecutionStatus.ERROR,
                error=str(exc),
            )

    # ------------------------------------------------------------------
    # LangGraph node adapter
    # ------------------------------------------------------------------
    async def __call__(self, state: WorkflowState) -> WorkflowState:
        prompts = state.get("candidate_prompts", []) or []
        errors = list(state.get("errors", []))
        try:
            results = await self.execute_batch(prompts)
            return {**state, "execution_results": results, "errors": errors}
        except ExecutorError as exc:
            self.logger.error("executor_node_failed", extra={"error": str(exc)})
            errors.append(f"[{self.name}] {exc}")
            return {**state, "execution_results": [], "errors": errors}
