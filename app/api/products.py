"""Product catalog endpoints."""

from typing import List
from fastapi import APIRouter, HTTPException, status
from app.models import Product
from app.state import app_state

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=List[Product])
async def list_products():
    """Returns the list of available products."""
    return list(app_state.products.values())


@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """Returns details for a specific product."""
    product = app_state.products.get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product '{product_id}' not found.",
        )
    return product
