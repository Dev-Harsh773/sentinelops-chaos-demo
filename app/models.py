"""Pydantic schemas for request and response models."""

from typing import Optional
from pydantic import BaseModel, Field


class Product(BaseModel):
    id: str
    name: str
    price: float
    stock: int


class OrderCreate(BaseModel):
    product_id: str
    quantity: int = Field(default=1, ge=1)
    customer_email: str


class Order(BaseModel):
    order_id: str
    product_id: str
    quantity: int
    status: str
    total: float
    customer_email: str
    created_at: str


class FailureToggleRequest(BaseModel):
    enabled: bool


class FailureStatusResponse(BaseModel):
    order_processing_failure: bool
    health_outage_failure: bool
