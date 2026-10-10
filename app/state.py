"""In-memory state and mock data store."""

from typing import Dict
from app.models import Product, Order


INITIAL_PRODUCTS: Dict[str, Product] = {
    "prod-1": Product(id="prod-1", name="Cloud Sentinel Sensor v1", price=299.99, stock=45),
    "prod-2": Product(id="prod-2", name="Telemetry Forwarder Node", price=149.50, stock=80),
    "prod-3": Product(id="prod-3", name="Failover Edge Gateway", price=799.00, stock=12),
}


class AppState:
    def __init__(self):
        self.products: Dict[str, Product] = dict(INITIAL_PRODUCTS)
        self.orders: Dict[str, Order] = {}
        self.fail_order_processing: bool = False
        self.fail_health_outage: bool = False

    def reset_failures(self):
        self.fail_order_processing = False
        self.fail_health_outage = False


app_state = AppState()
