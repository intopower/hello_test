from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用级配置，读取环境变量."""

    app_name: str = "TV Commentary Studio"
    environment: str = "development"
    openai_api_key: str | None = None
    object_storage_bucket: str = "media"
    task_expiration_minutes: int = 60 * 24

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


def get_settings() -> Settings:
    return Settings()


settings = get_settings()
