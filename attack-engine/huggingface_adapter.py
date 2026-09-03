"""
Local HuggingFace `transformers` provider adapter.

`transformers` (and torch) are optional, heavy dependencies deliberately
NOT listed in requirements.txt as hard requirements - they are imported
lazily on first use so the rest of the executor (and the whole
attack-engine) works without them installed. Install with:
    pip install transformers torch
"""
from __future__ import annotations

import asyncio
from typing import Any, Optional

from executor.providers.base import ProviderResponse
from core.logging_config import get_logger

logger = get_logger(__name__)


class HuggingFaceLocalAdapter:
    provider_name = "huggingface_local"

    def __init__(self, default_model: Optional[str] = None) -> None:
        self._default_model = default_model
        self._pipelines: dict[str, Any] = {}

    def _get_pipeline(self, model: str):
        if model not in self._pipelines:
            try:
                from transformers import pipeline  # type: ignore
            except ImportError as exc:
                raise RuntimeError(
                    "The 'transformers' package is required for the huggingface_local "
                    "provider. Install it with: pip install transformers torch"
                ) from exc
            self._pipelines[model] = pipeline("text-generation", model=model)
        return self._pipelines[model]

    async def generate(self, prompt: str, model: str, timeout_seconds: float) -> ProviderResponse:
        target_model = model or self._default_model
        if not target_model:
            raise ValueError("No model specified for the huggingface_local provider")

        loop = asyncio.get_running_loop()
        pipe = await loop.run_in_executor(None, self._get_pipeline, target_model)
        result = await asyncio.wait_for(
            loop.run_in_executor(None, lambda: pipe(prompt, max_new_tokens=256, num_return_sequences=1)),
            timeout=timeout_seconds,
        )
        text = result[0]["generated_text"]
        return ProviderResponse(text=text, raw={"generated_text": text})
