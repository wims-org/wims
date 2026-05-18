from __future__ import annotations

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from dependencies.database import SessionDep
from models.api import Query, QueryReq
from models.category import Category, CategoryCreate, CategoryPublic, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"], responses={404: {"description": "Not found"}})


@router.post("", response_model=CategoryPublic)
async def create_category(category: CategoryCreate, session: SessionDep):
    db_category = Category.model_validate(category)
    session.add(db_category)
    try:
        await session.commit()
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    await session.refresh(db_category)
    return db_category


@router.post("/search", response_model=list[CategoryPublic])
async def search_categories(query: Query, session: SessionDep):
    query = QueryReq.model_validate(query)
    return (await session.execute(select(Category).where(Category.title.ilike(f"%{query.term}%")))).scalars().all()


@router.get("", response_model=list[CategoryPublic])
async def get_all_categories(session: SessionDep, offset: int = 0, limit: int = 100):
    return (await session.execute(select(Category).offset(offset).limit(limit))).scalars().all()


@router.get("/tree", response_model=list[CategoryPublic])
async def get_category_tree(session: SessionDep):
    return (await session.execute(select(Category).where(Category.parent_id.is_(None)))).scalars().all()


@router.get("/{id}/tree", response_model=list[CategoryPublic])
async def get_category_tree_from_id(id: int, session: SessionDep):
    # return the tree of the given category starting from the respective root category (parent_id = None)
    category = await session.get(Category, id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    # find the upper-most parent category
    while category.parent_id is not None:
        category = await session.get(Category, category.parent_id)
    return category


@router.get("/{id}", response_model=CategoryPublic)
async def get_category(id: int, session: SessionDep):
    category = await session.get(Category, id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/{id}", response_model=CategoryPublic)
async def update_category(id: int, category: CategoryUpdate, session: SessionDep):
    db_category = await session.get(Category, id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    db_category.sqlmodel_update(category.model_dump(exclude_unset=True))
    session.add(db_category)
    await session.commit()
    await session.refresh(db_category)
    return db_category


@router.delete("/{id}")
async def delete_category(id: int, session: SessionDep):
    category = await session.get(Category, id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    await session.delete(category)
    await session.commit()
    return {"ok": True}
