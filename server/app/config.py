"""
Configuration settings for the MCP OAuth DCR Server.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Server configuration
    SERVER_URL: str = "http://localhost:8000"
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000

    # JWT configuration
    JWT_SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # OAuth configuration
    OAUTH_AUTHORIZATION_CODE_EXPIRE_MINUTES: int = 10
    OAUTH_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # MCP configuration
    MCP_SERVER_NAME: str = "Mock MCP Server"
    MCP_SERVER_VERSION: str = "0.1.0"

    # Development settings
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
