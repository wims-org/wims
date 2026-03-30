import asyncio
import enum
import uuid
from collections.abc import AsyncGenerator
from typing import Annotated

import pydantic
from fastapi import Depends, Request

from dependencies import settings

settings = settings.get_settings()

MESSAGE_STREAM_DELAY = 0.3  # second
MESSAGE_STREAM_RETRY_TIMEOUT = 15000  # millisecond


class MessageQueue(pydantic.BaseModel):
    subscriptions: set[str] = pydantic.Field(default_factory=set)
    message_queue: list = pydantic.Field(default_factory=list)


class Event(enum.Enum):
    SCAN = "SCAN"
    COMPLETION = "COMPLETION"
    ALIVE = "ALIVE"
    ERROR = "ERROR"


class SseMessage(pydantic.BaseModel):
    class SseMessageData(pydantic.BaseModel):
        reader_id: str | None = None
        rfid: str | None = None  # Todo rename RFID to tag id
        data: dict | None = None
        stream_id: str | None = None

    event: Event
    data: SseMessageData | dict
    id: str = str(uuid.uuid4())
    retry: int = MESSAGE_STREAM_RETRY_TIMEOUT


class EventHandler:
    """A class for handling events."""

    def __init__(self):
        self._queues_lock = asyncio.Lock()
        self.__message_queues: dict[str, MessageQueue] = {}
        asyncio.create_task(self.push_heartbeats())

    async def push_heartbeats(self):
        message = SseMessage(
            data=SseMessage.SseMessageData(reader_id=None, data={"message": "connection alive"}).model_dump(
                mode="json"
            ),
            event=Event.ALIVE,
        )
        while True:
            await self.append_message_to_all_queues(message=message)
            await asyncio.sleep(5)

    async def has_stream_id(self, stream_id: str) -> bool:
        async with self._queues_lock:
            return stream_id in self.__message_queues

    async def get_message_queue(self, stream_id: str) -> MessageQueue:
        async with self._queues_lock:
            return self.__message_queues.get(stream_id).message_queue if stream_id in self.__message_queues else []

    async def pop_first_message_from_queue(self, stream_id: str) -> SseMessage | None:
        async with self._queues_lock:
            if stream_id in self.__message_queues and self.__message_queues.get(stream_id).message_queue:
                res = self.__message_queues.get(stream_id).message_queue.pop(0)
            else:
                res = None
        return res

    async def message_length(self, stream_id: str) -> int:
        async with self._queues_lock:
            messages_len = 0
            if stream_id in self.__message_queues:
                messages_len = len(self.__message_queues[stream_id].message_queue)
        return messages_len

    async def create_message_queue(self, stream_id: str):
        async with self._queues_lock:
            if stream_id not in self.__message_queues:
                self.__message_queues[stream_id] = MessageQueue(subscriptions=set())

    async def has_subscription(self, stream_id: str, reader_id: str) -> bool:
        async with self._queues_lock:
            return stream_id in self.__message_queues and reader_id in self.__message_queues[stream_id].subscriptions

    async def add_subscription(self, stream_id: str, reader: str):
        async with self._queues_lock:
            if stream_id in self.__message_queues:
                self.__message_queues[stream_id].subscriptions.add(reader)

    async def delete_subscription(self, stream_id: str, reader: str):
        async with self._queues_lock:
            if stream_id in self.__message_queues:
                self.__message_queues[stream_id].subscriptions.discard(reader)

    async def delete_message_queue(self, stream_id: str):
        async with self._queues_lock:
            if stream_id in self.__message_queues:
                del self.__message_queues[stream_id]

    async def append_message_to_all_queues_with_reader(self, reader: str, message: SseMessage):
        async with self._queues_lock:
            for stream_id in self.__message_queues:
                if reader in self.__message_queues[stream_id].subscriptions:
                    msg = message.model_dump(mode="json")
                    if isinstance(msg["data"], dict):
                        msg["data"]["stream_id"] = str(stream_id)
                    self.__message_queues[stream_id].message_queue.append(msg)

    async def append_message_to_all_queues(self, message: SseMessage):
        async with self._queues_lock:
            for stream_id in list(self.__message_queues.keys()):
                if len(self.__message_queues[stream_id].message_queue) >= 10:
                    del self.__message_queues[stream_id]
                    continue
                msg = message.model_dump(mode="json")
                msg["data"]["stream_id"] = str(stream_id)
                msg["data"]["subscriptions"] = list(self.__message_queues[stream_id].subscriptions)
                self.__message_queues[stream_id].message_queue.append(msg)

    async def append_message_to_queue(self, stream_id: str, message: SseMessage):
        async with self._queues_lock:
            if stream_id in self.__message_queues:
                msg = message.model_dump(mode="json")
                msg["data"]["stream_id"] = str(stream_id)
                self.__message_queues[stream_id].message_queue.append(msg)


class EventHandlerFactory:
    _instance: EventHandler | None = None

    @classmethod
    def get_instance(cls) -> EventHandler:
        if cls._instance is None:
            cls._instance = EventHandler()
        return cls._instance


# Dependency
async def event_handler_dependency() -> AsyncGenerator[EventHandler]:
    async with asyncio.Lock():
        yield EventHandlerFactory.get_instance()


EventHandlerDep = Annotated[EventHandler, Depends(event_handler_dependency)]


async def get_event_handler(request: Request, event_handler: EventHandlerDep) -> None:
    return event_handler
