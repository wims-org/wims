from fastapi import APIRouter, HTTPException, Request, logger

from dependencies.backend_service import BackendService

router = APIRouter(prefix="/camera", tags=["complecameration"], responses={404: {"description": "Not found"}})


def get_bs(request: Request) -> BackendService:
    return request.app.state.backend_service


@router.get("")
def getCameraUrl(request: Request):
    bs = get_bs(request)
    return {"url": bs.camera.url}


@router.get("/last_image")
def getLastImage(request: Request):
    bs = get_bs(request)
    return {"image": bs.camera.last_image}


@router.get("/snapshot")
def getSnapshot(request: Request):
    res = {"images": get_bs(request).camera.get_camera_image_urls()}
    if not res["images"]:
        logger.error("No images captured from camera")
        raise HTTPException(status_code=400, detail="No images captured from camera")
    return res
