"""管线编排：串联语音转写、脚本生成、剪辑、配音等步骤（当前为占位实现）。"""

from __future__ import annotations

import asyncio
from pathlib import Path
from app.schemas.tasks import TaskStatus, TimelineEvent, VideoAsset
from app.services.script_generator import ScriptGenerationService
from app.services.storage import FileStorageService
from app.services.task_service import TaskService
from app.services.transcription import TranscriptionService
from app.services.tts_service import TTSService
from app.services.video_editor import VideoEditingService


class PipelineOrchestrator:
    def __init__(
        self,
        task_service: TaskService,
        storage: FileStorageService,
        transcription: TranscriptionService,
        script_service: ScriptGenerationService,
        video_editor: VideoEditingService,
        tts_service: TTSService,
    ) -> None:
        self._task_service = task_service
        self._storage = storage
        self._transcription = transcription
        self._script_service = script_service
        self._video_editor = video_editor
        self._tts_service = tts_service

    async def process_task(self, task_id: str) -> None:
        task = self._task_service.get_task(task_id)
        if not task:
            return
        timeline: list[TimelineEvent] = []
        current_time = 0.0

        try:
            self._task_service.update_task(task_id, status=TaskStatus.ANALYZING)
            transcript = await asyncio.to_thread(
                self._transcription.transcribe,
                self._get_source_path(task_id, task.source_asset),
                hints=[task.options.description or ""],
            )
            current_time = self._append_timeline(timeline, "剧情解析", current_time, 12, "analysis")

            self._task_service.update_task(task_id, status=TaskStatus.SCRIPTING)
            script_result = await asyncio.to_thread(
                self._script_service.generate,
                transcript.segments,
                target_duration=task.options.target_duration,
            )
            self._task_service.update_task(
                task_id,
                script=script_result.segments,
                bgm_theme=script_result.bgm_theme,
            )
            current_time = self._append_timeline(timeline, "脚本生成", current_time, 18, "script")

            self._task_service.update_task(task_id, status=TaskStatus.EDITING)
            video_asset = await asyncio.to_thread(
                self._video_editor.build_highlight,
                task_id,
                task.source_asset,
                script_result.segments,
            )
            current_time = self._append_timeline(timeline, "智能剪辑", current_time, 30, "editing")

            self._task_service.update_task(task_id, status=TaskStatus.RENDERING)
            narration_assets = await asyncio.to_thread(
                self._tts_service.synthesize_segments,
                task_id,
                script_result.segments,
                language=task.options.language,
                voice_profile=task.options.voice_profile,
            )
            current_time = self._append_timeline(timeline, "配音与混音", current_time, 20, "audio")

            self._task_service.update_task(
                task_id,
                status=TaskStatus.COMPLETED,
                output_asset=video_asset,
                narration_assets=narration_assets,
                timeline=timeline,
            )
        except Exception as exc:  # pragma: no cover - 容错路径
            self._task_service.update_task(
                task_id,
                status=TaskStatus.FAILED,
                failure_reason=str(exc),
                timeline=timeline,
            )

    def _append_timeline(
        self,
        timeline: list[TimelineEvent],
        label: str,
        start: float,
        duration: float,
        category: str,
    ) -> float:
        event = TimelineEvent(label=label, start=start, end=start + duration, category=category)
        timeline.append(event)
        return start + duration

    def _get_source_path(self, task_id: str, asset: VideoAsset | None) -> Path:
        if asset and asset.local_path:
            path = Path(asset.local_path)
            if path.exists():
                return path
        placeholder = self._storage.allocate_file(task_id, "placeholder.txt")
        placeholder.write_text("占位文件", encoding="utf-8")
        return placeholder
