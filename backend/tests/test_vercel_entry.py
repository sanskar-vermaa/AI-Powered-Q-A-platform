"""The Vercel entry point must boot the API with no database configured."""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SCRIPT = """
import importlib.util, os
spec = importlib.util.spec_from_file_location("vercel_entry", "api/index.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
print(os.environ["DATABASE_URL"])
from fastapi.testclient import TestClient
with TestClient(module.app) as client:
    print(client.get("/api/health").json()["status"])
"""


def _run(extra_env: dict[str, str], tmp_path) -> list[str]:
    env = {k: v for k, v in os.environ.items() if k not in ("DATABASE_URL", "POSTGRES_URL")}
    env.update(extra_env)
    env["FRONTEND_DIST"] = str(tmp_path / "no-dist")
    out = subprocess.run(
        [sys.executable, "-c", SCRIPT],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    return out.stdout.strip().splitlines()


def test_falls_back_to_tmp_sqlite(tmp_path):
    url, status = _run({}, tmp_path)
    assert url == "sqlite:////tmp/qa_platform.db"
    assert status == "ok"


def test_uses_postgres_url_from_integration(tmp_path):
    db = tmp_path / "integration.db"
    url, status = _run({"POSTGRES_URL": f"sqlite:///{db}"}, tmp_path)
    assert url == f"sqlite:///{db}"
    assert status == "ok"


def test_explicit_database_url_wins(tmp_path):
    db = tmp_path / "explicit.db"
    url, _ = _run({"DATABASE_URL": f"sqlite:///{db}", "POSTGRES_URL": "postgres://x/y"}, tmp_path)
    assert url == f"sqlite:///{db}"
