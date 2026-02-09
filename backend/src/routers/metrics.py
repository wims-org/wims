from fastapi import APIRouter, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Gauge, generate_latest

from routers.utils import get_bs

router = APIRouter(prefix="", tags=["metrics"])


ITEM_COUNT = Gauge("item_count_total", "Total number of items")
USER_COUNT = Gauge("user_count_total", "Total number of users")
CATEGORY_COUNT = Gauge("category_count_total", "Total number of categories")
READER_COUNT = Gauge("reader_count_total", "Total number of readers")


@router.get("/metrics")
def metrics(request: Request):
    db = get_bs(request).dbc.db

    ITEM_COUNT.set(db["items"].count_documents({}))
    USER_COUNT.set(db["users"].count_documents({}))
    CATEGORY_COUNT.set(db["categories"].count_documents({}))
    READER_COUNT.set(db["readers"].count_documents({}))

    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
