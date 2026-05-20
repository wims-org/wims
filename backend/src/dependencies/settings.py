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
    # mandatory
    database_uri: str
    send_telemetry: bool = False
    # features
    features_openai_api_key: str = ""
    # Webhook settings
    webhook_url: str = ""
    webhook_events: list[WebhookEvent] = [x.value for x in WebhookEvent]

    # others
    data_path: Path = "/data"
    log_level: str = "WARN"
    sentry_dsn_backend: str = "https://9f6b292159894c6983b61313779ad123@glitch.fleaz.me/4"
    sentry_dsn_frontend: str = "https://08b94672614847df87cac87c393f4a66@glitch.fleaz.me/5"

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
