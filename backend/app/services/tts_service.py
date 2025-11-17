from __future__ import annotations

import math
import wave
from pathlib import Path
from typing import Iterable

import numpy as np

from app.schemas.tasks import NarrationAsset, ScriptSegment
from app.services.storage import FileStorageService


class TTSService:
    def __init__(self, storage: FileStorageService, sample_rate: int = 22050) -> None:
        self._storage = storage
        self._sample_rate = sample_rate

    def synthesize_segments(
        self,
        task_id: str,
        segments: Iterable[ScriptSegment],
        *,
        language: str,
        voice_profile: str,
    ) -> list[NarrationAsset]:
        assets: list[NarrationAsset] = []
        for segment in segments:
            filename = f"narration_{segment.order}.wav"
            path = self._storage.allocate_file(task_id, filename)
            self._write_placeholder_audio(path, duration=max(segment.end - segment.start, 5))
            asset = self._storage.build_asset(task_id, filename, local_path=path)
            assets.append(
                NarrationAsset(
                    url=asset.url,
                    locale=language,
                    voice_profile=voice_profile,
                    duration=max(segment.end - segment.start, 5),
                )
            )
        return assets

    def _write_placeholder_audio(self, path: Path, duration: float) -> None:
        total_frames = int(self._sample_rate * duration)
        amplitude = 32767
        freq = 220
        t = np.linspace(0, duration, total_frames)
        data = (amplitude * np.sin(2 * math.pi * freq * t)).astype(np.int16)
        with wave.open(str(path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self._sample_rate)
            wav_file.writeframes(data.tobytes())
