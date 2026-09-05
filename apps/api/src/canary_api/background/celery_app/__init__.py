"""Celery application factory.

Analysis tasks (scanning, indexing, security/dependency/architecture
analysis) will be registered under ``background.tasks`` in later phases.
This module only establishes the wiring so the worker process can start.
"""

from __future__ import annotations

from celery import Celery

from canary_api.core.config import get_settings


def create_celery_app() -> Celery:
    """Construct the Celery application using centralized settings."""

    settings = get_settings()
    app = Celery(
        "canary",
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend,
    )
    app.conf.task_serializer = "json"
    app.conf.result_serializer = "json"
    app.conf.accept_content = ["json"]
    app.conf.timezone = "UTC"
    return app


celery_app = create_celery_app()
