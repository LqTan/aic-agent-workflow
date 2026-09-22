from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    database_url: str = Field(
        default="sqlite:///./data/aic.db",
        alias="DATABASE_URL",
    )

    kis_data_root: Path = Field(default=Path("./data/aic"), alias="KIS_DATA_ROOT")
    kis_index_root: Path = Field(
        default=Path("./data/search_index"),
        alias="KIS_INDEX_ROOT",
    )
    kis_domain_taxonomy: Path | None = Field(
        default=None,
        alias="KIS_DOMAIN_TAXONOMY",
    )
    kis_demo_mode: bool = Field(default=True, alias="KIS_DEMO_MODE")
    kis_clip_model: str = Field(default="ViT-B-32", alias="KIS_CLIP_MODEL")
    kis_clip_pretrained: str = Field(default="openai", alias="KIS_CLIP_PRETRAINED")

    kis_llm_api_key: str = Field(default="", alias="KIS_LLM_API_KEY")
    kis_llm_endpoint: str = Field(default="", alias="KIS_LLM_ENDPOINT")
    kis_llm_model: str = Field(default="", alias="KIS_LLM_MODEL")

    kis_max_video_size: int = Field(
        default=2 * 1024 * 1024 * 1024,
        alias="KIS_MAX_VIDEO_SIZE",
    )

    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    app_log_level: str = Field(default="INFO", alias="APP_LOG_LEVEL")
    app_cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000"],
        alias="APP_CORS_ORIGINS",
    )

    def resolved_data_root(self) -> Path:
        path = Path(self.kis_data_root)
        return path if path.is_absolute() else (Path.cwd() / path).resolve()

    def resolved_index_root(self) -> Path:
        path = Path(self.kis_index_root)
        return path if path.is_absolute() else (Path.cwd() / path).resolve()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
