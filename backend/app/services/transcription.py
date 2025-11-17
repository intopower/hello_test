from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Sequence

from openai import OpenAI


@dataclass
class TranscriptionResult:
    language: str
    segments: list[str]


class TranscriptionProvider(Protocol):
    def transcribe(
        self,
        media_path: Path,
        *,
        hints: Sequence[str] | None = None,
        language: str | None = None,
    ) -> TranscriptionResult: ...


class OpenAITranscriptionService:
    """调用 OpenAI Whisper API."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        default_language: str = "zh",
    ) -> None:
        self._default_language = default_language
        self._model = model
        self._client = OpenAI(api_key=api_key)

    def transcribe(
        self,
        media_path: Path,
        *,
        hints: Sequence[str] | None = None,
        language: str | None = None,
    ) -> TranscriptionResult:
        lang = language or self._default_language
        with media_path.open("rb") as audio_file:
            response = self._client.audio.transcriptions.create(
                model=self._model,
                file=audio_file,
                language=lang,
                prompt=" ".join(hints or []),
            )
        text = getattr(response, "text", "") or ""
        segments = self._split_segments(text)
        detected = getattr(response, "language", None) or lang
        return TranscriptionResult(language=detected, segments=segments)

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


class LocalTranscriptionService:
    """基于硬件信息的占位实现，可扩展为本地 Whisper/MPS/CPU 推理."""

    def __init__(self, device_hint: str, default_language: str = "zh") -> None:
        self._default_language = default_language
        self._device_hint = device_hint

    def transcribe(
        self,
        media_path: Path,
        *,
        hints: Sequence[str] | None = None,
        language: str | None = None,
    ) -> TranscriptionResult:
        lang = language or self._default_language
        summary = "、".join(hints or []) or "该剧集"
        segments = [
            f"[{self._device_hint}] 对 {media_path.name} 的本地解析：{summary}",
            "开场：镜头节奏紧张，适合加快口播",
            "中段：冲突与反转并存，建议使用情绪起伏的配音",
            "收尾：留下悬念，引导用户观看正片",
        ]
        return TranscriptionResult(language=lang, segments=segments)
