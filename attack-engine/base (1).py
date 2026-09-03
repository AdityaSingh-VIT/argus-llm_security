"""
Provider adapter abstraction the Attack Executor depends on (Dependency
Inversion) so it never talks to a specific vendor SDK/HTTP API directly.
New providers are added by implementing this protocol - the Executor
itself never needs to change.
"""
from __future__ import annotations

from typing import Optional, Protocol, runtime_checkable

from pydantic import BaseModel, Field


class ProviderResponse(BaseModel):
    text: str
    raw: dict = Field(default_factory=dict)
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


@runtime_checkable
class ProviderAdapter(Protocol):
    provider_name: str

    async def generate(self, prompt: str, model: str, timeout_seconds: float) -> ProviderResponse:
        ...
