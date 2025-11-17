from __future__ import annotations

import asyncio

from celery.utils.log import get_task_logger

from app.core.celery_app import celery_app
from app.workflows.bootstrap import get_orchestrator

logger = get_task_logger(__name__)


@celery_app.task(name="pipeline.process_task")
def process_video_task(task_id: str) -> None:
    logger.info("Starting pipeline for task %s", task_id)
    orchestrator = get_orchestrator()
    try:
        asyncio.run(orchestrator.process_task(task_id))
        logger.info("Task %s completed", task_id)
    except Exception as exc:  # pragma: no cover
        logger.exception("Task %s failed: %s", task_id, exc)
        raise
