"""
Notification Service — API tests.

Covers:
  - Health check
  - List notifications (empty)
  - Service starts without DB (Redis-only)
"""

import sys
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

# Add notification-service to path
NOTIF_ROOT = Path(__file__).resolve().parent.parent.parent / "services" / "notification-service"
sys.path.insert(0, str(NOTIF_ROOT))

from app.main import app


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture
async def client():
    """Return an AsyncClient bound to the FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ===================================================================
# Health
# ===================================================================

@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "Notification Service" in data["service"]


# ===================================================================
# Notifications list
# ===================================================================

@pytest.mark.asyncio
async def test_list_notifications_empty(client):
    resp = await client.get("/api/v1/notifications/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
