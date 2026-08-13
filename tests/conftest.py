"""
Shared pytest fixtures for all service tests.

Provides:
  - async DB setup / teardown per module
  - pre-configured AsyncClient for FastAPI
  - environment overrides so tests don't need a real Kafka / Redis
"""

import asyncio
import os
import sys
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

# Ensure the project root is on sys.path so `shared.*` imports work.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Environment overrides — tests run WITHOUT real Kafka / Redis
# ---------------------------------------------------------------------------
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("LOG_LEVEL", "WARNING")


# ---------------------------------------------------------------------------
# anyio backend (required by pytest-asyncio >= 0.23)
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


# ---------------------------------------------------------------------------
# Helpers that each test module MUST override by importing its own app/engine
# ---------------------------------------------------------------------------
def _get_service_root(service_name: str) -> Path:
    return PROJECT_ROOT / "services" / service_name


def _add_service_to_path(service_name: str):
    service_root = _get_service_root(service_name)
    if str(service_root) not in sys.path:
        sys.path.insert(0, str(service_root))
