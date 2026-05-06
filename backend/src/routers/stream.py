import asyncio
import json
import uuid
from collections.abc import AsyncGenerator

from fastapi import APIRouter, HTTPException, Request
from loguru import logger
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from dependencies.event_handler import MESSAGE_STREAM_DELAY, Event, EventHandlerDep, SseEvent

router = APIRouter(prefix="/stream", tags=["stream"], responses={404: {"description": "Not found"}})


class StreamRequestData(BaseModel):
    stream_id: str
    reader_id: str | None = None

@router.get(
    "",
    response_model=SseEvent,
    # ToDo: SseEvent is not marked as "text/event-stream" in the OpenAPI schema, 
    # but at least included as a type. fine for now
    responses={
        200: {"content": {"text/event-stream": SseEvent.model_json_schema()}},
    },
)
async def message_stream(
    event_handler: EventHandlerDep,
    request: Request,
    stream_id: str | None = None,
    reader_id: str | None = None,
):
    logger.debug(f"Message stream {request}, {stream_id}, {reader_id}")
    if not stream_id:
        stream_id = str(uuid.uuid4())

    async def event_generator() -> AsyncGenerator[SseEvent]:
        try:
            while True:
                if await request.is_disconnected():
                    break
                if await event_handler.message_length(stream_id):
                    message = await event_handler.pop_first_message_from_queue(stream_id)
                    if message["event"] != Event.ALIVE.value:
                        logger.debug(f"Sending message: {stream_id} {str(message)[:100]}")
                    message["data"] = json.dumps(message["data"])
                    yield message
                await asyncio.sleep(MESSAGE_STREAM_DELAY)
        finally:
            # Clean up the message queue when the stream is closed
            await event_handler.delete_message_queue(stream_id)
            logger.debug(f"Deleted message queue for stream_id: {stream_id}")

    await event_handler.create_message_queue(stream_id)
    await event_handler.add_subscription(stream_id, stream_id)
    if reader_id:
        await event_handler.add_subscription(stream_id, reader_id)
    return EventSourceResponse(content=event_generator(), media_type="text/event-stream")


@router.post("/subscription")
async def add_subscription(stream_data: StreamRequestData, event_handler: EventHandlerDep):
    
    if not await event_handler.has_stream_id(stream_data.stream_id):
        raise HTTPException(status_code=404, detail={"error": "Stream ID does not exist"})
    if not stream_data.reader_id:
        raise HTTPException(status_code=400, detail={"error": "Reader ID is required"})
    await event_handler.add_subscription(stream_data.stream_id, stream_data.reader_id)
    return {"message": f"Subscription added for reader {stream_data.reader_id} on stream {stream_data.stream_id}"}


@router.delete("/subscription")
async def delete_subscription(stream_data: StreamRequestData, event_handler: EventHandlerDep):
    if not await event_handler.has_stream_id(stream_data.stream_id):
        raise HTTPException(status_code=404, detail={"error": "Stream ID does not exist"})
    if not stream_data.reader_id:
        raise HTTPException(status_code=400, detail={"error": "Reader ID is required"})
    if not await event_handler.has_subscription(stream_data.stream_id, stream_data.reader_id):
        raise HTTPException(status_code=404, detail={"error": "Subscription does not exist"})
    await event_handler.delete_subscription(stream_data.stream_id, stream_data.reader_id)
    return {"message": f"Subscription removed for reader {stream_data.reader_id} on stream {stream_data.stream_id}"}
