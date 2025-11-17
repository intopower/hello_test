from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Dict

from app.schemas.tasks import (
    NarrationAsset,
    ScriptSegment,
    TaskStatus,
    TimelineEvent,
    VideoAsset,
    VideoTask,
    VideoTaskCreate,
)


class TaskService:
    """基于本地文件的任务存储服务，便于后续替换为数据库."""

    def __init__(self, data_root: Path) -> None:
        self._tasks: Dict[str, VideoTask] = {}
        self._lock = Lock()
        self._tasks_file = data_root / "tasks.json"
        self._tasks_file.parent.mkdir(parents=True, exist_ok=True)
        self._load()

    def _load(self) -> None:
        if not self._tasks_file.exists():
            return
        try:
            raw = json.loads(self._tasks_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            raw = []
        for entry in raw:
            task = VideoTask.model_validate(entry)
            self._tasks[task.id] = task

    def _persist(self) -> None:
        payload = [task.model_dump(mode="json") for task in self._tasks.values()]
        self._tasks_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def create_task(self, payload: VideoTaskCreate, source_asset: VideoAsset | None = None) -> VideoTask:
        task_id = uuid.uuid4().hex
        now = datetime.utcnow()
        task = VideoTask(
            id=task_id,
            status=TaskStatus.PENDING,
            created_at=now,
            updated_at=now,
            script=[],
            source_asset=source_asset,
            options=payload.model_copy(),
        )
        with self._lock:
            self._tasks[task_id] = task
            self._persist()
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
        timeline: list[TimelineEvent] | None = None,
        narration_assets: list[NarrationAsset] | None = None,
        bgm_theme: str | None = None,
        source_asset: VideoAsset | None = None,
    ) -> VideoTask:
        task = self._tasks[task_id]
        if status:
            task.status = status
        if script is not None:
            task.script = script
        if output_asset:
            task.output_asset = output_asset
        if source_asset:
            task.source_asset = source_asset
        if timeline is not None:
            task.timeline = timeline
        if narration_assets is not None:
            task.narration_assets = narration_assets
        if bgm_theme is not None:
            task.bgm_theme = bgm_theme
        if failure_reason is not None:
            task.failure_reason = failure_reason
        task.updated_at = datetime.utcnow()
        with self._lock:
            self._tasks[task_id] = task
            self._persist()
        return task


TASK_SERVICE: TaskService | None = None


def get_task_service() -> TaskService:
    global TASK_SERVICE  # noqa: PLW0603
    if TASK_SERVICE is None:
        from app.core.config import settings

        TASK_SERVICE = TaskService(settings.data_root)
    return TASK_SERVICE
