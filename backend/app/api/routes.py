from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.config import settings
from app.schemas.tasks import TaskStatus, VideoTaskCreate, VideoTaskDetail, VideoTaskResponse
from app.services.task_service import get_task_service
from app.workflows.bootstrap import get_storage_service
from app.workers.tasks import process_video_task

router = APIRouter(prefix="/api")
task_service = get_task_service()
storage_service = get_storage_service()


@router.post("/tasks", response_model=VideoTaskResponse)
async def create_task(
    metadata: Annotated[str, Form(description="VideoTaskCreate JSON 数据")],
    file: UploadFile | None = File(None),
):
    try:
        payload = VideoTaskCreate.model_validate_json(metadata)
    except ValueError as exc:  # noqa: PERF203
        raise HTTPException(status_code=400, detail=f"metadata 解析失败: {exc}") from exc

    task = task_service.create_task(payload)
    source_asset = storage_service.save_upload(task.id, file)
    if source_asset:
        task = task_service.update_task(task.id, source_asset=source_asset)
    process_video_task.delay(task.id)
    return VideoTaskResponse(task_id=task.id, status=task.status)


@router.get("/tasks/{task_id}", response_model=VideoTaskDetail)
async def get_task(task_id: str):
    task = task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return VideoTaskDetail(**_public_task(task), progress=_status_to_progress(task.status))


@router.get("/tasks", response_model=list[VideoTaskDetail])
async def list_tasks():
    return [
        VideoTaskDetail(**_public_task(task), progress=_status_to_progress(task.status))
        for task in task_service.list_tasks()
    ]


def _status_to_progress(status: TaskStatus) -> float:
    mapping = {
        "pending": 0.05,
        "analyzing": 0.25,
        "scripting": 0.5,
        "editing": 0.75,
        "rendering": 0.9,
        "completed": 1.0,
        "failed": 1.0,
    }
    key = status.value if isinstance(status, TaskStatus) else str(status)
    return mapping.get(key, 0.0)


def _public_task(task):
    return task.model_dump(exclude={"source_asset": {"local_path"}, "output_asset": {"local_path"}})
