from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用级配置，读取环境变量."""

    app_name: str = "TV Commentary Studio"
    environment: str = "development"
    openai_api_key: str | None = None
    object_storage_bucket: str = "media"
    task_expiration_minutes: int = 60 * 24
    media_url_prefix: str = "/media"

    base_dir: Path = Path(__file__).resolve().parents[2]
    media_root: Path = base_dir / "storage" / "media"
    data_root: Path = base_dir / "storage" / "data"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


def get_settings() -> Settings:
    settings = Settings()
    settings.media_root.mkdir(parents=True, exist_ok=True)
    settings.data_root.mkdir(parents=True, exist_ok=True)
    return settings


settings = get_settings()
