import asyncio
import enum
import json
import logging
import time
import uuid
from pathlib import Path

import yaml
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, ValidationError
from sse_starlette.sse import EventSourceResponse

from database_connector import MongoDBConnector
from models.database import Item
from mqtt_client import MQTTClientManager, ReaderMessage

logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.DEBUG)

logger.debug("Starting backend service")

MESSAGE_STREAM_DELAY = 1  # second
MESSAGE_STREAM_RETRY_TIMEOUT = 15000  # milisecond
app = FastAPI()

origins = [
    "http://localhost:5000",
    "http://localhost:5002",
    "http://localhost:5005",
    "http://localhost:5173",
    "http://localhost:8000",
    "http://localhost",
    "https://localhost",
    "http://localhost:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def read_config():
    with open(Path("__file__").parent.absolute() / "config.yml") as file:
        return yaml.safe_load(file)


config = read_config()

# testing websocket
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>WebSocket Test</title>
    </head>
    <body>
        <h1>WebSocket Test</h1>
        <input type="text" id="topic" placeholder="Enter topic">
        <button onclick="connectWebSocket()">Connect</button>
        <ul id="messages"></ul>
        <script>
            function connectWebSocket() {
                const topic = document.getElementById('topic').value;
                const ws = new WebSocket("ws://localhost:5005/ws?mqtt_topic=" + topic);
                ws.onmessage = function(event) {
                    const messages = document.getElementById('messages');
                    const message = document.createElement('li');
                    message.textContent = event.data;
                    messages.appendChild(message);
                };
            }
        </script>
    </body>
</html>
"""


@app.get("/ws")
async def get():
    return HTMLResponse(html)


class Event(enum.Enum):
    REDIRECT = "REDIRECT"


class SseMessage(BaseModel):
    event: Event
    data: dict
    id: str = str(uuid.uuid4())
    retry: int = MESSAGE_STREAM_RETRY_TIMEOUT

    class SseMessageData(BaseModel):
        reader_id: str
        rfid: str


class BackendService:
    def __init__(self, db_config, mqtt_config):
        self.db = MongoDBConnector(
            uri=db_config.get("uri", "mongodb://localhost:27017"),
            database=db_config.get("database", "inventory"),
        )
        self.mqtt_client_manager = MQTTClientManager(
            callback=self.handle_message,
            host=mqtt_config.get("host", "localhost"),
            port=mqtt_config.get("port", 1883),
        )
        self.readers: dict[str, list[dict]] = {}

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
                data=SseMessage.SseMessageData(reader_id=msg.reader_id, rfid=msg.rfid).model_dump(mode="json"),
                event=Event.REDIRECT,
            ).model_dump(mode="json")
        )

    def start_mqtt(self):
        self.mqtt_client_manager.connect()

    def add_mqtt_topic(self, topic):
        self.mqtt_client_manager.add_topic(topic)


# init
# Use config parameters
db_config = config.get("database", {})
mqtt_config = config.get("mqtt", {})
backend_service = BackendService(db_config, mqtt_config)
backend_service.start_mqtt()
backend_service.add_mqtt_topic("foo/bar")
logger.debug(f"Initializing backend service with config: {config}")


async def handle_message(message, topic):
    logger.debug(f"Handle message: {message} on topic {topic}")
    # await backend_service.websocket_manager.send_message(message, topic)


@app.get("/test-db")
async def test_db_connection():
    try:
        backend_service.db.connect()
        backend_service.db.disconnect()
        return {"message": "Database connection successful"}
    except Exception as e:
        return {"message": f"Database connection failed: {e}"}


# Routes


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


# Database Proxy


@app.post("/item")
async def update_item(item: Item):
    item_data = item.model_dump(mode="json")
    updated_rows = backend_service.db.update(
        collection_name="items",
        # match by either tag_uuid or old container_tag_id, only for id migration
        query={ "$or": [{"tag_uuid": item_data["tag_uuid"]}, {"container_tag_id": item_data["container_tag_id"]}] },
        update_values=item_data,
    )
    if updated_rows:
        return {"message": "Item updated successfully"}
    else:
        return {"message": "Failed to update item"}


@app.put("/item")
async def create_item(item: Item):
    item_data = item.model_dump(mode="json")
    updated_rows = backend_service.db.create(collection_name="items", document=item_data)
    if updated_rows:
        return {"message": "Item created successfully"}
    else:
        return {"message": "Failed to update item"}


@app.delete("/item/{rfid}")
async def delete_item(rfid: str):
    updated_rows = backend_service.db.delete(
        collection_name="items",
        query={"container_tag_id": rfid},
    )
    if updated_rows:
        return {"message": "Item deleted successfully"}
    else:
        return {"message": "Failed to update item"}


@app.get("/item/{rfid}")
async def get_item(rfid: str):
    item = backend_service.db.find_by_rfid(collection_name="items", rfid=rfid)
    if item:
        try:
            return Item.model_validate(item, strict=False, from_attributes=True)
        except ValidationError as e:
            logger.error(f"Error validating item: {item=}, {e}")
            return HTTPException(status_code=500, detail="found, but error validating database content")
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@app.get("/items")
async def get_items():
    items = backend_service.db.read(collection_name="items")
    if items:
        return items
    else:
        return {"message": "Item not found"}

# dont look to closely at this
@app.patch("/items")
async def patch_items():
    items = backend_service.db.read(collection_name="items")
    for item_data in items:
        item = Item.model_validate(item_data, strict=False, from_attributes=True)
        item_data = item.model_dump(mode="json")
        updated_rows = backend_service.db.update(
            collection_name="items",
            query={"container_tag_id": item_data["container_tag_id"]},
            update_values=item_data,
        )
    if items:
        return items
    else:
        return {"message": "Item not found"}


def get_message():
    """this could be any function that blocks until data is ready"""
    time.sleep(1.0)
    s = time.ctime(time.time())
    return s


@app.get("/stream")
async def message_stream(request: Request, reader: str):
    logger.debug(f"Message stream{request}, {reader}")
    backend_service.readers[reader] = []

    def new_messages():
        return len(backend_service.readers[reader]) > 0

    async def event_generator():
        while True:
            # If client was closed the connection
            if await request.is_disconnected():
                break
            # Checks for new messages and return them to client if any
            if new_messages():
                message = backend_service.readers[reader].pop(0)
                logger.debug(f"Sending message: {message}")
                yield message
            await asyncio.sleep(MESSAGE_STREAM_DELAY)

    return EventSourceResponse(event_generator())
