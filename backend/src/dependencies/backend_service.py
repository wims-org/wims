import asyncio
import enum
import json
import logging
import uuid
from asyncio import Event
from pathlib import Path

from pydantic import BaseModel
from wtforms import ValidationError

from database_connector import MongoDBConnector
from modules import chatgpt
from mqtt_client import MQTTClientManager, ReaderMessage
from utils import find

logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.DEBUG)


MESSAGE_STREAM_DELAY = 1  # second
MESSAGE_STREAM_RETRY_TIMEOUT = 15000  # millisecondfrom utils import find


class Event(enum.Enum):
    REDIRECT = "REDIRECT"
    COMPLETION = "COMPLETION"
    ALIVE = "ALIVE"


class SseMessage(BaseModel):
    event: Event
    data: dict
    id: str = str(uuid.uuid4())
    retry: int = MESSAGE_STREAM_RETRY_TIMEOUT

    class SseMessageData(BaseModel):
        reader_id: str
        rfid: str = None
        data: dict = None


class BackendService:
    def __init__(self, db_config, mqtt_config, config):
        self.db = MongoDBConnector(
            uri=f"mongodb://{db_config.get("host", "localhost")
                             }:{db_config.get("port", "27017")}",
            database=db_config.get("database", "inventory"),
        )
        self.mqtt_client_manager = MQTTClientManager(
            callback=self.handle_message,
            host=mqtt_config.get("broker", {}).get("host", "localhost"),
            port=mqtt_config.get("broker", {}).get("port", 1883),
        )
        self.readers: dict[str, list[dict]] = {}

        # Read the schema from the file
        with open(Path(__file__).parent.parent.parent / "schemas" / "llm_schema.json") as schema_file:
            schema = json.load(schema_file)
        self.llm_completion = chatgpt.ChatGPT(api_key=find("features.openai.api_key", config), response_schema=schema)

        asyncio.create_task(self.push_messages())

    async def handle_message(self, message, topic):
        logger.debug(f"Handle message: {message} on topic {topic}")
        try:
            msg = ReaderMessage(**json.loads(message))
            self.readers.setdefault(msg.reader_id, [])
        except (ValidationError, json.JSONDecodeError) as e:
            logger.error(f"Error parsing message: {e}, {message}")
            return
        self.readers[msg.reader_id].append(
            SseMessage(
                data=SseMessage.SseMessageData(reader_id=msg.reader_id, rfid=msg.rfid).model_dump(mode="json", exclude_none=True),
                event=Event.REDIRECT,
            ).model_dump(mode="json")
        )

    def start_mqtt(self):
        self.mqtt_client_manager.connect()

    def add_mqtt_topic(self, topic):
        self.mqtt_client_manager.add_topic(topic)

    def close(self):
        self.db.close()
        self.mqtt_client_manager.stop()

    async def push_messages(self):
        while True:
            for client in self.readers:
                message = SseMessage(
                    data=SseMessage.SseMessageData(reader_id=client, data={"message": "connection alive"}).model_dump(
                        mode="json"
                    ),
                    event=Event.ALIVE,
                ).model_dump(mode="json")
                self.readers[client].append(message)
            await asyncio.sleep(5)
