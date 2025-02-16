import asyncio
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from dependencies.backend_service import MESSAGE_STREAM_DELAY, BackendService, Event
from dependencies.config import read_config
from routers import completion, items, readers
from utils import find

logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.DEBUG)

logger.debug("Starting backend service")

global config

config = read_config()


def setup_middleware(
    app,
):
    frontend_config = config.get("frontend", {})
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
    origins.append(
        f"http://{frontend_config.get("host",
                                      "0.0.0.0")}:{frontend_config.get("port", '8080')}"
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.config = config
    app.state.backend_service = BackendService(
        db_config=config.get("database", {}),
        mqtt_config=config.get("mqtt", {}),
        config=config,
    )
    app.state.backend_service.start_mqtt()
    try:
        scan_topic = find(key := "mqtt.topics.scan", config)
    except (KeyError, TypeError) as e:
        logger.error(
            f"Error updating config key {
                key}, check config file and environment variables: {e}"
        )
    app.state.backend_service.add_mqtt_topic(scan_topic or "rfid/scan")
    yield
    app.state.backend_service.close()


app = FastAPI(lifespan=lifespan)
app.include_router(readers.router)
app.include_router(items.router)
app.include_router(completion.router)
setup_middleware(app)


async def handle_message(message, topic):
    logger.debug(f"Handle message: {message} on topic {topic}")
    # await app.state.backend_service.websocket_manager.send_message(message, topic)


@app.get("/test-db")
async def test_db_connection():
    try:
        app.state.backend_service.db.connect()
        app.state.backend_service.db.disconnect()
        return {"message": "Database connection successful"}
    except Exception as e:
        return {"message": f"Database connection failed: {e}"}


# Routes


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


def get_message():
    """this could be any function that blocks until data is ready"""
    time.sleep(1.0)
    s = time.ctime(time.time())
    return s


@app.get("/stream")
async def message_stream(request: Request, reader: str):
    logger.debug(f"Message stream{request}, {reader}")
    app.state.backend_service.readers[reader] = []

    def new_messages():
        return len(app.state.backend_service.readers[reader]) > 0

    async def event_generator():
        while True:
            # If client was closed the connection
            if await request.is_disconnected():
                break
            # Checks for new messages and return them to client if any
            if new_messages():
                message = app.state.backend_service.readers[reader].pop(0)
                if message["event"] != Event.ALIVE.value:
                    logger.debug(f"Sending message: {message}")
                yield message
            await asyncio.sleep(MESSAGE_STREAM_DELAY)

    return EventSourceResponse(event_generator())
