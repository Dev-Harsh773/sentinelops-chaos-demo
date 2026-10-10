"""Tests for startup non-error telemetry handshake with SentinelOps."""

from unittest.mock import AsyncMock, patch
import httpx
import pytest
from starlette.testclient import TestClient
from app.config import settings
from app.main import app
from app.telemetry import emit_startup_telemetry


@pytest.mark.asyncio
async def test_startup_telemetry_construction_and_dispatch():
    """Startup handshake telemetry is dispatched with log/INFO/chaos.service.started."""
    fake_resp = httpx.Response(status_code=200, content=b'{"status":"accepted"}')

    with patch.object(settings, "SENTINELOPS_WEBHOOK_URL", "https://ingress.example.com/connectors/conn-e2e/ingest"), \
         patch.object(settings, "SENTINELOPS_WEBHOOK_SECRET", "handshake-secret-key"), \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = fake_resp

        result = await emit_startup_telemetry()
        assert result is True

        mock_post.assert_awaited_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "https://ingress.example.com/connectors/conn-e2e/ingest"
        assert kwargs["headers"]["X-Sentinel-Secret"] == "handshake-secret-key"

        payload = kwargs["json"]
        assert payload["service"] == "sentinelops-chaos-demo"
        assert payload["signal_type"] == "log"
        assert payload["level"] == "INFO"
        assert payload["event_type"] == "chaos.service.started"
        assert "started successfully" in payload["message"]
        assert payload["metadata"]["status"] == "online"


@pytest.mark.asyncio
async def test_startup_telemetry_non_blocking_on_network_error():
    """Startup handshake does not fail or raise exception if SentinelOps is unreachable."""
    with patch.object(settings, "SENTINELOPS_WEBHOOK_URL", "https://unreachable.example.com/connectors/conn-1/ingest"), \
         patch("httpx.AsyncClient.post", side_effect=httpx.ConnectError("Network unreachable")):

        # Must gracefully return False without raising exception
        result = await emit_startup_telemetry()
        assert result is False


def test_lifespan_triggers_startup_handshake():
    """Application lifespan context executes startup handshake in background."""
    with patch("app.main.emit_startup_telemetry", new_callable=AsyncMock) as mock_handshake:
        with TestClient(app):
            # TestClient context triggers FastAPI lifespan
            pass
        mock_handshake.assert_called_once()
