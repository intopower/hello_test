from __future__ import annotations

from celery import Celery

from app.core.config import settings


def create_celery_app() -> Celery:
    app = Celery(
        "tv_commentary",
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend,
        include=["app.workers.tasks"],
    )
    app.conf.update(
        task_default_queue="tv-commentary",
        task_track_started=True,
        broker_connection_retry_on_startup=True,
    )
    return app


celery_app = create_celery_app()
