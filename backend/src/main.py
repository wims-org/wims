import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from prometheus_client import Counter, Histogram, disable_created_metrics
from starlette.middleware.base import BaseHTTPMiddleware

from dependencies.backend_service import BackendService
from dependencies.config import read_config
from routers import (
    backup,
    categories,
    completion,
    config,
    healthz,
    metrics,
    openapi,
    queries,
    readers,
    scan,
    stream,
    users,
)
from routers.items import items
from utils import find

configuration = read_config()

logger.info("Starting backend service")

# Prometheus metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "http_status"],
)
REQUEST_DURATION = Histogram(
    "request_duration_seconds",
    "Request duration in seconds",
    ["method", "endpoint", "http_status"],
)
disable_created_metrics()


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        try:
            routePath = request.scope["route"].path
        except KeyError:
            # Sometimes we don't have a route object. Pls don't ask me why...
            routePath = request.scope["path"]

        REQUEST_COUNT.labels(request.method, routePath, str(response.status_code)).inc()
        REQUEST_DURATION.labels(request.method, routePath, str(response.status_code)).observe(duration)
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.config = configuration
    app.state.backend_service = BackendService(
        db_config=configuration.get("database", {}),
        config=configuration,
    )
    yield


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
app.include_router(queries.router)
app.include_router(users.router)
app.include_router(scan.router)
app.include_router(config.router)
app.include_router(categories.router)
app.include_router(backup.router)
app.include_router(metrics.router)
app.include_router(openapi.router)

if find("features.openai", configuration):
    app.include_router(completion.router)
    logger.info("LLM features enabled")
else:
    logger.info("LLM feature disabled. Handarbeit!")

app.add_middleware(MetricsMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
