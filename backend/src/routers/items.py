from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database_connector import RecursiveContainerObject
from db import db_items
from dependencies import database
from models.item import Item, ItemCreate, ItemPublic, ItemUpdate
from routers.utils import get_bs
from schemas.requests import ItemBacklogRequest, ItemRequest

router = APIRouter(prefix="/items", tags=["items"], responses={404: {"description": "Not found"}})


class Query(BaseModel):
    filters: dict[str:str] = {}
    sort_by: str
    sort_reverse: bool


@router.post("", response_model=ItemPublic)
async def create_item(item: ItemCreate, session: Annotated[AsyncSession, Depends(database.get_db_session)]):
    db_item = Item.model_validate(item)
    await session.add(db_item)
    try:
        await session.commit()
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    await session.refresh(db_item)
    return db_item


@router.get("/{id}", response_model=ItemPublic)
async def get_item(session: Annotated[AsyncSession, Depends(database.get_db_session)], id: str, query: str|None=None):
    if query:
        pass # TODO
    item = await session.get(Item, id)
    if not item:
        raise HTTPException(status_code=400, detail="Item id not found")
    return item


@router.get("/", response_model=list[ItemPublic])
async def get_items(
    session: Annotated[AsyncSession, Depends(database.get_db_session)], offset: int = 0, limit: int = 0
):
    return await session.exec(select(Item).offset(offset).limit(limit)).all()


@router.put("/{id}", response_model=ItemPublic)
async def update_item(id: str, item: ItemUpdate, session: Annotated[AsyncSession, Depends(database.get_db_session)]):
    item = await session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db_item = item.model_dump(exclude_unset=True)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@router.delete("/{id}")
async def delete_item(id: str, session: Annotated[AsyncSession, Depends(database.get_db_session)]):
    item = await session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    session.delete(item)
    session.commit()
    return {"ok": True}


### Bis hierher und nicht weiter ### TODO

@router.post("/backlog", response_model=ItemPublic)
async def post_backlog_item(
    item: ItemBacklogRequest, session: Annotated[AsyncSession, Depends(database.get_db_session)]
) -> Item:
    return await ItemsService(db=session).create_backlog_item(item=item)


@router.get("/{rfid}/containers", response_model=RecursiveContainerObject)
async def get_item_with_containers(
    rfid: str, session: Annotated[AsyncSession, Depends(database.get_db_session)]
) -> RecursiveContainerObject:
    return await ItemsService(db=session).get_item_with_containers(rfid=rfid)


@router.get("/{rfid}/content", response_model=list[Item])
async def get_item_content(
    request: Request,
    rfid: str,
) -> list[Item]:
    content = get_bs(request).dbc.read(collection_name="items", query={"container_tag_uuid": rfid})
    if not content:
        raise HTTPException(status_code=404, detail="Item content not found")
    return content


@router.post("/search", response_model=list[Item])
async def get_item_search(request: Request, query: str) -> list[Item]:
    """
    Search for items based on a query object, post to allow for body.
    """
    query = Query.model_validate(query)
    logger.debug(f"Searching items with search query: {query}")
    items = db_items.get_items_with_search_query(query=query, db=get_bs(request).dbc.db)
    if not items:
        raise HTTPException(status_code=404, detail="Item not found")
    return items


@router.post("/csv-import", response_model=ItemChangedResponse)
async def bulk_import_items(
    request: Request,
    items: list[ItemRequest],
) -> ItemChangedResponse:
    """
    Bulk import items. Accepts a list of item dicts.
    If an item with the same tag_uuid exists, it is updated; otherwise, it is created.
    """
    db = get_bs(request).dbc
    imported = 0
    updated = 0
    errors = []
    error_items = []
    for idx, item_req in enumerate(items):
        try:
            # Remove None values, use defaults for missing fields
            item_dict = {k: v for k, v in item_req.model_dump(exclude_none=True).items()}
            item = Item.model_validate(item_dict, strict=False, from_attributes=True)
            # Try to update existing item
            result = db.update(
                collection_name="items",
                query={"tag_uuid": item.tag_uuid},
                update_values=item.model_dump(mode="json", by_alias=True),
            )

            if result:
                updated += 1
            else:
                error_items.append(item.tag_uuid)
        except pymongo.errors.DuplicateKeyError:
            # If not found, create new
            db.create(
                collection_name="items",
                document=item.model_dump(mode="json", by_alias=True),
            )
            imported += 1
        except Exception as e:
            errors.append(f"Row {idx}: {str(e)}")
            if tag_uuid := item_dict.get("tag_uuid"):
                error_items.append(tag_uuid)

    if imported == 0 and updated == 0 and not errors:
        logger.warning(error_items)
        raise HTTPException(
            status_code=406,
            detail={
                "message": "Not Modified. No items imported or updated.",
                "errors": errors,
                "error_items": error_items,
            },
        )
    if errors:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Validation error: Some items are invalid. Please check your input.",
                "errors": errors,
                "error_items": error_items,
            },
        )

    msg = f"{imported} item(s) imported, {updated} item(s) updated successfully."
    if errors:
        msg += f" {len(errors)} error(s): {'; '.join(errors)}"
    return ItemChangedResponse(message=msg, errors=errors, error_items=error_items)
