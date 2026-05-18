from typing import Annotated

from fastapi import APIRouter, Response
from fastapi.params import Depends
from prometheus_client import CONTENT_TYPE_LATEST, Gauge, generate_latest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import func, select

from dependencies import database
from models.item import Item

router = APIRouter(prefix="", tags=["metrics"])


ITEM_COUNT = Gauge("item_count_total", "Total number of items", namespace="wims")
CONTAINER_COUNT = Gauge("container_count_total", "Total number of containers", namespace="wims")
USER_COUNT = Gauge("user_count_total", "Total number of users", namespace="wims")
CATEGORY_COUNT = Gauge("category_count_total", "Total number of categories", namespace="wims")
READER_COUNT = Gauge("reader_count_total", "Total number of readers", namespace="wims")


@router.get("/metrics")
async def metrics(session: Annotated[AsyncSession, Depends(database.get_db_session)]):
    database = session

    ITEM_COUNT.set((await database.execute(text("SELECT COUNT(*) FROM item"))).scalar())
    USER_COUNT.set((await database.execute(text("SELECT COUNT(*) FROM user"))).scalar())
    CATEGORY_COUNT.set((await database.execute(text("SELECT COUNT(*) FROM category"))).scalar())
    READER_COUNT.set((await database.execute(text("SELECT COUNT(*) FROM reader"))).scalar())

    # A container is an Item with content
    statement = select(func.count()).where(Item.content.any())
    result_object = (await database.execute(statement)).scalar()
    CONTAINER_COUNT.set(result_object)

    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
