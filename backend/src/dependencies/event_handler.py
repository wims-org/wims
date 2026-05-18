import asyncio
from collections.abc import AsyncGenerator
from typing import Annotated

import pydantic
from fastapi import Depends, Request

from dependencies import settings
from models.api import Event, SseEvent, SseEventData

settings = settings.get_settings()


class MessageQueue(pydantic.BaseModel):
    subscriptions: set[str] = pydantic.Field(default_factory=set)
    message_queue: list = pydantic.Field(default_factory=list)


class EventHandler:
    """A class for handling events."""

    def __init__(self):
        self._queues_lock = asyncio.Lock()
        self.__message_queues: dict[str, MessageQueue] = {}
        asyncio.create_task(self.push_heartbeats())

    def get_alive_message(self) -> SseEvent:
        return SseEvent(
            data=SseEventData(reader_id=None, data={"message": "connection alive"}).model_dump(mode="json"),
            event=Event.ALIVE,
        )

    async def push_heartbeats(self):
        while True:
            await self.append_message_to_all_queues(message=self.get_alive_message())
            await asyncio.sleep(5)

    async def has_stream_id(self, stream_id: str) -> bool:
        async with self._queues_lock:
            return stream_id in self.__message_queues

    async def get_message_queue(self, stream_id: str) -> MessageQueue:
        async with self._queues_lock:
            return self.__message_queues.get(stream_id).message_queue if stream_id in self.__message_queues else []

    async def pop_first_message_from_queue(self, stream_id: str) -> SseEvent | None:
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

    async def append_message_to_all_queues_with_reader(self, reader: str, message: SseEvent):
        async with self._queues_lock:
            for stream_id in self.__message_queues:
                if reader in self.__message_queues[stream_id].subscriptions:
                    msg = message.model_dump(mode="json")
                    if isinstance(msg["data"], dict):
                        msg["data"]["stream_id"] = str(stream_id)
                    self.__message_queues[stream_id].message_queue.append(msg)

    async def append_message_to_all_queues(self, message: SseEvent):
        async with self._queues_lock:
            for stream_id in list(self.__message_queues.keys()):
                if len(self.__message_queues[stream_id].message_queue) >= 10:
                    self.__message_queues[stream_id].message_queue = []
                    continue
                msg = message.model_dump(mode="json")
                msg["data"]["stream_id"] = str(stream_id)
                msg["data"]["subscriptions"] = list(self.__message_queues[stream_id].subscriptions)
                self.__message_queues[stream_id].message_queue.append(msg)

    async def append_message_to_queue(self, stream_id: str, message: SseEvent):
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
