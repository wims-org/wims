import enum

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, or_

from dependencies.database import SessionDep
from models.category import Category
from models.item import File, Item, ItemBacklog, ItemCreate, ItemPublic, ItemUpdate

RELATION_MAP: dict[str, type] = {
    "category": Category,
}

router = APIRouter(prefix="/items", tags=["items"], responses={404: {"description": "Not found"}})


class Qualifier(enum.Enum):
    IN = "in"
    NOT_IN = "not_in"
    EQUALS = "eq"
    NOT_EQUALS = "not_eq"
    GREATER_THAN = "gt"
    LESS_THAN = "lt"


class FilterReq(BaseModel):
    field: str
    qualifier: Qualifier = Qualifier.EQUALS
    value: str | int | list[str | int]


class Filter(FilterReq):
    # since pydantic does not allow for nullable defaults, this wrapper is used
    qualifier: Qualifier | None = Field(default=None, description="If null, defaults to 'eq'.")


class QueryReq(BaseModel):
    term: str | None = None
    filters: list[Filter] = []
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1)
    sort_by: str | None = None
    sort_desc: bool = False


class Query(QueryReq):
    # since pydantic does not allow for nullable defaults, this wrapper is used
    filters: list[Filter] | None = Field(default=None, description="If null, defaults to empty list.")
    offset: int | None = Field(default=None, ge=0, description="If null, defaults to 0.")
    limit: int | None = Field(default=None, ge=1, description="If null, defaults to 10.")
    sort_desc: bool | None = Field(default=None, description="If null, defaults to False.")


class ContainerObject(BaseModel):
    item_id: int
    short_name: str


async def _add_item_ids_to_files(item_id: int, item_data: ItemCreate | ItemUpdate, session: AsyncSession) -> None:
    """Link uploaded files/images to an item by setting File.item_id."""
    """Why is this necessary? How to implicitly link existing files to items?"""
    payload_files = (item_data.images or []) + (item_data.files or [])
    if not payload_files:
        return

    requested_ids = sorted({f.id for f in payload_files})
    db_files = (await session.execute(select(File).where(File.id.in_(requested_ids)))).scalars().all()
    db_file_by_id = {db_file.id: db_file for db_file in db_files}

    missing_ids = [file_id for file_id in requested_ids if file_id not in db_file_by_id]
    if missing_ids:
        raise HTTPException(status_code=404, detail=f"File ids not found: {missing_ids}")

    for file_id in requested_ids:
        db_file = db_file_by_id[file_id]
        db_file.item_id = item_id
        session.add(db_file)


@router.post("", response_model=ItemPublic)
async def create_item(item: ItemCreate, session: SessionDep):
    db_item = Item.model_validate(item.model_dump(exclude={"images", "files"}))
    session.add(db_item)
    try:
        await session.commit()
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    await _add_item_ids_to_files(db_item.id, item, session)
    await session.commit()
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


@router.get("/{id}", response_model=ItemPublic)
async def get_item(session: SessionDep, id: int):
    item = await session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item id not found")
    return item


@router.get("/", response_model=list[ItemPublic])
async def get_all_item(session: SessionDep, offset: int = 0, limit: int = 10):
    return (await session.execute(select(Item).offset(offset).limit(limit))).scalars().all()


