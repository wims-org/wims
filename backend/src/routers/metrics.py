from typing import Annotated

from fastapi import APIRouter, Request, Response
from fastapi.params import Depends
from prometheus_client import CONTENT_TYPE_LATEST, Gauge, generate_latest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import database

router = APIRouter(prefix="", tags=["metrics"])


ITEM_COUNT = Gauge("item_count_total", "Total number of items")
USER_COUNT = Gauge("user_count_total", "Total number of users")
CATEGORY_COUNT = Gauge("category_count_total", "Total number of categories")
READER_COUNT = Gauge("reader_count_total", "Total number of readers")


@router.get("/metrics")
async def metrics(
    session: Annotated[AsyncSession, Depends(database.get_db_session)],
):
    database = session

    ITEM_COUNT.set((await database.execute(text("SELECT COUNT(*) FROM item"))).scalar())
    USER_COUNT.set((await database.execute(text("SELECT COUNT(*) FROM users"))).scalar())
    CATEGORY_COUNT.set((await database.execute(text("SELECT COUNT(*) FROM category"))).scalar())
    # READER_COUNT.set((await database.execute(text("SELECT COUNT(*) FROM reader"))).scalar())

    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
