"""
neo4jk/connection.py

Owns the single Neo4j driver instance for the whole app.

FIXES vs. original:
- Validates env vars are present at import time instead of failing
  cryptically on first query.
- Verifies connectivity on startup (fail fast, not on the first request).
- Exposes a context-managed session helper so callers never forget to
  close a session.
- Exposes get_driver()/close_driver() so main.py can manage lifecycle
  cleanly (open once at startup, close once at shutdown) instead of every
  module opening its own driver.
"""

import os
import logging
from contextlib import contextmanager

from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("digital_twin.neo4j")

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

_REQUIRED = {"NEO4J_URI": URI, "NEO4J_USERNAME": USERNAME, "NEO4J_PASSWORD": PASSWORD}
_missing = [name for name, val in _REQUIRED.items() if not val]
if _missing:
    raise EnvironmentError(
        f"Missing required environment variables: {', '.join(_missing)}. "
        f"Copy .env.example to .env and fill these in."
    )

_driver = None


def get_driver():
    """Return a lazily-created, process-wide singleton driver."""
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))
        try:
            _driver.verify_connectivity()
            logger.info("Connected to Neo4j at %s", URI)
        except Exception:
            _driver = None
            raise
    return _driver


def close_driver():
    """Call once, on app shutdown."""
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None
        logger.info("Neo4j driver closed")


@contextmanager
def get_session():
    """
    Usage:
        with get_session() as session:
            session.run(...)
    Guarantees the session is closed even if the query raises.
    """
    driver = get_driver()
    session = driver.session()
    try:
        yield session
    finally:
        session.close()
if __name__ == "__main__":

    try:
        driver = get_driver()

        with driver.session() as session:
            result = session.run("RETURN 1 AS test")
            print(result.single()["test"])

        print("Neo4j connection successful")

    except Exception as e:
        print("Neo4j connection failed:")
        print(e)

    finally:
        close_driver()