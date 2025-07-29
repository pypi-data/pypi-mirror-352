"""Logging configuration for xmltree."""

import logging

from rich.logging import RichHandler

from .config import get_settings


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance."""
    assert name, "Logger name cannot be empty"

    # Configure logging once at module level
    if not logging.getLogger().handlers:
        settings = get_settings()

        logging.basicConfig(
            level=settings.log_level,  # Already validated by pydantic
            format="%(message)s",
            handlers=[
                RichHandler(
                    rich_tracebacks=True,
                    tracebacks_show_locals=settings.debug,
                    show_time=True,
                    show_path=settings.debug,
                )
            ],
            force=True,  # Reconfigure if already configured
        )

    return logging.getLogger(name)
