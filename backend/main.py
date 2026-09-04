"""
Root entry point for Argus backend to allow running:
    uvicorn main:app --reload --port 8000
from inside the backend/ folder.
"""
import sys
import os

# Ensure the 'app' folder is on sys.path so 'routes', 'database', etc. import cleanly
app_dir = os.path.join(os.path.dirname(__file__), "app")
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from app.main import app  # noqa: F401, E402
