from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from openai import OpenAI


@dataclass
class TranscriptionResult:
    language: str
    segments: list[str]


class TranscriptionService:
    """Whisper/OpenAI 转写，若缺少 API Key 则回退到占位内容."""

    def __init__(
        self,
        *,
        api_key: str | None,
        model: str,
        default_language: str = "zh",
    ) -> None:
        self._default_language = default_language
        self._model = model
        self._client: OpenAI | None = OpenAI(api_key=api_key) if api_key else None

    def transcribe(
        self,
        media_path: Path,
        *,
        hints: Sequence[str] | None = None,
        language: str | None = None,
    ) -> TranscriptionResult:
        lang = language or self._default_language
        if self._client and media_path.exists():
            with media_path.open("rb") as audio_file:
                response = self._client.audio.transcriptions.create(
                    model=self._model,
                    file=audio_file,
                    language=lang,
                    prompt=" ".join(hints or ""),
                )
            text = getattr(response, "text", "") or ""
            segments = self._split_segments(text)
            detected = getattr(response, "language", None) or lang
            return TranscriptionResult(language=detected, segments=segments)

        return TranscriptionResult(language=lang, segments=self._fallback_segments(media_path, hints))

    def _split_segments(self, text: str) -> list[str]:
        if not text.strip():
            return ["未识别到有效对白，但仍可生成概述。"]
        delimiters = "。！？!?\n"
        segments: list[str] = []
        current = ""
        for char in text:
            current += char
            if char in delimiters and current.strip():
                segments.append(current.strip())
                current = ""
        if current.strip():
            segments.append(current.strip())
        return segments

    def _fallback_segments(self, media_path: Path, hints: Sequence[str] | None) -> list[str]:
        summary = "".join(hints or [])
        filename = media_path.name
        return [
            f"【占位】素材 {filename}，请在配置 OPENAI_API_KEY 后获取真实转写。",
            f"参考线索：{summary or '暂无'}",
            "可继续执行脚本生成，以便验证后续链路。",
        ]
