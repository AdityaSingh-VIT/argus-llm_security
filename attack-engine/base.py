"""
Common contract for every LangGraph agent node in the attack-engine.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from core.logging_config import get_logger

StateT = TypeVar("StateT")


class BaseAgent(ABC, Generic[StateT]):
    """Concrete agents (PlannerAgent today; PromptGeneratorAgent,
    ExecutionCoordinatorAgent, ResponseAnalyzerAgent, RiskScorerAgent, and
    MitigationGeneratorAgent once implemented) implement `__call__` as an
    async LangGraph node: it receives the shared WorkflowState and returns
    a state update.
    """

    name: str = "base_agent"

    def __init__(self) -> None:
        self._logger = get_logger(self.__class__.__module__)

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    @abstractmethod
    async def __call__(self, state: StateT) -> StateT:
        raise NotImplementedError
