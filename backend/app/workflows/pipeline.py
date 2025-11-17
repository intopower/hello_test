"""管线编排：串联语音转写、脚本生成、剪辑、配音等步骤（当前为占位实现）。"""

from __future__ import annotations

import asyncio
from typing import Iterable

from app.schemas.tasks import ScriptSegment, TaskStatus, VideoAsset
from app.services.task_service import InMemoryTaskService


class PipelineOrchestrator:
    def __init__(self, task_service: InMemoryTaskService) -> None:
        self._task_service = task_service

    async def process_task(self, task_id: str) -> None:
        # 模拟分析阶段
        self._task_service.update_task(task_id, status=TaskStatus.ANALYZING)
        await asyncio.sleep(0.1)
        transcript = self._mock_transcription()

        # 脚本生成
        self._task_service.update_task(task_id, status=TaskStatus.SCRIPTING)
        await asyncio.sleep(0.1)
        script = list(self._mock_script_segments(transcript))
        self._task_service.update_task(task_id, script=script)

        # 剪辑
        self._task_service.update_task(task_id, status=TaskStatus.EDITING)
        await asyncio.sleep(0.1)
        video_asset = VideoAsset(url=f"memory://{task_id}/output.mp4", duration=90.0, resolution="1080p")

        # 渲染
        self._task_service.update_task(
            task_id,
            status=TaskStatus.COMPLETED,
            output_asset=video_asset,
        )

    def _mock_transcription(self) -> list[str]:
        return [
            "两位主角在雨夜重逢，情绪复杂",
            "反派突然出现触发冲突",
            "最后用开放式结尾留下悬念",
        ]

    def _mock_script_segments(self, transcript: Iterable[str]) -> Iterable[ScriptSegment]:
        for idx, line in enumerate(transcript, start=1):
            yield ScriptSegment(
                order=idx,
                text=f"第{idx}段解说：{line}",
                start=(idx - 1) * 30.0,
                end=idx * 30.0,
                emotion="dramatic" if idx == 2 else "calm",
                keywords=["主角", "冲突"] if idx == 2 else ["剧情", "线索"],
            )
