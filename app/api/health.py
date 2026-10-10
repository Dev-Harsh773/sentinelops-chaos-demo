"""Health check endpoint supporting simulated outage."""

from fastapi import APIRouter, Response, status
from app.config import settings
from app.state import app_state

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check(response: Response):
    """Health check endpoint.

    Returns HTTP 200 when healthy.
    Returns HTTP 503 when health outage failure is toggled on.
    """
    if app_state.fail_health_outage:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "unhealthy",
            "service": settings.SERVICE_NAME,
            "error": "Database connection pool exhausted",
        }

    return {
        "status": "ok",
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
    }
