"""Shared fixtures/paths for the dashboard tests.

Loads the stack's .env (falling back to .env.example) so the integration test
talks to InfluxDB/Grafana with the same credentials the containers were started
with, and exposes the authoritative telemetry schema.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

DASHBOARD_DIR = Path(__file__).resolve().parents[1]
SCHEMA_PATH = DASHBOARD_DIR / "docs" / "telemetry.schema.json"


def _load_env() -> dict[str, str]:
    """Read .env (or .env.example) into a plain dict (no external dependency)."""
    env: dict[str, str] = {}
    for candidate in (DASHBOARD_DIR / ".env", DASHBOARD_DIR / ".env.example"):
        if candidate.exists():
            for line in candidate.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                env[key.strip()] = value.strip()
            break
    # Real environment variables win over the file.
    env.update({k: v for k, v in os.environ.items() if k in env})
    return env


@pytest.fixture(scope="session")
def stack_env() -> dict[str, str]:
    return _load_env()


@pytest.fixture(scope="session")
def schema() -> dict:
    assert SCHEMA_PATH.exists(), f"schema not found at {SCHEMA_PATH}"
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
