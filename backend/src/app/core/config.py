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

    kis_data_root: Path = Field(default=Path("./data"), alias="KIS_DATA_ROOT")
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

    kis_embedding_provider: str = Field(
        default="remote",
        alias="KIS_EMBEDDING_PROVIDER",
    )

    kis_embedding_url: str = Field(
        default="",
        alias="KIS_EMBEDDING_URL",
    )

    kis_embedding_api_key: str = Field(
        default="",
        alias="KIS_EMBEDDING_API_KEY",
    )

    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    app_log_level: str = Field(default="INFO", alias="APP_LOG_LEVEL")
    app_cors_origins: str = Field(
        default="http://localhost:3000",
        alias="APP_CORS_ORIGINS",
    )
    app_public_base_url: str = Field(
        default="http://localhost:8000",
        alias="APP_PUBLIC_BASE_URL",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse ``app_cors_origins`` (JSON array, comma string, or single url)."""
        value = (self.app_cors_origins or "").strip()
        if not value:
            return []
        if value.startswith("["):
            import json

            parsed = json.loads(value)
            return [str(item).strip() for item in parsed if str(item).strip()]
        return [item.strip() for item in value.split(",") if item.strip()]

    def resolved_data_root(self) -> Path:
        path = Path(self.kis_data_root)
        return path if path.is_absolute() else (Path.cwd() / path).resolve()

    def resolved_index_root(self) -> Path:
        path = Path(self.kis_index_root)
        return path if path.is_absolute() else (Path.cwd() / path).resolve()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
