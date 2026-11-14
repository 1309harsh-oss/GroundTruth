"""
Vercel serverless entrypoint for the GroundTruth FastAPI backend.
Vercel looks for `api/index.py` and exports the ASGI `app` object.
"""
import sys
import os
from pathlib import Path

# Put the repo root on sys.path so `apps.api.app.main` resolves correctly
root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

# Vercel sets VERCEL=1; use /tmp for writable storage and SQLite
if os.getenv("VERCEL"):
    # Ensure SQLite lives in /tmp (writable) instead of ./data (read-only on Vercel)
    if not os.getenv("DATABASE_URL"):
        os.environ.setdefault("DATABASE_URL", "sqlite:////tmp/groundtruth.db")
    # Ensure uploaded files land in /tmp/storage
    os.environ.setdefault("STORAGE_LOCAL_ROOT", "/tmp/storage")

from apps.api.app.main import app  # noqa: E402  – must come after sys.path fixup
