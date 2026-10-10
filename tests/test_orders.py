"""Tests for order creation and simulated order processing failures."""

import pytest
from starlette.testclient import TestClient
from app.main import app
from app.state import app_state


@pytest.fixture(autouse=True)
def reset_state():
    app_state.reset_failures()
    yield
    app_state.reset_failures()


def test_create_order_success():
    client = TestClient(app)
    payload = {
        "product_id": "prod-1",
        "quantity": 2,
        "customer_email": "alice@example.com",
    }
    response = client.post("/orders", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["order_id"].startswith("ord-")
    assert data["status"] == "confirmed"
    assert data["quantity"] == 2
    assert data["customer_email"] == "alice@example.com"
    assert data["total"] == 599.98


def test_get_order_by_id():
    client = TestClient(app)
    create_resp = client.post("/orders", json={"product_id": "prod-2", "quantity": 1, "customer_email": "bob@example.com"})
    order_id = create_resp.json()["order_id"]

    get_resp = client.get(f"/orders/{order_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["order_id"] == order_id


def test_create_order_product_not_found():
    client = TestClient(app)
    response = client.post("/orders", json={"product_id": "unknown-prod", "quantity": 1, "customer_email": "test@example.com"})
    assert response.status_code == 404


def test_create_order_insufficient_stock():
    client = TestClient(app)
    response = client.post("/orders", json={"product_id": "prod-1", "quantity": 99999, "customer_email": "test@example.com"})
    assert response.status_code == 400


def test_create_order_with_failure_toggle():
    client = TestClient(app)
    app_state.fail_order_processing = True

    response = client.post("/orders", json={"product_id": "prod-1", "quantity": 1, "customer_email": "alice@example.com"})
    assert response.status_code == 500
    data = response.json()
    assert "Inventory allocation lock timeout during order checkout" in data["detail"]
