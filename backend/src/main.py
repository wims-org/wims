import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from dependencies.backend_service import BackendService
from dependencies.config import read_config

# Use absolute import
from routers import camera, completion, healthz, items, queries, readers, scan, stream
from utils import find

# Read config

config = read_config()

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
        config=config,
    )
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
app.include_router(camera.router)
app.include_router(queries.router)
app.include_router(scan.router)

if find("features.openai", config):
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
    return JSONResponse(app.openapi())
