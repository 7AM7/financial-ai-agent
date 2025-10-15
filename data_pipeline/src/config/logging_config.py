"""
Structured logging configuration using structlog.
"""
import logging
import sys
from pathlib import Path

import structlog

from src.config.settings import settings


def setup_logging() -> None:
    """Configure structured logging for the application."""

    # Ensure logs directory exists
    settings.logs_dir.mkdir(parents=True, exist_ok=True)

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
    )

    # Add file handler
    file_handler = logging.FileHandler(
        settings.logs_dir / "pipeline.log",
        encoding="utf-8",
    )
    file_handler.setLevel(getattr(logging, settings.log_level.upper()))
    logging.getLogger().addHandler(file_handler)

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(colors=True),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)
