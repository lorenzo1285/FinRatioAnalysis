"""Configuration settings for FinRatioAnalysis MCP Server.

Reads environment variables with sensible defaults per research D9.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """MCP server configuration from environment variables."""

    log_level: str = "INFO"
    timeout_seconds: int = 15
    default_freq: str = "yearly"
    cache_ttl_seconds: int = 0  # Disabled by default

    model_config = SettingsConfigDict(
        env_prefix="FINRATIO_MCP_",
        case_sensitive=False,
    )


# Global settings instance
settings = Settings()
