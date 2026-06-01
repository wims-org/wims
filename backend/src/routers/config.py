from fastapi import APIRouter
from pydantic import BaseModel

from dependencies.settings import SettingsDep

router = APIRouter(prefix="/config", tags=["config"])


class ConfigResponseModel(BaseModel):
    llm_enabled: bool
    commit_hash: str
    send_telemetry: bool
    sentry_dsn_frontend: str


@router.get("/", response_model=ConfigResponseModel)
async def config(settings: SettingsDep):
    return ConfigResponseModel(
        llm_enabled=bool(settings.features_openai_api_key),
        commit_hash=settings.commit_hash,
        send_telemetry=settings.send_telemetry,
        sentry_dsn_frontend=settings.sentry_dsn_frontend,
    )
