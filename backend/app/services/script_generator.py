from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

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

    def generate(self, transcript: Iterable[str], *, target_duration: int = 90) -> ScriptGenerationResult:
        lines = list(transcript)
        if not lines:
            lines = ["剧情即将展开，敬请期待"]

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
