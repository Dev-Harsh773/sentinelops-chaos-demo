"""Application configuration loaded from environment."""

import os
from typing import Optional


class Settings:
    SENTINELOPS_WEBHOOK_URL: Optional[str] = os.getenv("SENTINELOPS_WEBHOOK_URL")
    SENTINELOPS_WEBHOOK_SECRET: Optional[str] = os.getenv("SENTINELOPS_WEBHOOK_SECRET")
    CHAOS_ADMIN_TOKEN: str = os.getenv("CHAOS_ADMIN_TOKEN", "chaos-admin-secret")
    SERVICE_NAME: str = os.getenv("SERVICE_NAME", "sentinelops-chaos-demo")
    SERVICE_VERSION: str = "1.0.0"


settings = Settings()
