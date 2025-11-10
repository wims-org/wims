from fastapi import APIRouter, Request

from dependencies.backend_service import ConfigResponseModel
from routers.utils import get_bs

router = APIRouter(prefix="/config", tags=["config"])


@router.get("/", response_model=ConfigResponseModel)
async def config(request: Request):
    return get_bs(request).get_config()
