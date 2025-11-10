import asyncio
import enum
import json
import uuid
from pathlib import Path

import openai
import pydantic
from loguru import logger

from database_connector import MongoDBConnector
from modules import chatgpt
from modules.camera import Camera
from utils import find

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


class ConfigResponseModel(pydantic.BaseModel):
    database_connected: bool
    llm_enabled: bool
    camera_enabled: bool


class BackendService:
    def __init__(self, db_config, config):
        self.config = config
        self.db = MongoDBConnector(
            uri=f"mongodb://{db_config.get('host', 'localhost')}:{db_config.get('port', '27017')}",
            database=db_config.get("database", "inventory"),
        )

        self._queues_lock = asyncio.Lock()
        self.__message_queues: dict[str, MessageQueue] = {}

        # Read the schema from the file
        with open(Path(__file__).parent.parent.parent / "schemas" / "llm_schema.json") as schema_file:
            schema = json.load(schema_file)

        try:
            self.llm_completion = chatgpt.ChatGPT(
                api_key=find(key := "features.openai.api_key", config), response_schema=schema
            )
        except (KeyError, TypeError, openai.OpenAIError) as e:
            logger.error(f"Error getting config key {key}, check config file and environment variables: {e}")
            self.llm_completion = None

        try:
            self.camera = Camera(find(key := "camera.url", config))
        except (KeyError, TypeError, openai.OpenAIError) as e:
            logger.error(f"Error getting config key {key}, check config file and environment variables: {e}")
            self.camera = None
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

    def is_ready(self) -> bool:
        return self.db.is_connected()
