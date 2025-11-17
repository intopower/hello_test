from __future__ import annotations

from functools import lru_cache

from app.core.config import settings
from app.core.hardware import detect_hardware
from app.services.service_factory import (
    build_script_service,
    build_transcription_service,
    build_tts_service,
    encoder_for_accelerator,
)
from app.services.storage import FileStorageService
from app.services.task_service import get_task_service
from app.services.video_editor import VideoEditingService
from app.workflows.pipeline import PipelineOrchestrator


@lru_cache(maxsize=1)
def get_storage_service() -> FileStorageService:
    return FileStorageService(settings.media_root, settings.media_url_prefix)


@lru_cache(maxsize=1)
def get_hardware_profile():
    return detect_hardware()


@lru_cache(maxsize=1)
def get_orchestrator() -> PipelineOrchestrator:
    task_service = get_task_service()
    storage = get_storage_service()
    hardware = get_hardware_profile()

    transcription = build_transcription_service(settings, hardware)
    script_service = build_script_service(settings)
    tts_service = build_tts_service(settings, storage)
    video_editor = VideoEditingService(
        storage,
        preferred_encoder=encoder_for_accelerator(hardware.accelerator),
    )

    return PipelineOrchestrator(
        task_service=task_service,
        storage=storage,
        transcription=transcription,
        script_service=script_service,
        video_editor=video_editor,
        tts_service=tts_service,
    )
