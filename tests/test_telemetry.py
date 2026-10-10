"""Tests for telemetry dispatch and error handler integration."""

from unittest.mock import AsyncMock, patch
import httpx
import pytest
from starlette.testclient import TestClient
from app.config import settings
from app.main import app
from app.state import app_state
from app.telemetry import dispatch_telemetry


@pytest.fixture(autouse=True)
def reset_state():
    app_state.reset_failures()
    yield
    app_state.reset_failures()


@pytest.mark.asyncio
async def test_dispatch_telemetry_success():
    """Telemetry payload is sent with correct structure and authentication header."""
    fake_resp = httpx.Response(status_code=200, content=b'{"status":"accepted"}')

    with patch.object(settings, "SENTINELOPS_WEBHOOK_URL", "http://gateway.local:8080/connectors/conn-1/ingest"), \
         patch.object(settings, "SENTINELOPS_WEBHOOK_SECRET", "test-secret-token"), \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = fake_resp

        success = await dispatch_telemetry(
            signal_type="log",
            level="ERROR",
            event_type="order.processing.failed",
            message="Simulated error message",
            exception_type="OrderProcessingError",
            traceback="Traceback...",
            metadata={"product_id": "prod-1"},
        )

        assert success is True
        mock_post.assert_awaited_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "http://gateway.local:8080/connectors/conn-1/ingest"
        assert kwargs["headers"]["X-Sentinel-Secret"] == "test-secret-token"
        assert kwargs["json"]["signal_type"] == "log"
        assert kwargs["json"]["level"] == "ERROR"
        assert kwargs["json"]["event_type"] == "order.processing.failed"
        assert kwargs["json"]["exception_type"] == "OrderProcessingError"


@pytest.mark.asyncio
async def test_dispatch_telemetry_skipped_when_no_url():
    """Telemetry is gracefully skipped if webhook URL is not configured."""
    with patch.object(settings, "SENTINELOPS_WEBHOOK_URL", None), \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        success = await dispatch_telemetry(
            signal_type="log",
            level="ERROR",
            event_type="order.failed",
            message="Test",
        )
        assert success is False
        mock_post.assert_not_called()


def test_order_processing_error_invokes_telemetry_dispatch():
    """Triggering OrderProcessingError executes dispatch_telemetry in background."""
    client = TestClient(app)
    app_state.fail_order_processing = True

    with patch("app.main.dispatch_telemetry", new_callable=AsyncMock) as mock_dispatch:
        response = client.post(
            "/orders",
            json={"product_id": "prod-1", "quantity": 1, "customer_email": "test@example.com"},
        )
        assert response.status_code == 500
        mock_dispatch.assert_called_once()
        call_kwargs = mock_dispatch.call_args.kwargs
        assert call_kwargs["event_type"] == "order.processing.failed"
        assert call_kwargs["exception_type"] == "OrderProcessingError"