@router.put("/{id}", response_model=ItemPublic)
async def update_item(id: int, item: ItemUpdate, session: SessionDep):
    db_item = await session.get(Item, id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    update = item.model_dump(exclude={"images", "files"})
    db_item.sqlmodel_update(update)
    if db_item.container_id:
        if db_item.id is db_item.container_id:
            raise HTTPException(status_code=400, detail="Circular Dependency: Self-reference!")
        parents = await get_item_parents(db_item, session)
        parent_ids = [p.item_id for p in parents]
        if db_item.id in parent_ids:
            raise HTTPException(
                status_code=400,
                detail=f"Circular Dependency: {parents[parent_ids.index(db_item.id) + 1].short_name} "
                "stored in {db_item.short_name}",
            )
    session.add(db_item)
    await _add_item_ids_to_files(db_item.id, item, session)
    await session.commit()
    await session.refresh(db_item)
    return db_item


@router.delete("/{id}")
async def delete_item(id: int, session: SessionDep):
    item = await session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    await session.delete(item)
    await session.commit()
    return {"ok": True}


@router.get("/{id}/containers", response_model=list[ContainerObject])
async def get_item_with_containers(id: int, session: SessionDep):
    # recursive query to get all parent containers of an item, starting from the item itself,
    # and return a list of ContainerObjects with item_id and short_name
    item = await session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return await get_item_parents(item, session, parents=[ContainerObject(item_id=item.id, short_name=item.short_name)])


async def get_item_parents(item: Item, session: AsyncSession, parents: list = None) -> list[ContainerObject]:
    if parents is None:
        parents = []
    if item.container_id is None:
        return parents
    parent = await session.get(Item, item.container_id)
    if parent.id in [p.item_id for p in parents]:
        return parents
    parents = [ContainerObject(item_id=parent.id, short_name=parent.short_name)] + parents
    return await get_item_parents(parent, session, parents)


@router.post("/search", response_model=list[ItemPublic])
async def get_item_search(query: Query, session: SessionDep):
    """
    Search for items based on a query object, post to allow for body.
    """
    try:
        query = QueryReq.model_validate(
            query,
        )
        statement = select(Item)
        term_fields = ["short_name"]
        # Term
        if query.term:
            statement = statement.where(or_(*[col(getattr(Item, key)).contains(query.term) for key in term_fields]))

        # Filters
        for filter in query.filters or []:
            if "." in filter.field:
                relation_name, field_name = filter.field.split(".", 1)
                if relation_name not in RELATION_MAP:
                    raise HTTPException(status_code=400, detail=f"Invalid filter relation: {relation_name}")
                related_model = RELATION_MAP[relation_name]
                if not hasattr(related_model, field_name):
                    raise HTTPException(status_code=400, detail=f"Invalid filter field: {filter.field}")
                statement = statement.join(related_model)
                column = getattr(related_model, field_name)
            else:
                if filter.field not in Item.model_fields:
                    raise HTTPException(status_code=400, detail=f"Invalid filter field: {filter.field}")
                column = getattr(Item, filter.field)

            match filter.qualifier or Qualifier.EQUALS:
                case Qualifier.EQUALS:
                    statement = statement.where(column == filter.value)
                case Qualifier.NOT_EQUALS:
                    statement = statement.where(column != filter.value)
                case Qualifier.IN:
                    statement = statement.where(column.in_(filter.value))
                case Qualifier.NOT_IN:
                    statement = statement.where(~column.in_(filter.value))
                case Qualifier.GREATER_THAN:
                    statement = statement.where(column > filter.value)
                case Qualifier.LESS_THAN:
                    statement = statement.where(column < filter.value)

        # Offset & limits
        statement = statement.offset(query.offset or 0).limit(query.limit or 10)

        # Order & sort
        if query.sort_by:
            if query.sort_desc:
                statement = statement.order_by(getattr(Item, query.sort_by).desc())
            else:
                statement = statement.order_by(getattr(Item, query.sort_by))
    except (ValidationError, ValueError) as e:
        raise HTTPException(status_code=422, detail=f"Validation error: {str(e)}") from e
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
#     If an item with the same code exists, it is updated; otherwise, it is created.
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
#                 query={"code": item.code},
#                 update_values=item.model_dump(mode="json", by_alias=True),
#             )

#             if result:
#                 updated += 1
#             else:
#                 error_items.append(item.code)
#         except pymongo.errors.DuplicateKeyError:
#             # If not found, create new
#             db.create(
#                 collection_name="items",
#                 document=item.model_dump(mode="json", by_alias=True),
#             )
#             imported += 1
#         except Exception as e:
#             errors.append(f"Row {idx}: {str(e)}")
#             if code := item_dict.get("code"):
#                 error_items.append(code)

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
