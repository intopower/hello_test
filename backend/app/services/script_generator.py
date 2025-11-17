from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Iterable

from openai import OpenAI

from app.schemas.tasks import ScriptSegment


@dataclass
class ScriptGenerationResult:
    segments: list[ScriptSegment]
    bgm_theme: str


class ScriptGenerationService:
    THEMES = [
        ("dreamy_cinematic", "空灵电影感"),
        ("dark_suspense", "暗黑悬疑"),
        ("retro_romance", "复古情怀"),
    ]

    def __init__(self, *, api_key: str | None, model: str, temperature: float = 0.4) -> None:
        self._client: OpenAI | None = OpenAI(api_key=api_key) if api_key else None
        self._model = model
        self._temperature = temperature

    def generate(
        self,
        transcript: Iterable[str],
        *,
        target_duration: int = 90,
        language: str = "zh",
    ) -> ScriptGenerationResult:
        lines = list(transcript)
        if not lines:
            lines = ["剧情即将展开，敬请期待"]

        if self._client:
            try:
                result = self._client.responses.create(
                    model=self._model,
                    temperature=self._temperature,
                    response_format={
                        "type": "json_schema",
                        "json_schema": {
                            "name": "VideoNarrationScript",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "bgm_theme": {"type": "string"},
                                    "segments": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "text": {"type": "string"},
                                                "emotion": {"type": "string"},
                                                "keywords": {
                                                    "type": "array",
                                                    "items": {"type": "string"},
                                                },
                                            },
                                            "required": ["text"],
                                        },
                                    },
                                },
                                "required": ["segments"],
                            },
                        },
                    },
                    input=[
                        {
                            "role": "system",
                            "content": [
                                {
                                    "type": "text",
                                    "text": (
                                        "你是一名中文短视频解说脚本编剧，需要把电视剧对白转成 3-5 段有节奏的口播稿，"
                                        "并给出对应情绪与关键词。"
                                    ),
                                }
                            ],
                        },
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": (
                                        f"语言：{language}，目标时长 {target_duration} 秒。\n"
                                        f"剧集关键对白：\n" + "\n".join(f"- {line}" for line in lines)
                                    ),
                                }
                            ],
                        },
                    ],
                )
                payload = self._extract_json(result)
                if payload:
                    return self._json_to_segments(payload, target_duration)
            except Exception:  # pragma: no cover - 调用失败回退
                pass

        return self._fallback(lines, target_duration)

    def _extract_json(self, response) -> dict | None:
        try:
            chunks = []
            for item in getattr(response, "output", []):
                for content in getattr(item, "content", []):
                    text = getattr(content, "text", None)
                    if text:
                        chunks.append(text)
            raw = "".join(chunks).strip()
            if raw:
                return json.loads(raw)
        except json.JSONDecodeError:
            return None
        return None

    def _json_to_segments(self, payload: dict, target_duration: int) -> ScriptGenerationResult:
        raw_segments = payload.get("segments", [])
        count = max(len(raw_segments), 1)
        duration_per_segment = max(target_duration / count, 8)
        segments: list[ScriptSegment] = []
        for idx, item in enumerate(raw_segments, start=1):
            text = item.get("text", "").strip() or "（内容待补充）"
            start = (idx - 1) * duration_per_segment
            end = min(idx * duration_per_segment, target_duration)
            segments.append(
                ScriptSegment(
                    order=idx,
                    text=text,
                    start=start,
                    end=end,
                    emotion=item.get("emotion"),
                    keywords=item.get("keywords") or [],
                )
            )
        theme_idx = len(segments) % len(self.THEMES)
        theme = payload.get("bgm_theme") or self.THEMES[theme_idx][0]
        return ScriptGenerationResult(segments=segments, bgm_theme=theme)

    def _fallback(self, lines: list[str], target_duration: int) -> ScriptGenerationResult:
        duration_per_segment = max(target_duration / max(len(lines), 1), 10)
        segments: list[ScriptSegment] = []
        for idx, line in enumerate(lines, start=1):
            start = (idx - 1) * duration_per_segment
            end = min(idx * duration_per_segment, target_duration)
            segments.append(
                ScriptSegment(
                    order=idx,
                    text=f"{line}（短视频解说强化）",
                    start=start,
                    end=end,
                    emotion="dramatic" if idx % 2 == 0 else "calm",
                    keywords=["角色", "冲突", f"节拍{idx}"],
                )
            )

        theme_idx = (len(lines) + target_duration) % len(self.THEMES)
        theme_slug, _ = self.THEMES[theme_idx]
        return ScriptGenerationResult(segments=segments, bgm_theme=theme_slug)
