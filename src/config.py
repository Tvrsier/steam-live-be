from __future__ import annotations

from typing import Literal, Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field

Environment = Literal["local", "dev", "prod"]
StorageLevels = Literal["local", "s3"]


class Settings(BaseSettings):
    # Ambiente
    environment: Environment = "local"

    # Storage: locale o S3
    storage_level: StorageLevels = "local"

    # Directory locale che conterrà i JSON
    local_path: str = "./resources/data/"

    # S3
    s3_bucket: Optional[str] = None
    s3_access_key: Optional[str] = None
    s3_secret_key: Optional[str] = None
    s3_region: Optional[str] = None

    # Steam
    steam_api_key: Optional[str] = None

    # App Steam specifiche da tracciare (opzionale)
    tracked_app_ids: List[int] = Field(default_factory=list)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
