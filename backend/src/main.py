from pathlib import Path
from fastapi import FastAPI, WebSocket
import threading
from fastapi.responses import HTMLResponse

from models.database import Item
from models.requests import UpdateItemRequest
from database_connector import MongoDBConnector
from mqtt_client import MQTTClientManager
from websocket import WebSocketManager
import yaml
from uuid import UUID

app = FastAPI()


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
        self.websocket_manager = WebSocketManager()

    async def handle_message(self, message, topic):
        print(f"Handle message: {message} on topic {topic}")
        await self.websocket_manager.send_message(message, topic)

    def start_mqtt(self):
        self.mqtt_client_manager.start()

    def add_mqtt_topic(self, topic):
        self.mqtt_client_manager.add_topic(topic)

    async def connect_websocket(self, websocket: WebSocket, mqtt_topic: str):
        if not mqtt_topic:
            await websocket.accept()
            await websocket.send_text("No topic provided")
            await websocket.close()
            return
        print(f"Websocket connection for topic {mqtt_topic}")
        await self.websocket_manager.connect(websocket, mqtt_topic)
        self.add_mqtt_topic(mqtt_topic)


# init
# Use config parameters
db_config = config.get("database", {})
mqtt_config = config.get("mqtt", {})

backend_service = BackendService(db_config, mqtt_config)
backend_service.add_mqtt_topic("foo/bar")
mqtt_thread = threading.Thread(target=backend_service.start_mqtt)
mqtt_thread.start()


async def handle_message(message, topic):
    print(f"Handle message: {message} on topic {topic}")
    await backend_service.websocket_manager.send_message(message, topic)


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


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, mqtt_topic: str):
    if not mqtt_topic:
        await websocket.accept()
        await websocket.send_text("No topic provided")
        await websocket.close()
        return
    print(f"Websocket connection for topic {mqtt_topic}")
    await backend_service.connect_websocket(websocket, mqtt_topic)
    backend_service.add_mqtt_topic(mqtt_topic)

# Database Proxy


@app.post("/item")
async def update_item(item: UpdateItemRequest):
    item_data = item.model_dump(mode="json")
    updated_rows = backend_service.db.update(
        collection_name="items", query={"container_tag_id": item_data["container_tag_id"]}, update_values=item_data
    )
    if updated_rows:
        return {"message": "Item updated successfully"}
    else:
        return {"message": "Failed to update item"}


@app.put("/item")
async def update_item(item: UpdateItemRequest):
    item_data = item.model_dump(mode="json")
    updated_rows = backend_service.db.create(collection_name="items", document=item_data)
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
