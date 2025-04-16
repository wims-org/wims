from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter(prefix="/healthz", tags=["healthz"])


@router.get("", response_class=PlainTextResponse)
async def healthz():
    # TODO: Actually check things like DB and MQTT connectivity and then return appropiate status code
    return "OK"
