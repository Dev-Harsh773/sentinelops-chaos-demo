"""Tests for GET /health and failure toggling."""

import pytest
from starlette.testclient import TestClient
from app.main import app
from app.state import app_state


@pytest.fixture(autouse=True)
def reset_state():
    app_state.reset_failures()
    yield
    app_state.reset_failures()


def test_health_check_healthy():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "sentinelops-chaos-demo"


def test_health_check_outage_toggled():
    client = TestClient(app)
    app_state.fail_health_outage = True

    response = client.get("/health")
    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "unhealthy"
    assert "Database connection pool exhausted" in data["error"]
