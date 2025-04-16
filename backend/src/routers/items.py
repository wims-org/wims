import pydantic
import pymongo
from fastapi import APIRouter, HTTPException, Request
from loguru import logger

from database_connector import MongoDBConnector
from models.database import Item
from models.requests import ItemRequest

router = APIRouter(prefix="/items", tags=["items"], responses={404: {"description": "Not found"}})


def get_db(request: Request) -> MongoDBConnector:
    return request.app.state.backend_service.db


@router.put("/{rfid}")
async def put_item(request: Request):
    # update item
    item = await request.json()
    item_data = ItemRequest.model_validate(item, strict=False, from_attributes=True)
    item_data = Item.model_validate(item_data, strict=False, from_attributes=True)
    # item_data = item.model_dump(mode="json")
    updated_rows = get_db(request).update(
        collection_name="items",
        # match by either tag_uuid or old container_tag_uuid, only for id migration
        query={"$or": [{"tag_uuid": item_data.tag_uuid}]},
        update_values=item_data.model_dump(mode="json", by_alias=True),
    )
    if updated_rows:
        return {"message": "Item updated successfully"}
    else:
        return {"message": "Failed to update item"}


@router.post("")
async def post_item(request: Request):
    # create item
    item = await request.json()
    item = {k: v for k, v in item.items() if v is not None}
    item_data = ItemRequest.model_validate(item, strict=False, from_attributes=True)
    item = Item.model_validate(item_data, strict=False, from_attributes=True)
    try:
        updated_rows = get_db(request).create(
            collection_name="items",
            document=item.model_dump(mode="json", by_alias=True),
        )
    except pymongo.errors.DuplicateKeyError as e:
        raise HTTPException(status_code=400, detail="Item already exists") from e
    if updated_rows:
        logger.debug(f"Item created: {item_data}, {updated_rows}")
        return {"message": "Item created successfully"}
    else:
        return {"message": "Failed to update item"}


@router.delete("/{rfid}")
async def delete_item(request: Request, rfid: str):
    updated_rows = get_db(request).delete(
        collection_name="items",
        query={"tag_uuid": rfid},
    )
    if updated_rows:
        return {"message": "Item deleted successfully"}
    else:
        return {"message": "Failed to update item"}


@router.get("/{rfid}")
async def get_item(request: Request, rfid: str):
    item = get_db(request).find_by_rfid(collection_name="items", rfid=rfid)
    if item:
        try:
            return Item.model_validate(item, strict=False, from_attributes=True)
        except pydantic.ValidationError as e:
            logger.error(f"Error validating item: {item=}, {e}")
            errors = [f"{'.'.join(err.get('loc', []))} {err.get('type')}: {err.get('msg')}" for err in e.errors()]
            valid_item = Item.model_construct(**item)
            res = valid_item.model_dump(exclude_unset=True, exclude_defaults=True, exclude_none=True)
            res["errors"] = errors
            return res

    else:
        raise HTTPException(status_code=404, detail="Item not found")


@router.get("")
async def get_items(request: Request, query: str = None):
    if query:
        items = get_db(request).read(
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
    else:
        items = get_db(request).read(collection_name="items")

    if items:
        return items
    else:
        return {"message": "Item not found"}


# dont look to closely at this
@router.patch("")
async def patch_items(request: Request):
    items = get_db(request).read(collection_name="items")
    for item_data in items:
        item = Item.model_validate(item_data, strict=False, from_attributes=True)
        item_data = item.model_dump(mode="json")
        _ = get_db(request).update(
            collection_name="items",
            query={"container_tag_uuid": item_data["container_tag_uuid"]},
            update_values=item_data,
        )
    if items:
        return items
    else:
        return {"message": "Item not found"}
