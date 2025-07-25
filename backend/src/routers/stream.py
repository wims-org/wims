import asyncio
import json

from fastapi import APIRouter, Request
from loguru import logger
from sse_starlette.sse import EventSourceResponse

from dependencies.backend_service import MESSAGE_STREAM_DELAY, Event

router = APIRouter(prefix="/stream", tags=["stream"], responses={404: {"description": "Not found"}})


@router.get("")
async def message_stream(request: Request, reader: str):
    logger.debug(f"Message stream {request}, {reader}")
    request.app.state.backend_service.readers[reader] = []

    def new_messages():
        return len(request.app.state.backend_service.readers[reader]) > 0

    async def event_generator():
        while True:
            # If client was closed the connection
            if await request.is_disconnected():
                break
            # Checks for new messages and return them to client if any
            if new_messages():
                message = request.app.state.backend_service.readers[reader].pop(0)
                if message["event"] != Event.ALIVE.value:
                    logger.debug(f"Sending message: {str(message)[:100]}")
                message["data"] = json.dumps(message["data"])
                yield message
            await asyncio.sleep(MESSAGE_STREAM_DELAY)

    return EventSourceResponse(event_generator())
