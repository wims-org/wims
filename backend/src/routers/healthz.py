from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse

router = APIRouter(prefix="/healthz", tags=["healthz"])


@router.get("", response_class=PlainTextResponse)
async def healthz():
    return "OK"


@router.get("/ready", response_class=PlainTextResponse)
async def ready(request: Request):
    backend_service = request.app.state.backend_service
    if not backend_service.is_ready():
        return PlainTextResponse("Service not ready", status_code=503)
    return "OK"
