from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
from routers.utils import get_bs

router = APIRouter(prefix="", tags=["healthz"])


@router.get("/healthz", response_class=PlainTextResponse)
async def healthz():
    """
    Always HTTP 200
    """
    return "OK"


@router.get("/ready", response_class=PlainTextResponse)
async def ready(request: Request):
    """
    Check if we have a database connection
    """
    if not get_bs.is_ready():
        return PlainTextResponse("Service not ready", status_code=503)
    return "OK"
