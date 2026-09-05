"""Structured logging setup using structlog.

Call ``configure_logging`` once at process startup (API app, Celery worker,
or CLI script). After that, use ``get_logger(__name__)`` anywhere to obtain
a bound structured logger.
"""

from __future__ import annotations

import logging
import sys

import structlog

from canary_api.core.config import Settings


def configure_logging(settings: Settings) -> None:
    """Configure stdlib logging + structlog processors for the process."""

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=settings.log_level.upper(),
    )

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    renderer: structlog.types.Processor
    if settings.log_json:
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer()

    structlog.configure(
        processors=[*shared_processors, renderer],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.types.BindableLogger:
    """Return a structured logger bound to ``name`` (typically ``__name__``)."""

    return structlog.get_logger(name)
