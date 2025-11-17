from __future__ import annotations

from app.core.config import Settings
from app.core.hardware import Accelerator, HardwareProfile
from app.services.script_generator import (
    OpenAIScriptGenerationService,
    RuleBasedScriptGenerationService,
    ScriptGenerationProvider,
)
from app.services.storage import FileStorageService
from app.services.transcription import (
    LocalTranscriptionService,
    OpenAITranscriptionService,
    TranscriptionProvider,
)
from app.services.tts_service import OpenAITTSService, ProceduralTTSService, TTSProvider


def build_transcription_service(settings: Settings, hardware: HardwareProfile) -> TranscriptionProvider:
    if settings.openai_api_key:
        return OpenAITranscriptionService(
            api_key=settings.openai_api_key,
            model=settings.openai_transcription_model,
            default_language=settings.default_language,
        )
    return LocalTranscriptionService(
        device_hint=hardware.accelerator.value,
        default_language=settings.default_language,
    )


def build_script_service(settings: Settings) -> ScriptGenerationProvider:
    if settings.openai_api_key:
        return OpenAIScriptGenerationService(
            api_key=settings.openai_api_key,
            model=settings.openai_script_model,
            temperature=settings.openai_script_temperature,
        )
    return RuleBasedScriptGenerationService()


def build_tts_service(
    settings: Settings,
    storage: FileStorageService,
) -> TTSProvider:
    if settings.openai_api_key:
        return OpenAITTSService(
            storage,
            api_key=settings.openai_api_key,
            model=settings.openai_tts_model,
        )
    return ProceduralTTSService(storage)


def encoder_for_accelerator(accelerator: Accelerator) -> str:
    mapping = {
        Accelerator.CUDA: "h264_nvenc",
        Accelerator.ROCM: "h264_vaapi",
        Accelerator.METAL: "h264_videotoolbox",
    }
    return mapping.get(accelerator, "libx264")
