from fastapi import APIRouter, HTTPException, Request
from loguru import logger

import db.db_item_lists as db_item_lists
from models.database import Item
from routers.utils import get_bs

router = APIRouter(prefix="", tags=["items"], responses={404: {"description": "Not found"}})


@router.get("/", response_model=list[Item])
async def get_items(
    request: Request,
) -> list[Item]:
    items = get_bs(request).dbc.read(collection_name="items")
    if items:
        return items
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@router.get("/", response_model=list[Item])
def get_items_option(
    request: Request,
    option: str,
    offset: int | None = None,
) -> list[Item]:
    """Meta-search of queries not directly bound to the data model"""
    match option:
        case "latest":
            items = db_item_lists.get_new_items_latest(offset=offset or 0, db=get_bs(request).dbc.db)
        case "borrowed":
            items = db_item_lists.get_items_borrowed(db=get_bs(request).dbc.db)
    if items:
        return items
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@router.get("/", response_model=list[Item])
async def get_items_query(request: Request, query: str, offset: int | None) -> list[Item]:
    items = get_bs(request).dbc.read(
        collection_name="items",
        query={
            "$or": [
                {"tag_uuid": {"$regex": query, "$options": "i"}},
                {"short_name": {"$regex": query, "$options": "i"}},
                {"item_type": {"$regex": query, "$options": "i"}},
                {"tags": {"$regex": query, "$options": "i"}},
                {"manufacturer": {"$regex": query, "$options": "i"}},
            ]
        },
    )
    logger.debug(f"Found {len(items)} items matching query: {query}")
    if items:
        return items
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@router.get("/", response_model=list[Item])
async def get_items_search_params(request: Request, borrowed_by: str | None, offset: int | None) -> list[Item]:
    """And-Search"""
    query_params = {"borrowed_by": borrowed_by}
    query = {param: value for param, value in query_params.items}

    items = get_bs(request).dbc.read(collection_name="items", query=query)
    logger.debug(f"Found {len(items)} items matching query: {query}")
    if items:
        return items
    else:
        raise HTTPException(status_code=404, detail="Item not found")
