"""Main FastAPI application for SentinelOps Chaos Demo."""

import asyncio
from contextlib import asynccontextmanager
import logging
import traceback
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.api import admin, health, orders, products
from app.config import settings
from app.exceptions import OrderProcessingError
from app.telemetry import dispatch_telemetry, emit_startup_telemetry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chaos_app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager executing startup non-blocking handshake telemetry."""
    # Emit startup telemetry event in background without blocking startup
    asyncio.create_task(emit_startup_telemetry())
    yield


app = FastAPI(
    title="SentinelOps Chaos Demo App",
    description="Deliberately breakable cloud e-commerce service for SentinelOps E2E validation.",
    version=settings.SERVICE_VERSION,
    lifespan=lifespan,
)

# Mount API routers
app.include_router(health.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(admin.router)


@app.get("/", tags=["Root"])
async def root():
    """Service status and quick overview."""
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "endpoints": {
            "health": "/health",
            "products": "/products",
            "orders": "/orders",
            "admin_failures": "/admin/failures",
        },
        "docs": "/docs",
    }


@app.exception_handler(OrderProcessingError)
async def handle_order_processing_error(request: Request, exc: OrderProcessingError):
    """Custom exception handler for simulated order processing chaos.

    Generates a full stack trace, dispatches telemetry asynchronously to
    SentinelOps in the background, and returns an HTTP 500 response.
    """
    tb_str = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    logger.error("OrderProcessingError triggered: %s", exc.message)

    # Dispatch non-blocking background telemetry to SentinelOps connector
    asyncio.create_task(
        dispatch_telemetry(
            signal_type="log",
            level="ERROR",
            event_type="order.processing.failed",
            message=f"Order checkout failed: {exc.message}",
            exception_type="OrderProcessingError",
            traceback=tb_str,
            metadata={"error": exc.message, "path": str(request.url.path)},
        )
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Order processing failed: {exc.message}"},
    )
