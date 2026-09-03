"""
Structured-ish logging setup for the attack-engine.

Deliberately built on the standard library `logging` module (no extra
dependency such as structlog) to keep the Attack Planner's dependency
footprint minimal. Call sites pass structured context via `extra={...}`;
the formatter renders it inline for local/dev readability. Swapping the
formatter for a JSON formatter in production does not require touching
any call site.
"""
from __future__ import annotations

import logging
import sys
from functools import lru_cache

_CONFIGURED = False
_RESERVED_RECORD_KEYS = set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__.keys()) | {
    "message",
    "asctime",
}


class _ContextFormatter(logging.Formatter):
    """Formatter that appends any `extra=` fields passed to a log call."""

    def format(self, record: logging.LogRecord) -> str:
        base = super().format(record)
        extras = {k: v for k, v in record.__dict__.items() if k not in _RESERVED_RECORD_KEYS}
        if extras:
            base = f"{base} | {extras}"
        return base


def configure_logging(level: str = "INFO") -> None:
    """Idempotently configure the root logger. Safe to call multiple times
    (e.g. once per module import) - only the first call takes effect."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(_ContextFormatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))

    root = logging.getLogger()
    root.setLevel(level.upper())
    root.handlers = [handler]
    _CONFIGURED = True


@lru_cache(maxsize=None)
def get_logger(name: str) -> logging.Logger:
    """Return a module-scoped logger, configuring logging on first use."""
    configure_logging()
    return logging.getLogger(name)
