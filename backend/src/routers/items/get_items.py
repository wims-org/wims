from fastapi import APIRouter, HTTPException, Request

from db import db_items
from models.database import Item
from models.requests import SearchQuery
from routers.utils import get_bs

router = APIRouter(prefix="", tags=["items"], responses={404: {"description": "Not found"}})


@router.get("/", response_model=list[Item])
async def get_items(
    request: Request,
) -> list[Item]:
    items = get_bs(request).dbc.read(collection_name="items").sort("created_at", -1)
    if items:
        return items
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@router.get("/", response_model=list[Item])
async def get_items_query(request: Request, query: str) -> list[Item]:
    query = SearchQuery.model_validate(query)
    items = db_items.get_items_with_search_query(query=query, db=get_bs(request).dbc.db)
    if items:
        return items
    else:
        raise HTTPException(status_code=404, detail="Item not found")
