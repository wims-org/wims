from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, or_

from dependencies.database import SessionDep
from models.item import Item, ItemBacklog, ItemCreate, ItemPublic, ItemPublicWithRefs, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"], responses={404: {"description": "Not found"}})


class Query(BaseModel):
    term: str | None = None
    filters: dict[str, str] = {}
    offset: int = 0
    limit: int = 10
    sort_by: str | None = None
    sort_desc: bool = False


class ContainerObject(BaseModel):
    item_id: int
    short_name: str


@router.post("", response_model=ItemPublic)
async def create_item(item: ItemCreate, session: SessionDep):
    db_item = Item.model_validate(item)
    session.add(db_item)
    try:
        await session.commit()
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    await session.refresh(db_item)
    return db_item


@router.post("/backlog")
async def create_backlog_item(item: ItemBacklog, session: SessionDep):
    db_item = Item.model_validate(ItemBacklog.model_validate(item))
    session.add(db_item)
    try:
        await session.commit()
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    await session.refresh(db_item)
    return db_item


@router.get("/{id}", response_model=ItemPublicWithRefs)
async def get_item(session: SessionDep, id: str):
    item = await session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item id not found")
    return item


@router.get("/", response_model=list[ItemPublic])
async def get_all_item(session: SessionDep, offset: int = 0, limit: int = 10):
    return (await session.execute(select(Item).offset(offset).limit(limit))).scalars().all()


@router.put("/{id}", response_model=ItemPublic)
async def update_item(id: str, item: ItemUpdate, session: SessionDep):
    db_item = await session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    update = item.model_dump(exclude_unset=True)
    db_item.sqlmodel_update(update)
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)
    return db_item


@router.delete("/{id}")
async def delete_item(id: str, session: SessionDep):
    item = await session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    session.delete(item)
    session.commit()
    return {"ok": True}


@router.get("/{id}/containers", response_model=list[ContainerObject])
async def get_item_with_containers(id: str, session: SessionDep):
    item = await session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    parents = await get_item_parents(item, session)
    return parents


async def get_item_parents(item: Item, session: AsyncSession, parents: list = None) -> list[ContainerObject]:
    # Check for first iteration
    if parents is None:
        parents = [ContainerObject(item_id=item.id, short_name=item.short_name)]

    if item.container_id is None:
        return parents
    parent = await session.get(Item, item.container_id)
    parents = [ContainerObject(item_id=parent.id, short_name=parent.short_name)].append(parents)
    return await get_item_parents(parent, session, parents)


@router.post("/search", response_model=list[ItemPublic])
async def get_item_search(query: Query, session: SessionDep):
    """
    Search for items based on a query object, post to allow for body.
    """
    try:
        statement = select(Item)
        term_fields = ["short_name"]
        # Term
        if query.term:
            statement = statement.where(or_(*[col(getattr(Item, key)).contains(query.term) for key in term_fields]))

        # Filters
        if query.filters:
            statement = statement.where(
                or_(*[col(getattr(Item, key)).contains(term) for key, term in query.filters.items()])
            )

        # Offset & limits
        statement = statement.offset(query.offset).limit(query.limit)

        # Order & sort
        if query.sort_by:
            if query.sort_desc:
                statement = statement.order_by(getattr(Item, query.sort_by).desc())
            else:
                statement = statement.order_by(getattr(Item, query.sort_by))
    except (KeyError, AttributeError) as e:
        print(e)
        raise HTTPException(status_code=400, detail="Your query is bad and you should feel bad!") from None

    print(statement)
    results = await session.execute(statement)
    return results.scalars().all()


# TODO
# @router.post("/csv-import", response_model=ItemChangedResponse)
# async def bulk_import_items(
#     request: Request,
#     items: list[ItemRequest],
# ) -> ItemChangedResponse:
#     """
#     Bulk import items. Accepts a list of item dicts.
#     If an item with the same tag_uuid exists, it is updated; otherwise, it is created.
#     """
#     db = get_bs(request).dbc
#     imported = 0
#     updated = 0
#     errors = []
#     error_items = []
#     for idx, item_req in enumerate(items):
#         try:
#             # Remove None values, use defaults for missing fields
#             item_dict = {k: v for k, v in item_req.model_dump(exclude_none=True).items()}
#             item = Item.model_validate(item_dict, strict=False, from_attributes=True)
#             # Try to update existing item
#             result = db.update(
#                 collection_name="items",
#                 query={"tag_uuid": item.tag_uuid},
#                 update_values=item.model_dump(mode="json", by_alias=True),
#             )

#             if result:
#                 updated += 1
#             else:
#                 error_items.append(item.tag_uuid)
#         except pymongo.errors.DuplicateKeyError:
#             # If not found, create new
#             db.create(
#                 collection_name="items",
#                 document=item.model_dump(mode="json", by_alias=True),
#             )
#             imported += 1
#         except Exception as e:
#             errors.append(f"Row {idx}: {str(e)}")
#             if tag_uuid := item_dict.get("tag_uuid"):
#                 error_items.append(tag_uuid)

#     if imported == 0 and updated == 0 and not errors:
#         logger.warning(error_items)
#         raise HTTPException(
#             status_code=406,
#             detail={
#                 "message": "Not Modified. No items imported or updated.",
#                 "errors": errors,
#                 "error_items": error_items,
#             },
#         )
#     if errors:
#         raise HTTPException(
#             status_code=422,
#             detail={
#                 "message": "Validation error: Some items are invalid. Please check your input.",
#                 "errors": errors,
#                 "error_items": error_items,
#             },
#         )

#     msg = f"{imported} item(s) imported, {updated} item(s) updated successfully."
#     if errors:
#         msg += f" {len(errors)} error(s): {'; '.join(errors)}"
#     return ItemChangedResponse(message=msg, errors=errors, error_items=error_items)
