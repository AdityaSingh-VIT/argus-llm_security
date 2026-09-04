"""
Unit tests for AttackExecutorAgent. No live network calls - a fake
ProviderAdapter stands in for a real provider, and the OpenAI/Anthropic/
Gemini/Ollama HTTP adapters are separately tested against a mocked
httpx transport in test_provider_adapters.py.
"""
from __future__ import annotations

import pytest

from core.config import AttackEngineSettings
from core.exceptions import ExecutorError
from executor.executor import AttackExecutorAgent
from executor.providers.base import ProviderResponse
from models.enums import AttackCategory, MutationStrategy, Severity
from models.execution_models import ExecutionStatus
from models.prompt_models import GeneratedPrompt


class _FakeAdapter:
    provider_name = "fake"

    def __init__(self, fail_on: set[str] | None = None) -> None:
        self.calls: list[str] = []
        self._fail_on = fail_on or set()

    async def generate(self, prompt: str, model: str, timeout_seconds: float) -> ProviderResponse:
        self.calls.append(prompt)
        if prompt in self._fail_on:
            raise ConnectionError("simulated provider outage")
        return ProviderResponse(text=f"Echo: {prompt[:20]}", prompt_tokens=10, completion_tokens=5, total_tokens=15)


def _prompt(content: str = "test prompt") -> GeneratedPrompt:
    return GeneratedPrompt(
        scenario_id="scenario-1",
        category=AttackCategory.PROMPT_INJECTION,
        title="test",
        content=content,
        mutation_strategy=MutationStrategy.IDENTITY,
        variant_index=0,
        expected_behavior="refuse",
        success_criteria="comply",
        severity=Severity.MEDIUM,
    )


def _settings(**overrides) -> AttackEngineSettings:
    base = {"executor_default_provider": "fake", "executor_default_model": "fake-model", "executor_max_retries": 1}
    base.update(overrides)
    return AttackEngineSettings(**base)


@pytest.mark.asyncio
async def test_execute_batch_records_success() -> None:
    adapter = _FakeAdapter()
    executor = AttackExecutorAgent(providers={"fake": adapter}, settings=_settings())

    results = await executor.execute_batch([_prompt("hello")])

    assert len(results) == 1
    assert results[0].status == ExecutionStatus.SUCCESS
    assert results[0].response_text.startswith("Echo:")
    assert results[0].total_tokens == 15
    assert results[0].request_id


@pytest.mark.asyncio
async def test_execute_batch_records_error_without_raising() -> None:
    adapter = _FakeAdapter(fail_on={"bad prompt"})
    executor = AttackExecutorAgent(providers={"fake": adapter}, settings=_settings())

    results = await executor.execute_batch([_prompt("bad prompt")])

    assert len(results) == 1
    assert results[0].status == ExecutionStatus.ERROR
    assert results[0].error is not None


@pytest.mark.asyncio
async def test_execute_batch_unknown_provider_raises() -> None:
    executor = AttackExecutorAgent(providers={}, settings=_settings())
    with pytest.raises(ExecutorError):
        await executor.execute_batch([_prompt()])


@pytest.mark.asyncio
async def test_execute_batch_one_failure_does_not_abort_others() -> None:
    adapter = _FakeAdapter(fail_on={"fails"})
    executor = AttackExecutorAgent(providers={"fake": adapter}, settings=_settings())

    results = await executor.execute_batch([_prompt("ok-1"), _prompt("fails"), _prompt("ok-2")])

    statuses = {r.status for r in results}
    assert statuses == {ExecutionStatus.SUCCESS, ExecutionStatus.ERROR}
    assert len(results) == 3


@pytest.mark.asyncio
async def test_call_as_langgraph_node_populates_state() -> None:
    adapter = _FakeAdapter()
    executor = AttackExecutorAgent(providers={"fake": adapter}, settings=_settings())
    state = {"candidate_prompts": [_prompt()], "errors": []}

    result = await executor(state)

    assert len(result["execution_results"]) == 1
    assert result["errors"] == []
