from __future__ import annotations

from datetime import datetime
from typing import Dict
import uuid

from fastapi import UploadFile

from app.schemas.tasks import (
    ScriptSegment,
    TaskStatus,
    VideoAsset,
    VideoTask,
    VideoTaskCreate,
)


class InMemoryTaskService:
    """简单的内存任务管理，后续可替换为数据库/队列实现."""

    def __init__(self) -> None:
        self._tasks: Dict[str, VideoTask] = {}

    def create_task(self, payload: VideoTaskCreate, file: UploadFile | None = None) -> VideoTask:
        task_id = uuid.uuid4().hex
        now = datetime.utcnow()
        asset = VideoAsset(url=f"memory://{task_id}/{file.filename}" if file else "")

        task = VideoTask(
            id=task_id,
            status=TaskStatus.PENDING,
            created_at=now,
            updated_at=now,
            script=[],
            source_asset=asset,
        )
        self._tasks[task_id] = task
        return task

    def get_task(self, task_id: str) -> VideoTask | None:
        return self._tasks.get(task_id)

    def list_tasks(self) -> list[VideoTask]:
        return list(self._tasks.values())

    def update_task(
        self,
        task_id: str,
        *,
        status: TaskStatus | None = None,
        script: list[ScriptSegment] | None = None,
        output_asset: VideoAsset | None = None,
        failure_reason: str | None = None,
    ) -> VideoTask:
        task = self._tasks[task_id]
        if status:
            task.status = status
        if script is not None:
            task.script = script
        if output_asset:
            task.output_asset = output_asset
        if failure_reason:
            task.failure_reason = failure_reason
        task.updated_at = datetime.utcnow()
        self._tasks[task_id] = task
        return task


# 在真正部署时可以换成依赖注入的单例
TASK_SERVICE = InMemoryTaskService()
