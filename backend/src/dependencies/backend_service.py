import asyncio
import enum
import json
import uuid
from pathlib import Path

import openai
import pydantic
from loguru import logger

from database_connector import MongoDBConnector
from models.database import Item
from modules import chatgpt
from modules.camera import Camera
from mqtt_client import MQTTClientManager, ReaderMessage
from utils import find

MESSAGE_STREAM_DELAY = 1  # second
MESSAGE_STREAM_RETRY_TIMEOUT = 15000  # millisecond from utils import find


class Event(enum.Enum):
    SCAN = "SCAN"
    COMPLETION = "COMPLETION"
    ALIVE = "ALIVE"


class SseMessage(pydantic.BaseModel):
    class SseMessageData(pydantic.BaseModel):
        reader_id: str
        rfid: str | None = None  # Todo rename RFID to tag id
        data: dict | None = None

    event: Event
    data: SseMessageData | dict
    id: str = str(uuid.uuid4())
    retry: int = MESSAGE_STREAM_RETRY_TIMEOUT


class BackendService:
    def __init__(self, db_config, mqtt_config, config):
        self.config = config
        self.db = MongoDBConnector(
            uri=f"mongodb://{db_config.get("host", "localhost")
                             }:{db_config.get("port", "27017")}",
            database=db_config.get("database", "inventory"),
        )
        self.mqtt_client_manager = MQTTClientManager(
            callback=self.handle_message, mqtt_config=mqtt_config.get(
                "broker", {})
        )
        # todo refactor to clients or sth
        self.readers: dict[str, list[dict]] = {}

        # Read the schema from the file
        with open(Path(__file__).parent.parent.parent / "schemas" / "llm_schema.json") as schema_file:
            schema = json.load(schema_file)

        try:
            self.item_data_topic = find(key := "mqtt.topics.result", config)
            self.llm_completion = chatgpt.ChatGPT(
                api_key=find(key := "features.openai.api_key", config), response_schema=schema
            )
            self.camera = Camera(find(key := "camera.url", config))
        except (KeyError, TypeError, openai.OpenAIError) as e:
            logger.error(
                f"Error getting config key {key}, check config file and environment variables: {e}")
        asyncio.create_task(self.push_heartbeats())

    async def handle_message(self, message, topic):
        logger.debug(f"Handle message: {message} on topic {topic}")
        try:
            msg = ReaderMessage(**json.loads(message))
            self.readers.setdefault(msg.reader_id, [])
        except (pydantic.ValidationError, json.JSONDecodeError) as e:
            logger.error(f"Error parsing message: {e}, {message}")
            return
        data = SseMessage.SseMessageData(reader_id=msg.reader_id, rfid=msg.tag_id).model_dump(
            mode="json", exclude_none=True
        )
        self.readers[msg.reader_id].append(SseMessage(
            data=data, event=Event.SCAN).model_dump(mode="json"))

        # Send db data to reader
        # todo don't fetch data from db twice
        item_raw = self.db.find_by_rfid("items", msg.tag_id)
        if item_raw is None:
            # Item not found
            self.mqtt_client_manager.publish(
                self.item_data_topic + f"/{msg.reader_id}", "null")
        else:
            try:
                item = Item.model_validate(
                    item_raw, strict=False, from_attributes=True)
                self.mqtt_client_manager.publish(
                    self.item_data_topic + f"/{msg.reader_id}",
                    str(
                        item.model_dump(
                            mode="json",
                            include={
                                "tag_uuid",
                                "short_name",
                                "amount",
                                "item_type",
                                "borrowed",
                                "container_tag_uuid",
                                "container_name",
                            },
                        )
                    ),
                )
            except pydantic.ValidationError as e:
                logger.error(f"Error validating item: {e}")
                self.mqtt_client_manager.publish(
                    self.item_data_topic + f"/{msg.reader_id}", "ValidationError")

    def start_mqtt(self):
        try:
            self.mqtt_client_manager.connect()
        except ConnectionRefusedError:
            logger.error(
                "MQTT connection refused. This results in unexpected behavior! Please check your MQTT broker configuration.")

    def add_mqtt_topic(self, topic):
        self.mqtt_client_manager.add_topic(topic)

    def close(self):
        self.db.close()
        self.mqtt_client_manager.stop()

    async def push_heartbeats(self):
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
