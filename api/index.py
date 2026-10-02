"""Vercel serverless entry point.

Vercel serves the built React app from `frontend/dist` and routes `/api/*`,
`/docs` and `/openapi.json` to this function, which exposes the FastAPI app.
"""

import os
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND))

# Vercel's Neon/Postgres integration exposes POSTGRES_URL; fall back to an
# ephemeral SQLite file in /tmp (the only writable path) for demo deploys.
if not os.environ.get("DATABASE_URL"):
    os.environ["DATABASE_URL"] = os.environ.get("POSTGRES_URL") or "sqlite:////tmp/qa_platform.db"

from app.main import app  # noqa: E402

__all__ = ["app"]
