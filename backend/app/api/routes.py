from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile

from app.schemas.tasks import TaskStatus, VideoTaskCreate, VideoTaskDetail, VideoTaskResponse
from app.services.task_service import TASK_SERVICE
from app.workflows.pipeline import PipelineOrchestrator

router = APIRouter(prefix="/api")
orchestrator = PipelineOrchestrator(TASK_SERVICE)


@router.post("/tasks", response_model=VideoTaskResponse)
async def create_task(
    background_tasks: BackgroundTasks,
    metadata: Annotated[str, Form(description="VideoTaskCreate JSON 数据")],
    file: UploadFile | None = File(None),
):
    try:
        payload = VideoTaskCreate.model_validate_json(metadata)
    except ValueError as exc:  # noqa: PERF203
        raise HTTPException(status_code=400, detail=f"metadata 解析失败: {exc}") from exc

    task = TASK_SERVICE.create_task(payload, file)
    background_tasks.add_task(orchestrator.process_task, task.id)
    return VideoTaskResponse(task_id=task.id, status=task.status)


@router.get("/tasks/{task_id}", response_model=VideoTaskDetail)
async def get_task(task_id: str):
    task = TASK_SERVICE.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return VideoTaskDetail(**task.model_dump(), progress=_status_to_progress(task.status))


@router.get("/tasks", response_model=list[VideoTaskDetail])
async def list_tasks():
    return [
        VideoTaskDetail(**task.model_dump(), progress=_status_to_progress(task.status))
        for task in TASK_SERVICE.list_tasks()
    ]


def _status_to_progress(status: TaskStatus) -> float:
    mapping = {
        "pending": 0.05,
        "analyzing": 0.25,
        "scripting": 0.5,
        "editing": 0.75,
        "rendering": 0.9,
        "completed": 1.0,
    }
    key = status.value if isinstance(status, TaskStatus) else str(status)
    return mapping.get(key, 0.0)
