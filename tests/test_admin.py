"""Tests for admin chaos control endpoints."""

import pytest
from starlette.testclient import TestClient
from app.config import settings
from app.main import app
from app.state import app_state


@pytest.fixture(autouse=True)
def reset_state():
    app_state.reset_failures()
    yield
    app_state.reset_failures()


def test_admin_requires_token():
    client = TestClient(app)
    # Missing token
    resp = client.get("/admin/failures")
    assert resp.status_code == 401

    # Invalid token
    resp = client.get("/admin/failures", headers={"X-Admin-Token": "bad-token"})
    assert resp.status_code == 401


def test_admin_get_and_toggle_failures():
    client = TestClient(app)
    headers = {"X-Admin-Token": settings.CHAOS_ADMIN_TOKEN}

    # Initial state
    resp = client.get("/admin/failures", headers=headers)
    assert resp.status_code == 200
    assert resp.json() == {"order_processing_failure": False, "health_outage_failure": False}

    # Enable order processing failure via payload
    resp = client.post("/admin/failures/order-processing", json={"enabled": True}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["order_processing_failure"] is True
    assert app_state.fail_order_processing is True

    # Enable health outage via payload
    resp = client.post("/admin/failures/health-outage", json={"enabled": True}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["health_outage_failure"] is True
    assert app_state.fail_health_outage is True

    # Disable both via payload
    client.post("/admin/failures/order-processing", json={"enabled": False}, headers=headers)
    client.post("/admin/failures/health-outage", json={"enabled": False}, headers=headers)
    assert app_state.fail_order_processing is False
    assert app_state.fail_health_outage is False


def test_admin_deterministic_enable_disable_and_reset():
    client = TestClient(app)
    headers = {"X-Admin-Token": settings.CHAOS_ADMIN_TOKEN}

    # Explicit enable order failure
    resp = client.post("/admin/failures/order-processing/enable", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["order_processing_failure"] is True
    assert app_state.fail_order_processing is True

    # Explicit disable order failure
    resp = client.post("/admin/failures/order-processing/disable", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["order_processing_failure"] is False
    assert app_state.fail_order_processing is False

    # Explicit enable health outage
    resp = client.post("/admin/failures/health-outage/enable", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["health_outage_failure"] is True
    assert app_state.fail_health_outage is True

    # Explicit disable health outage
    resp = client.post("/admin/failures/health-outage/disable", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["health_outage_failure"] is False
    assert app_state.fail_health_outage is False

    # Enable both then reset all
    client.post("/admin/failures/order-processing/enable", headers=headers)
    client.post("/admin/failures/health-outage/enable", headers=headers)
    assert app_state.fail_order_processing is True
    assert app_state.fail_health_outage is True

    reset_resp = client.post("/admin/failures/reset", headers=headers)
    assert reset_resp.status_code == 200
    assert reset_resp.json() == {"order_processing_failure": False, "health_outage_failure": False}
    assert app_state.fail_order_processing is False
    assert app_state.fail_health_outage is False
