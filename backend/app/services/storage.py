from __future__ import annotations

from pathlib import Path
import shutil

from fastapi import UploadFile

from app.schemas.tasks import VideoAsset


class FileStorageService:
    """本地文件存储，模拟对象存储能力."""

    def __init__(self, media_root: Path, public_prefix: str = "/media") -> None:
        self._media_root = media_root
        self._media_root.mkdir(parents=True, exist_ok=True)
        self._public_prefix = public_prefix.rstrip("/")

    def save_upload(self, task_id: str, file: UploadFile | None) -> VideoAsset | None:
        if not file:
            return None
        filename = file.filename or "source.mp4"
        dest = self._allocate_path(task_id, filename)
        with dest.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return self.build_asset(task_id, filename, local_path=dest)

    def duplicate_asset(self, task_id: str, source_path: Path, filename: str) -> VideoAsset:
        dest = self._allocate_path(task_id, filename)
        shutil.copy(source_path, dest)
        return self.build_asset(task_id, filename, local_path=dest)

    def allocate_file(self, task_id: str, filename: str) -> Path:
        return self._allocate_path(task_id, filename)

    def _allocate_path(self, task_id: str, filename: str) -> Path:
        task_dir = self._media_root / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        return task_dir / filename

    def build_asset(self, task_id: str, filename: str, *, local_path: Path) -> VideoAsset:
        url = f"{self._public_prefix}/{task_id}/{filename}"
        return VideoAsset(url=url, local_path=str(local_path))
