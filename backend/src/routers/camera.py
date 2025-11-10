from fastapi import APIRouter, HTTPException, Request

from dependencies.backend_service import BackendService

router = APIRouter(prefix="/camera", tags=["complecameration"], responses={404: {"description": "Not found"}})


def get_bs(request: Request) -> BackendService:
    return request.app.state.backend_service


@router.get("")
def getCameraUrl(request: Request):
    bs = get_bs(request)
    if not bs.camera:
        raise HTTPException(status_code=404, detail="Camera is not initialized")
    return {"url": bs.camera.url}


@router.get("/last_image")
def getLastImage(request: Request):
    bs = get_bs(request)
    if not bs.camera or not bs.camera.last_image:
        raise HTTPException(status_code=404, detail="No last image available from camera")
    return {"image": bs.camera.last_image}


@router.get("/snapshot")
def getSnapshot(request: Request):
    bs = get_bs(request)
    if not bs.camera:
        raise HTTPException(status_code=404, detail="Camera is not initialized")
    res = {"images": bs.camera.get_camera_image_urls()}
    if not res["images"]:
        raise HTTPException(status_code=404, detail="No images captured from camera")
    return res
