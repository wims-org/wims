from fastapi import APIRouter, Request

from dependencies.backend_service import BackendService, ConfigResponseModel

router = APIRouter(prefix="/config", tags=["config"])


def get_bs(request: Request) -> BackendService:
    return request.app.state.backend_service


@router.get("/", response_model=ConfigResponseModel)
async def config(request: Request):
    return get_bs(request).get_config()
