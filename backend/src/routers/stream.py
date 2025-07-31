import asyncio
import json
import uuid

from fastapi import APIRouter, Request
from loguru import logger
from sse_starlette.sse import EventSourceResponse

from dependencies.backend_service import MESSAGE_STREAM_DELAY, Event

router = APIRouter(prefix="/stream", tags=["stream"], responses={404: {"description": "Not found"}})


@router.get("")
async def message_stream(request: Request, reader: str):
    logger.debug(f"Message stream {request}, {reader}")
    stream_id = str(uuid.uuid4())
    await request.app.state.backend_service.create_message_queue(stream_id)
    await request.app.state.backend_service.add_subscription(stream_id, reader)

    async def event_generator():
        while True:
            # If client was closed the connection
            if await request.is_disconnected():
                break
            # Checks for new messages and return them to client if any
            if await request.app.state.backend_service.message_length(stream_id):
                message = await request.app.state.backend_service.pop_first_message_from_queue(stream_id)
                if message["event"] != Event.ALIVE.value:
                    logger.debug(f"Sending message: {str(message)[:100]}")
                message["data"] = json.dumps(message["data"])
                yield message
            await asyncio.sleep(MESSAGE_STREAM_DELAY)

    return EventSourceResponse(event_generator())
