"""Telemetry dispatcher sending events to SentinelOps connector ingest endpoint."""

import logging
from typing import Any, Dict, Optional
import httpx
from app.config import settings

logger = logging.getLogger("chaos_telemetry")


async def dispatch_telemetry(
    signal_type: str,
    level: str,
    event_type: str,
    message: str,
    exception_type: Optional[str] = None,
    traceback: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> bool:
    """Dispatches generic telemetry payload to configured SentinelOps ingest URL.
    
    Uses X-Sentinel-Secret authentication header and catches exceptions to prevent
    app disruptions if SentinelOps is unreachable.
    """
    if not settings.SENTINELOPS_WEBHOOK_URL:
        logger.debug("Telemetry dispatch skipped: SENTINELOPS_WEBHOOK_URL is not set.")
        return False

    payload: Dict[str, Any] = {
        "service": settings.SERVICE_NAME,
        "signal_type": signal_type,
        "level": level,
        "event_type": event_type,
        "message": message,
        "metadata": metadata or {},
    }
    if exception_type:
        payload["exception_type"] = exception_type
    if traceback:
        payload["traceback"] = traceback

    headers = {"Content-Type": "application/json"}
    if settings.SENTINELOPS_WEBHOOK_SECRET:
        headers["X-Sentinel-Secret"] = settings.SENTINELOPS_WEBHOOK_SECRET

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(settings.SENTINELOPS_WEBHOOK_URL, json=payload, headers=headers)
            if resp.status_code in (200, 201, 202):
                logger.info("Telemetry dispatched successfully (HTTP %d)", resp.status_code)
                return True
            else:
                logger.warning("Telemetry ingestion returned HTTP %d: %s", resp.status_code, resp.text)
                return False
    except Exception as exc:
        logger.warning("Failed to dispatch telemetry to %s: %s", settings.SENTINELOPS_WEBHOOK_URL, exc)
        return False


async def emit_startup_telemetry() -> bool:
    """Dispatches startup non-error handshake telemetry to SentinelOps."""
    logger.info("Emitting startup telemetry handshake to SentinelOps...")
    return await dispatch_telemetry(
        signal_type="log",
        level="INFO",
        event_type="chaos.service.started",
        message=f"{settings.SERVICE_NAME} v{settings.SERVICE_VERSION} started successfully",
        metadata={"status": "online", "version": settings.SERVICE_VERSION},
    )
