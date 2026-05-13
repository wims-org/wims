import logging
import os
import time
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_client import Counter, Histogram, disable_created_metrics
from sentry_sdk.integrations.fastapi import FastApiIntegration
from starlette.middleware.base import BaseHTTPMiddleware

import routers
from dependencies import database, event_handler, settings

wims_config = settings.get_settings()

# Set log level
logging.getLogger("uvicorn").setLevel(wims_config.log_level)

# Use same logger als uvicorn
logger = logging.getLogger("uvicorn")

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


if wims_config.sentry_dsn:
    sentry_sdk.init(
        dsn=wims_config.sentry_dsn,
        send_default_pii=True,
        integrations=[FastApiIntegration()],
        environment=os.environ.get("RUN_MODE", "development"),
    )

if os.environ.get("RUN_MODE", "") == "production":
    logger.info("Started in production mode")
    root_path = "/api"
else:
    logger.info("Started in development mode")
    root_path = "/"


def check_asset_path():
    if not wims_config.asset_path.exists():
        try:
            wims_config.asset_path.mkdir(parents=True)
        except (FileNotFoundError, OSError) as e:
            raise e


@asynccontextmanager
async def lifespan(app_: FastAPI):
    check_asset_path()
    event_handler.EventHandlerFactory.get_instance()
    yield


app = FastAPI(
    dependencies=[
        Depends(database.get_db),
        Depends(event_handler.get_event_handler),
        # Depends(backend_service.BackendService()),
    ],
    redirect_slashes=False,
    root_path=root_path,
    lifespan=lifespan,
)

# Serve static files from the ./data/ directory
app.mount("/data", StaticFiles(directory="."))

app.include_router(routers.users.router)
app.include_router(routers.items.router)
app.include_router(routers.readers.router)
app.include_router(routers.files.router)
app.include_router(routers.categories.router)

# app.include_router(queries.router)
app.include_router(routers.config.router)
# app.include_router(backup.router)

app.include_router(routers.stream.router)
app.include_router(routers.healthz.router)
app.include_router(routers.scan.router)
app.include_router(routers.metrics.router)

if settings.get_settings().features_openai_api_key:
    app.include_router(routers.identification.router)
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
