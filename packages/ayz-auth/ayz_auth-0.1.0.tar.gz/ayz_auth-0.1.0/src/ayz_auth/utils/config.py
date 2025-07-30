"""
Configuration management for ayz-auth package.

Uses Pydantic settings for type-safe configuration with environment variable support.
"""

from typing import Optional

from pydantic_settings import BaseSettings


class AuthSettings(BaseSettings):
    """
    Configuration settings for Stytch authentication middleware.

    All settings can be provided via environment variables with the STYTCH_ prefix.
    """

    # Stytch B2B API configuration
    stytch_project_id: str = ""
    stytch_secret: str = ""
    stytch_environment: str = "test"  # "test" or "live"

    # Redis configuration
    redis_url: str = "redis://localhost:6379"
    redis_password: Optional[str] = None
    redis_db: int = 0
    redis_ssl: bool = False

    # Caching configuration
    cache_ttl: int = 300  # 5 minutes default
    cache_prefix: str = "ayz_auth"

    # Logging configuration
    log_level: str = "INFO"
    log_sensitive_data: bool = False  # Never log tokens in production

    # Request configuration
    request_timeout: int = 10  # seconds
    max_retries: int = 3

    model_config = {
        "env_prefix": "STYTCH_",
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore",
    }


# Global settings instance
settings = AuthSettings()
