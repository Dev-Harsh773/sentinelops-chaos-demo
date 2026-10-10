"""Order checkout and management endpoints."""

from datetime import datetime, timezone
from typing import List
import uuid
from fastapi import APIRouter, HTTPException, status
from app.exceptions import OrderProcessingError
from app.models import Order, OrderCreate
from app.state import app_state

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(payload: OrderCreate):
    """Creates a new order.

    If order processing failure is simulated, raises OrderProcessingError.
    On success, deducts stock and returns HTTP 201 Created.
    """
    if app_state.fail_order_processing:
        raise OrderProcessingError("Inventory allocation lock timeout during order checkout")

    product = app_state.products.get(payload.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product '{payload.product_id}' not found.",
        )

    if product.stock < payload.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock for product '{product.name}'. Available: {product.stock}",
        )

    # Deduct stock
    product.stock -= payload.quantity

    order_id = f"ord-{uuid.uuid4().hex[:8]}"
    order = Order(
        order_id=order_id,
        product_id=payload.product_id,
        quantity=payload.quantity,
        status="confirmed",
        total=round(product.price * payload.quantity, 2),
        customer_email=payload.customer_email,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    app_state.orders[order_id] = order
    return order


@router.get("", response_model=List[Order])
async def list_orders():
    """Lists all created orders."""
    return list(app_state.orders.values())


@router.get("/{order_id}", response_model=Order)
async def get_order(order_id: str):
    """Gets details of an existing order."""
    order = app_state.orders.get(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order '{order_id}' not found.",
        )
    return order
