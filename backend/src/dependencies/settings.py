import pathlib
from functools import lru_cache
from pathlib import Path
from typing import Annotated

from fastapi import Depends
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    frontend_host: str = "localhost"
    database_uri: str
    log_level: str = "WARN"
    sentry_dsn: str = ""
    features_openai_api_key: str = ""
    asset_path: Path = "./data/assets"
    commit_hash: str = "unknown"

    model_config = SettingsConfigDict(env_file=pathlib.Path(__file__).parent.parent / ".env")


@lru_cache
def get_settings() -> Settings:
    """
    Reads the configuration settings from environment variables and returns a Settings object.
    :return: Settings object containing the configuration settings.
    """
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]
