from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Fail closed: development CORS requires an explicit environment selection.
    app_env: Literal["development", "test", "production"] = "production"
    cors_allowed_origins_raw: str = "http://localhost:3000,http://127.0.0.1:3000"
    geocoding_provider: Literal["nominatim"] = "nominatim"
    geocoding_base_url: str = "https://nominatim.openstreetmap.org"
    geocoding_user_agent: str = "yasam-kodu-development/0.1 (development@localhost)"
    geocoding_timeout_seconds: float = 5.0

    @property
    def cors_allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins_raw.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
