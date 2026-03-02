import os
import time

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from prometheus_client import Counter, Histogram, disable_created_metrics
from starlette.middleware.base import BaseHTTPMiddleware

from dependencies import database, event_handler, settings
from routers import (
    # completion,
    config,
    healthz,
    items,
    metrics,
    readers,
    scan,
    stream,
    # scan,
    # stream,
    users,
)

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
    )

if os.environ.get("RUN_MODE", "") == "production":
    logger.info("Started in production mode")
    root_path = "/api"
else:
    logger.info("Started in development mode")
    root_path = "/"

app = FastAPI(
    dependencies=[
        Depends(database.get_db),
        Depends(event_handler.get_event_handler),
        # Depends(backend_service.BackendService()),
    ],
    redirect_slashes=False,
    root_path=root_path,
)

app.include_router(users.router)
app.include_router(items.router)
app.include_router(readers.router)

# app.include_router(queries.router)
app.include_router(config.router)
# app.include_router(categories.router)
# app.include_router(backup.router)

app.include_router(stream.router)
app.include_router(healthz.router)
app.include_router(scan.router)
app.include_router(metrics.router)

if settings.get_settings().features_openai_api_key:
    # app.include_router(completion.router)
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
