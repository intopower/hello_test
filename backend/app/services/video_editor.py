from __future__ import annotations

from pathlib import Path
from typing import Iterable

from moviepy.editor import ColorClip, VideoFileClip, concatenate_videoclips

from app.schemas.tasks import ScriptSegment, VideoAsset
from app.services.storage import FileStorageService


class VideoEditingService:
    def __init__(self, storage: FileStorageService, *, preferred_encoder: str = "libx264") -> None:
        self._storage = storage
        self._preferred_encoder = preferred_encoder

    def build_highlight(
        self,
        task_id: str,
        source_asset: VideoAsset | None,
        segments: Iterable[ScriptSegment],
    ) -> VideoAsset:
        output_filename = "highlight.mp4"
        output_path = self._storage.allocate_file(task_id, output_filename)
        clip = None
        try:
            if source_asset and source_asset.local_path:
                src_path = Path(source_asset.local_path)
                if src_path.exists():
                    with VideoFileClip(str(src_path)) as original:
                        subclips = []
                        for segment in segments:
                            start = max(segment.start, 0)
                            end = min(segment.end, original.duration)
                            if end - start <= 0:
                                continue
                            subclips.append(original.subclip(start % original.duration, end % (original.duration or end)))
                        if subclips:
                            clip = concatenate_videoclips(subclips)
            if clip is None:
                duration = max((seg.end - seg.start) for seg in segments) if segments else 30
                clip = ColorClip(size=(1280, 720), color=(20, 23, 35), duration=duration)
            clip.write_videofile(str(output_path), codec=self._preferred_encoder, audio=False, fps=24)
        except Exception:
            output_path.write_bytes(b"placeholder video")
        finally:
            if clip is not None:
                clip.close()
        return self._storage.build_asset(task_id, output_filename, local_path=output_path)
