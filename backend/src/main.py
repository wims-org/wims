import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

# Use absolute import
from dependencies.backend_service import BackendService
from dependencies.config import read_config, read_env_config
from routers import completion, items, readers, stream, healthz
from utils import find

# Read config

config = {}
try:
    config = read_config(
        config_file_path=Path(os.environ.get("CONFIG_FILE")) if os.environ.get("CONFIG_FILE") else None
    )
except (FileNotFoundError, ValueError) as e:
    logger.error(e.message)

read_env_config(config)

logger.info("Starting backend service")

# Set up the FastAPI app

def setup_middleware(app):
    frontend_config = config.get("frontend", {})
    origins = [
        "*",
    ]
    origins.append(f"http://{frontend_config.get('host', '0.0.0.0')}:{frontend_config.get('port', '8080')}")
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
        logger.error(f"Error updating config key {key}, check config file and environment variables: {e}")
    app.state.backend_service.add_mqtt_topic(scan_topic or "rfid/scan/#")
    yield
    app.state.backend_service.close()


if os.environ.get("RUN_MODE", "") == "production":
    app = FastAPI(lifespan=lifespan, redirect_slashes=False, root_path="/api")
else:
    app = FastAPI(lifespan=lifespan, redirect_slashes=False)

app.include_router(readers.router)
app.include_router(items.router)
app.include_router(stream.router)
app.include_router(healthz.router)

if find("features.openai", config):
    app.include_router(completion.router)
    logger.info("LLM features enabled")
else:
    logger.info("Handarbeit")
setup_middleware(app)
