"""Runtime settings for the project."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    openai_api_key: str = ""
    nvidia_api_key: str = ""
    cohere_api_key: str = ""
    database_url: str = "postgresql://postgres:postgres@localhost:5432/startup_radar"
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    langsmith_api_key: str = ""
    langsmith_project: str = "nvidia-startup-ai-radar"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
