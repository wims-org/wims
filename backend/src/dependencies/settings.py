import pathlib
from functools import lru_cache
from pathlib import Path
from sys import exit
from typing import Annotated

from fastapi import Depends
from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from models.api import WebhookEvent


class Settings(BaseSettings):
    data_path: Path = "/data"
    database_uri: str
    features_openai_api_key: str = ""
    frontend_host: str = "localhost"
    log_level: str = "WARN"
    sentry_dsn: str = ""

    # Webhook settings
    webhook_url: str = ""
    webhook_events: list[WebhookEvent] = [x.value for x in WebhookEvent]

    # usually no need to change
    asset_uri_prefix: str = "/assets"
    commit_hash: str = "unknown"

    model_config = SettingsConfigDict(env_file=pathlib.Path(__file__).parent.parent / ".env")


@lru_cache
def get_settings() -> Settings:
    """
    Reads the configuration settings from environment variables and returns a Settings object.
    :return: Settings object containing the configuration settings.
    """
    try:
        return Settings()
    except ValidationError as ex:
        print("Your .env file is invalid!")
        print(ex)
        exit(1)


SettingsDep = Annotated[Settings, Depends(get_settings)]
