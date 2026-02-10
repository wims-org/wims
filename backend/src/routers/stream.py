import asyncio
import json
import uuid

from fastapi import APIRouter, HTTPException, Request
from loguru import logger
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from dependencies.backend_service import MESSAGE_STREAM_DELAY, Event

router = APIRouter(prefix="/stream", tags=["stream"], responses={404: {"description": "Not found"}})


class StreamRequestData(BaseModel):
    stream_id: str
    reader_id: str | None = None


@router.get("")
async def message_stream(request: Request, stream_id: str | None = None, reader_id: str | None = None):
    logger.debug(f"Message stream {request}, {stream_id}, {reader_id}")
    backend_service = request.app.state.backend_service
    if not stream_id:
        stream_id = str(uuid.uuid4())

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                if await backend_service.message_length(stream_id):
                    message = await backend_service.pop_first_message_from_queue(stream_id)
                    if message["event"] != Event.ALIVE.value:
                        logger.debug(f"Sending message: {stream_id} {str(message)[:100]}")
                    message["data"] = json.dumps(message["data"])
                    yield message
                await asyncio.sleep(MESSAGE_STREAM_DELAY)
        finally:
            # Clean up the message queue when the stream is closed
            await backend_service.delete_message_queue(stream_id)
            logger.debug(f"Deleted message queue for stream_id: {stream_id}")

    await backend_service.create_message_queue(stream_id)
    await backend_service.add_subscription(stream_id, stream_id)
    if reader_id:
        await backend_service.add_subscription(stream_id, reader_id)
    return EventSourceResponse(event_generator())


@router.post("/subscription")
async def add_subscription(request: Request, stream_data: StreamRequestData):
    backend_service = request.app.state.backend_service
    if not await backend_service.has_stream_id(stream_data.stream_id):
        raise HTTPException(status_code=404, detail={"error": "Stream ID does not exist"})
    if not stream_data.reader_id:
        raise HTTPException(status_code=400, detail={"error": "Reader ID is required"})
    await backend_service.add_subscription(stream_data.stream_id, stream_data.reader_id)
    return {"message": f"Subscription added for reader {stream_data.reader_id} on stream {stream_data.stream_id}"}


@router.delete("/subscription")
async def delete_subscription(request: Request, stream_data: StreamRequestData):
    backend_service = request.app.state.backend_service
    if not await backend_service.has_stream_id(stream_data.stream_id):
        raise HTTPException(status_code=404, detail={"error": "Stream ID does not exist"})
    if not stream_data.reader_id:
        raise HTTPException(status_code=400, detail={"error": "Reader ID is required"})
    if not await backend_service.has_subscription(stream_data.stream_id, stream_data.reader_id):
        raise HTTPException(status_code=404, detail={"error": "Subscription does not exist"})
    await backend_service.delete_subscription(stream_data.stream_id, stream_data.reader_id)
    return {"message": f"Subscription removed for reader {stream_data.reader_id} on stream {stream_data.stream_id}"}
