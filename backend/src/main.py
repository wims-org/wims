import asyncio
import json
import logging
import time
from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Use absolute import
from dependencies.backend_service import MESSAGE_STREAM_DELAY, BackendService
from dependencies.config import read_config
from  routers import items, completion, readers, stream
from utils import find

logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.DEBUG)

logger.debug("Starting backend service")

config = read_config()


def setup_middleware(app):
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
        f"http://{frontend_config.get('host', '0.0.0.0')}:{frontend_config.get('port', '8080')}"
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
            f"Error updating config key {key}, check config file and environment variables: {e}"
        )
    app.state.backend_service.add_mqtt_topic(scan_topic or "rfid/scan/#")
    yield
    app.state.backend_service.close()

if os.environ.get("RUN_MODE","") == "production":
    app = FastAPI(lifespan=lifespan, root_path="/api")
else:
    app = FastAPI(lifespan=lifespan)

app.include_router(readers.router)
app.include_router(items.router)
app.include_router(completion.router)
app.include_router(stream.router)
setup_middleware(app)
