"""
Domain-level exceptions for the attack-engine.

Kept intentionally small and explicit so callers (LangGraph nodes, API
handlers) can catch precise failure modes instead of bare `Exception`.
"""
from __future__ import annotations


class AttackEngineError(Exception):
    """Base class for all attack-engine domain errors."""


class GraphRepositoryError(AttackEngineError):
    """Raised when the Digital Twin graph cannot be read from Neo4j."""


class PlannerError(AttackEngineError):
    """Raised for domain-level Attack Planner failures (as opposed to
    infrastructure failures, which surface as GraphRepositoryError)."""


class PromptGenerationError(AttackEngineError):
    """Raised for domain-level Prompt Generator failures."""


class ExecutorError(AttackEngineError):
    """Raised for domain-level Attack Executor failures (unknown/
    unconfigured provider, invalid batch, etc). Per-request provider
    failures are captured on ExecutionResult.error instead of raised,
    so one bad prompt never aborts a whole batch."""


class AnalysisError(AttackEngineError):
    """Raised for domain-level Response Analyzer failures."""


class RiskScoringError(AttackEngineError):
    """Raised for domain-level Risk Scorer failures."""
