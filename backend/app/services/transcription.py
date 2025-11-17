from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass
class TranscriptionResult:
    language: str
    segments: list[str]


class TranscriptionService:
    """占位的语音转写服务，可在此对接 Whisper/Paraformer."""

    def __init__(self, default_language: str = "zh") -> None:
        self._default_language = default_language

    def transcribe(self, media_path: Path, *, hints: Sequence[str] | None = None) -> TranscriptionResult:
        summary = "".join(hints or [])
        filename = media_path.name
        segments = [
            f"【设定】素材 {filename}，包含{len(summary) or 3}个关键情节",
            "开场：主角遭遇突发事件，情绪被拉满",
            "中段：反派逼近、冲突升级，埋下伏笔",
            "结尾：留下悬念，适合短视频反转收尾",
        ]
        return TranscriptionResult(language=self._default_language, segments=segments)
