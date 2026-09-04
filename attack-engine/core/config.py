"""
Centralized, typed configuration for the attack-engine service.

All settings are environment-driven (12-factor style) via pydantic-settings,
prefixed with ATTACK_ENGINE_ to avoid collisions with the other services
(backend/, digital-twin/, chatbot/) that may share a Docker network / .env.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AttackEngineSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ATTACK_ENGINE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Neo4j (Digital Twin graph - read-only from this service) ---
    neo4j_uri: str = Field(default="bolt://localhost:7687")
    neo4j_user: str = Field(default="neo4j")
    neo4j_password: str = Field(default="neo4j")
    neo4j_database: str = Field(default="neo4j")

    # --- Attack Planner tuning ---
    planner_max_path_depth: int = Field(default=6, ge=1, le=15)
    planner_max_paths: int = Field(default=500, ge=1, le=5000)
    planner_max_scenarios_per_scan: int = Field(default=25, ge=1, le=500)
    planner_min_confidence: float = Field(default=0.3, ge=0.0, le=1.0)

    # --- Prompt Generator ---
    generator_variants_per_strategy: int = Field(default=1, ge=1, le=5)

    # --- Attack Executor ---
    # API keys are read from the environment only - never hardcoded, never
    # given a non-empty default. A missing key simply means that provider
    # is not registered (see executor/providers/registry.py).
    executor_openai_api_key: Optional[str] = Field(default=None)
    executor_anthropic_api_key: Optional[str] = Field(default=None)
    executor_gemini_api_key: Optional[str] = Field(default=None)
    executor_ollama_base_url: str = Field(default="http://localhost:11434")
    executor_huggingface_default_model: Optional[str] = Field(default=None)
    executor_default_provider: str = Field(default="ollama")
    executor_default_model: str = Field(default="llama3")
    executor_timeout_seconds: float = Field(default=30.0, ge=1.0, le=300.0)
    executor_max_retries: int = Field(default=3, ge=1, le=10)
    executor_max_concurrency: int = Field(default=5, ge=1, le=100)

    # --- Response Analyzer ---
    analyzer_enable_llm_judge: bool = Field(default=False)

    # --- Risk Scorer (configurable weighting; need not sum to 1 - they are
    # normalized against their own total at scoring time) ---
    risk_weight_severity: float = Field(default=0.35, ge=0.0)
    risk_weight_confidence: float = Field(default=0.25, ge=0.0)
    risk_weight_exploitability: float = Field(default=0.20, ge=0.0)
    risk_weight_business_impact: float = Field(default=0.20, ge=0.0)

    # --- Observability ---
    log_level: str = Field(default="INFO")
    environment: str = Field(default="development")
    debug: bool = Field(default=False)


@lru_cache(maxsize=1)
def get_settings() -> AttackEngineSettings:
    """Cached settings accessor - avoids re-parsing the environment on
    every DI resolution while still remaining test-friendly
    (get_settings.cache_clear() before overriding env vars in tests)."""
    return AttackEngineSettings()
