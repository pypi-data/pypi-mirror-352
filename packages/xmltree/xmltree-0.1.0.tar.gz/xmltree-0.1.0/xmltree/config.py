"""Configuration management for xmltree."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="XMLTREE_",
        case_sensitive=False,
    )

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="DEBUG", description="Logging level"
    )

    @property
    def debug(self) -> bool:
        """Check if running in debug mode."""
        return self.log_level == "DEBUG"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
