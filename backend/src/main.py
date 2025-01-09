import asyncio
import json
from pathlib import Path
import time
from fastapi import FastAPI, Request
import threading
from fastapi.responses import HTMLResponse

from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from models.requests import UpdateItemRequest
from database_connector import MongoDBConnector
from mqtt_client import MQTTClientManager, ReaderMessage
import yaml

from sse_starlette.sse import EventSourceResponse

import logging

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
    with open(Path("__file__").parent.absolute() / "config.yml", "r") as file:
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
        document = self.db.find_by_rfid(collection_name="items", rfid=msg.rfid)
        logger.debug(f"Document: {document}")
        if document:
            # send redirect to rfid frontend
            self.readers[msg.reader_id].append("message for reader"+msg.reader_id)

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
async def update_item(item: UpdateItemRequest):
    item_data = item.model_dump(mode="json")
    updated_rows = backend_service.db.update(
        collection_name="items",
        query={"container_tag_id": item_data["container_tag_id"]},
        update_values=item_data,
    )
    if updated_rows:
        return {"message": "Item updated successfully"}
    else:
        return {"message": "Failed to update item"}


@app.put("/item")
async def create_item(item: UpdateItemRequest):
    item_data = item.model_dump(mode="json")
    updated_rows = backend_service.db.create(
        collection_name="items", document=item_data
    )
    if updated_rows:
        return {"message": "Item updated successfully"}
    else:
        return {"message": "Failed to update item"}


@app.get("/item/{rfid}")
async def get_item(rfid: str):
    item = backend_service.db.find_by_rfid(collection_name="items", rfid=rfid)
    if item:
        return item
    else:
        return {"message": "Item not found"}


@app.get("/items")
async def get_items():
    items = backend_service.db.read(collection_name="items")
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
async def message_stream(request: Request,  reader: str):
    logger.debug(f"Message stream{request}, {reader}")
    backend_service.readers[reader] = []

    def new_messages():
        if len(backend_service.readers[reader]):
            return True
        return False

    async def event_generator():
        while True:
            # If client was closed the connection
            if await request.is_disconnected():
                break
            # Checks for new messages and return them to client if any
            if new_messages():
                yield {
                    "event": "message",
                    "id": "message_id",
                    "retry": MESSAGE_STREAM_RETRY_TIMEOUT,
                    "data": backend_service.readers[reader].pop(0),
                }

            await asyncio.sleep(MESSAGE_STREAM_DELAY)

    return EventSourceResponse(event_generator())
