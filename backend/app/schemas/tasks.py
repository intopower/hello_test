from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    SCRIPTING = "scripting"
    EDITING = "editing"
    RENDERING = "rendering"
    COMPLETED = "completed"
    FAILED = "failed"


class ScriptSegment(BaseModel):
    order: int
    text: str
    start: float = Field(..., description="片段起始时间，单位秒")
    end: float = Field(..., description="片段结束时间，单位秒")
    emotion: str | None = Field(None, description="情绪/语气标签")
    keywords: list[str] = Field(default_factory=list, description="镜头匹配关键词")


class VideoAsset(BaseModel):
    url: str
    duration: float | None = None
    resolution: str | None = None


class VideoTaskCreate(BaseModel):
    title: str
    description: str | None = None
    language: str = "zh"
    voice_profile: str = "narrator_female"
    target_duration: int = Field(90, ge=30, le=300)


class VideoTask(BaseModel):
    id: str
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    script: list[ScriptSegment] = Field(default_factory=list)
    source_asset: VideoAsset | None = None
    output_asset: VideoAsset | None = None
    failure_reason: str | None = None


class VideoTaskResponse(BaseModel):
    task_id: str
    status: TaskStatus


class VideoTaskDetail(VideoTask):
    progress: float = Field(0.0, ge=0.0, le=1.0)
