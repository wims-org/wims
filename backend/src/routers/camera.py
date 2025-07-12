
from fastapi import APIRouter, Request, logger
import loguru

from dependencies.backend_service import BackendService

router = APIRouter(prefix="/camera",
                   tags=["complecameration"], responses={404: {"description": "Not found"}})


def get_bs(request: Request) -> BackendService:
    return request.app.state.backend_service


@router.get("")
def getCameraUrl(request:Request):
    bs = get_bs(request)
    return {"url": bs.camera.url}


@router.get("/last_image")
def getLastImage(request:Request):
    bs = get_bs(request)
    return {"image": bs.camera.last_image}
