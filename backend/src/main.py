import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from dependencies.backend_service import BackendService
from dependencies.config import read_config

# Use absolute import
from routers import camera, completion, config, healthz, items, queries, readers, scan, stream, users
from utils import find

# Read config

configuration = read_config()

logger.info("Starting backend service")

# Set up the FastAPI app


def setup_middleware(app):
    frontend_config = configuration.get("frontend", {})
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
    app.state.config = configuration
    app.state.backend_service = BackendService(
        db_config=configuration.get("database", {}),
        config=configuration,
    )
    app.state.backend_service.start_mqtt()
    try:
        scan_topic = find(key := "mqtt.topics.scan", configuration)
    except (KeyError, TypeError) as e:
        logger.error(f"Error updating config key {key}, check config file and environment variables: {e}")
    app.state.backend_service.add_mqtt_topic(scan_topic or "rfid/scan/#")
    yield
    app.state.backend_service.close()


if os.environ.get("RUN_MODE", "") == "production":
    logger.info("Started in production mode")
    app = FastAPI(lifespan=lifespan, redirect_slashes=False, root_path="/api")
else:
    logger.info("Started in development mode")
    app = FastAPI(lifespan=lifespan, redirect_slashes=False)

app.include_router(readers.router)
app.include_router(items.router)
app.include_router(stream.router)
app.include_router(healthz.router)
app.include_router(camera.router)
app.include_router(queries.router)
app.include_router(users.router)
app.include_router(config.router)
app.include_router(scan.router)

if find("features.openai", configuration):
    app.include_router(completion.router)
    logger.info("LLM features enabled")
else:
    logger.info("Handarbeit")
setup_middleware(app)


@app.get("/openapi.json", include_in_schema=False)
async def custom_openapi():
    """
    Serve the OpenAPI spec for frontend code generation.
    """
    handler = app.openapi()
    handler.generate_schema()
    return JSONResponse(handler)
