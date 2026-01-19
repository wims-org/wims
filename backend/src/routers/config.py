from fastapi import APIRouter, Request

from dependencies.backend_service import ConfigResponseModel
from routers.utils import get_bs

router = APIRouter(prefix="/config", tags=["Config"])


@router.get("", response_model=ConfigResponseModel)
async def config(request: Request):
    """
    Return an object showing enabled/disable options in the backend
    """
    return get_bs(request).get_config()
