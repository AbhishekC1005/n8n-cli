from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    OPENAI_API_KEY: str = ""
    NIM_API_KEY: str = ""
    NIM_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    N8N_API_KEY: str = ""
    N8N_BASE_URL: str = "http://localhost:5678"
    MODEL: str = "moonshotai/kimi-k2.6"
    CACHE_TTL: int = 3600
    AGENT_HOME: Path = Path.home() / ".n8n-agent"


settings = Settings()


def get_agent_home() -> Path:
    return settings.AGENT_HOME


def ensure_agent_home() -> Path:
    home = settings.AGENT_HOME
    home.mkdir(parents=True, exist_ok=True)
    (home / "cache").mkdir(exist_ok=True)
    (home / "sessions").mkdir(exist_ok=True)
    (home / "sessions" / "archive").mkdir(exist_ok=True)
    (home / "backups").mkdir(exist_ok=True)
    return home
