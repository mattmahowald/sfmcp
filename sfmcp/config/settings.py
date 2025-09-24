from __future__ import annotations
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    # Prefer injecting short-lived tokens; adapt to your auth flow.
    sf_instance_url: str = Field(..., env="SF_INSTANCE_URL")
    sf_access_token: str = Field(..., env="SF_ACCESS_TOKEN")
    http_host: str = Field(default="127.0.0.1", env="SFMCP_HTTP_HOST")
    http_port: int = Field(default=3333, env="SFMCP_HTTP_PORT")

settings = Settings()  # evaluated at import time
