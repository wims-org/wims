from fastapi import APIRouter
from pydantic import BaseModel

from dependencies.settings import SettingsDep

router = APIRouter(prefix="/config", tags=["config"])


class ConfigResponseModel(BaseModel):
    llm_enabled: bool


@router.get("/", response_model=ConfigResponseModel)
async def config(settings: SettingsDep):
    return ConfigResponseModel(llm_enabled=bool(settings.features_openai_api_key))
