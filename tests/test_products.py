"""Tests for product catalog endpoints."""

from starlette.testclient import TestClient
from app.main import app


def test_list_products():
    client = TestClient(app)
    response = client.get("/products")
    assert response.status_code == 200
    products = response.json()
    assert len(products) >= 3
    ids = [p["id"] for p in products]
    assert "prod-1" in ids


def test_get_product_success():
    client = TestClient(app)
    response = client.get("/products/prod-1")
    assert response.status_code == 200
    assert response.json()["name"] == "Cloud Sentinel Sensor v1"


def test_get_product_not_found():
    client = TestClient(app)
    response = client.get("/products/non-existent-99")
    assert response.status_code == 404
