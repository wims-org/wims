import pydantic
import pymongo
from fastapi import APIRouter, HTTPException, Query, Request
from loguru import logger

from database_connector import MongoDBConnector, RecursiveContainerObject
from models.database import Item
from models.requests import ItemBacklogRequest, ItemRequest

router = APIRouter(prefix="/items", tags=["items"], responses={404: {"description": "Not found"}})


def get_db(request: Request) -> MongoDBConnector:
    return request.app.state.backend_service.db


class ItemChangedResponse(pydantic.BaseModel):
    message: str
    error_items: list[str] = []
    errors: list[str] = []

@router.put("/{rfid}", response_model=ItemChangedResponse)
async def put_item(
    request: Request,
    rfid: str,
    item: ItemRequest | None = None,
) -> ItemChangedResponse:
    # update item
    if item is None:
        item = await request.json()
    item_data = Item.model_validate(item.model_dump(exclude_unset=True, exclude_none=True), strict=False, from_attributes=True)

    old_item: dict = get_db(request).find_by_rfid(collection_name="items", rfid=rfid)
    if not old_item:
        raise HTTPException(status_code=404, detail="Item not found for update")
    old_item.update(item_data.model_dump(exclude_unset=True, exclude_none=True))
    try:
        old_item_data =Item.model_validate(old_item, strict=False, from_attributes=True)
    except pydantic.ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Validation error: {e}") from None

    updated_rows = get_db(request).update(
        collection_name="items",
        query={"$or": [{"tag_uuid": rfid}]},
        update_values=old_item_data.model_dump(mode="json", by_alias=True)
    )
    if updated_rows:
        return ItemChangedResponse(message="Item updated successfully")
    else:
        raise HTTPException(status_code=404, detail="Failed to update item, item not found or no changes made")


@router.post("", response_model=ItemChangedResponse)
async def post_item(
    request: Request,
    item: ItemRequest,
) -> ItemChangedResponse:
    """
    Create an item. If the item already exists, an error is raised.
    """
    item_dict = item.model_dump(exclude_unset=True, exclude_none=True)
    logger.debug(f"Creating item: {str(item_dict)[:100]}")
    try:
        item = Item.model_validate(item_dict, from_attributes=True)
        updated_rows = get_db(request).create(
            collection_name="items",
            document=item.model_dump(mode="json", by_alias=True),
        )
    except pydantic.ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Validation error: {e}") from None
    except pymongo.errors.DuplicateKeyError as e:
        raise HTTPException(status_code=400, detail="Item already exists") from e
    if updated_rows:
        #logger.debug(f"Item created: {str(item)[:100]}, {updated_rows}")
        return ItemChangedResponse(message="Item created successfully")
    else:
        raise HTTPException(status_code=500, detail="Failed to create item, please try again later")



@router.post("/backlog", response_model=ItemChangedResponse)
async def post_backlog_item(
    request: Request,
    item: ItemBacklogRequest,
) -> ItemChangedResponse:
    """
    Create a backlog item (no strict validation). If the item already exists, an error is raised.
    """
    item_dict = item.model_dump(exclude_unset=True, exclude_none=True)
    logger.debug(f"Creating item: {str(item_dict)[:100]}")
    if not item_dict.get("short_name"):
        item_dict["short_name"] = ""
    try:
        item = Item.model_validate(item_dict, from_attributes=True)
    except pydantic.ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Validation error: {e}") from None
    try:
        updated_rows = get_db(request).create(
            collection_name="items",
            document=item.model_dump(mode="json", by_alias=True, exclude_none=True, exclude_unset=True),
        )
    except pymongo.errors.DuplicateKeyError as e:
        raise HTTPException(status_code=400, detail="Item already exists") from e
    if updated_rows:
        return ItemChangedResponse(message="Item created successfully")
    else:
        raise HTTPException(status_code=500, detail="Failed to create item, please try again later")


@router.delete("/{rfid}", response_model=ItemChangedResponse)
async def delete_item(
    request: Request,
    rfid: str,
) -> ItemChangedResponse:
    updated_rows = get_db(request).delete(
        collection_name="items",
        query={"tag_uuid": rfid},
    )
    if updated_rows:
        return ItemChangedResponse(message="Item deleted successfully")
    else:
        raise HTTPException(status_code=404, detail="Failed to update item, item not found")


@router.get("/{rfid}", response_model=Item)
async def get_item(
    request: Request,
    rfid: str,
) -> Item:
    item = get_db(request).find_by_rfid(collection_name="items", rfid=rfid)
    if item:
        try:
            return Item.model_validate(item, strict=False, from_attributes=True)
        except pydantic.ValidationError as e:
            logger.error(f"Error validating item: {str(item)[:100]}, {e}")
            errors = [
                f"{'.'.join(map(str, err.get('loc', [])))} {err.get('type')}: {err.get('msg')}" for err in e.errors()
            ]
            valid_item = Item.model_construct(**item)
            res = valid_item.model_dump(exclude_unset=True, exclude_defaults=True, exclude_none=True)
            res["errors"] = errors
            return res
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@router.get("/{rfid}/containers", response_model=RecursiveContainerObject)
async def get_item_with_containers(
    request: Request,
    rfid: str,
) -> RecursiveContainerObject:
    recursive_containers = get_db(request).get_recursive_container_tags(collection_name="items", rfid=rfid)
    if not recursive_containers:
        raise HTTPException(status_code=404, detail="Item not found")
    return recursive_containers


@router.get("/{rfid}/content", response_model=list[Item])
async def get_item_content(
    request: Request,
    rfid: str,
) -> list[Item]:
    content = get_db(request).read(collection_name="items", query={"container_tag_uuid": rfid})
    if not content:
        raise HTTPException(status_code=404, detail="Item content not found")
    return content


@router.get("", response_model=list[Item])
async def get_items(
    request: Request,
    query: str | None = Query(None),
) -> list[Item]:
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
        raise HTTPException(status_code=404, detail="Item not found")


@router.patch("", response_model=list[Item])
async def patch_items(
    request: Request,
) -> list[Item]:
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
        raise HTTPException(status_code=404, detail="Item not found")


@router.post("/bulk", response_model=ItemChangedResponse)
async def bulk_import_items(
    request: Request,
    items: list[ItemRequest],
) -> ItemChangedResponse:
    """
    Bulk import items. Accepts a list of item dicts.
    If an item with the same tag_uuid exists, it is updated; otherwise, it is created.
    """
    db = get_db(request)
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
                "message": f"Validation error: Some items are invalid. Please check your input.",
                "errors": errors,
                "error_items": error_items,
            },
        )

    msg = f"{imported} item(s) imported, {updated} item(s) updated successfully."
    if errors:
        msg += f" {len(errors)} error(s): {'; '.join(errors)}"
    return ItemChangedResponse(message=msg, errors=errors, error_items=error_items)
