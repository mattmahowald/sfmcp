from __future__ import annotations
from pydantic import BaseSettings, Field
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    # Salesforce org configuration from .env file
    sf_instance_url: str = Field(..., env="SF_INSTANCE_URL")
    sf_access_token: str = Field(..., env="SF_ACCESS_TOKEN")
    sf_org_alias: str = Field(..., env="SF_ORG_ALIAS")
    sf_username: str = Field(..., env="SF_USERNAME")

    # Server configuration
    http_host: str = Field(default="127.0.0.1", env="SFMCP_HTTP_HOST")
    http_port: int = Field(default=3333, env="SFMCP_HTTP_PORT")


settings = Settings()  # evaluated at import time
