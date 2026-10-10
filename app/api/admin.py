"""Admin control endpoints for simulating failures and chaos."""

from typing import Optional
from fastapi import APIRouter, Header, HTTPException, status
from app.config import settings
from app.models import FailureStatusResponse, FailureToggleRequest
from app.state import app_state

router = APIRouter(prefix="/admin/failures", tags=["Admin Chaos Controls"])


def verify_admin_token(x_admin_token: Optional[str] = Header(None)):
    """Verifies the X-Admin-Token header against configured admin secret."""
    if not x_admin_token or x_admin_token != settings.CHAOS_ADMIN_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-Admin-Token header.",
        )


@router.get("", response_model=FailureStatusResponse)
async def get_failure_status(x_admin_token: Optional[str] = Header(None)):
    """Returns the current state of failure toggle switches."""
    verify_admin_token(x_admin_token)
    return FailureStatusResponse(
        order_processing_failure=app_state.fail_order_processing,
        health_outage_failure=app_state.fail_health_outage,
    )


@router.post("/order-processing", response_model=FailureStatusResponse)
async def set_order_processing_failure(
    payload: FailureToggleRequest,
    x_admin_token: Optional[str] = Header(None),
):
    """Explicitly enables or disables simulated OrderProcessingError in order checkout."""
    verify_admin_token(x_admin_token)
    app_state.fail_order_processing = payload.enabled
    return FailureStatusResponse(
        order_processing_failure=app_state.fail_order_processing,
        health_outage_failure=app_state.fail_health_outage,
    )


@router.post("/order-processing/enable", response_model=FailureStatusResponse)
async def enable_order_processing_failure(x_admin_token: Optional[str] = Header(None)):
    """Explicitly enables simulated OrderProcessingError."""
    verify_admin_token(x_admin_token)
    app_state.fail_order_processing = True
    return FailureStatusResponse(
        order_processing_failure=app_state.fail_order_processing,
        health_outage_failure=app_state.fail_health_outage,
    )


@router.post("/order-processing/disable", response_model=FailureStatusResponse)
async def disable_order_processing_failure(x_admin_token: Optional[str] = Header(None)):
    """Explicitly disables simulated OrderProcessingError."""
    verify_admin_token(x_admin_token)
    app_state.fail_order_processing = False
    return FailureStatusResponse(
        order_processing_failure=app_state.fail_order_processing,
        health_outage_failure=app_state.fail_health_outage,
    )


@router.post("/health-outage", response_model=FailureStatusResponse)
async def set_health_outage_failure(
    payload: FailureToggleRequest,
    x_admin_token: Optional[str] = Header(None),
):
    """Explicitly enables or disables simulated 503 outage on GET /health."""
    verify_admin_token(x_admin_token)
    app_state.fail_health_outage = payload.enabled
    return FailureStatusResponse(
        order_processing_failure=app_state.fail_order_processing,
        health_outage_failure=app_state.fail_health_outage,
    )


@router.post("/health-outage/enable", response_model=FailureStatusResponse)
async def enable_health_outage_failure(x_admin_token: Optional[str] = Header(None)):
    """Explicitly enables simulated 503 outage on GET /health."""
    verify_admin_token(x_admin_token)
    app_state.fail_health_outage = True
    return FailureStatusResponse(
        order_processing_failure=app_state.fail_order_processing,
        health_outage_failure=app_state.fail_health_outage,
    )


@router.post("/health-outage/disable", response_model=FailureStatusResponse)
async def disable_health_outage_failure(x_admin_token: Optional[str] = Header(None)):
    """Explicitly disables simulated 503 outage on GET /health."""
    verify_admin_token(x_admin_token)
    app_state.fail_health_outage = False
    return FailureStatusResponse(
        order_processing_failure=app_state.fail_order_processing,
        health_outage_failure=app_state.fail_health_outage,
    )


@router.post("/reset", response_model=FailureStatusResponse)
async def reset_all_failures(x_admin_token: Optional[str] = Header(None)):
    """Resets all simulated failure states to disabled (normal operating condition)."""
    verify_admin_token(x_admin_token)
    app_state.reset_failures()
    return FailureStatusResponse(
        order_processing_failure=app_state.fail_order_processing,
        health_outage_failure=app_state.fail_health_outage,
    )
