"""
neo4jk/connection.py validates env vars at import time (fail fast in
real usage). For tests -- which mock every actual DB call -- we just
need those vars to exist so the import doesn't blow up before mocking
even gets a chance to run.
"""

import os

os.environ.setdefault("NEO4J_URI", "bolt://localhost:7687")
os.environ.setdefault("NEO4J_USERNAME", "neo4j")
os.environ.setdefault("NEO4J_PASSWORD", "test-password")
