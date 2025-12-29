from fastapi import APIRouter, HTTPException, Request, Response
from loguru import logger
from pydantic import ValidationError

from db import db_categories
from models.database import Category
from routers.utils import get_bs

router = APIRouter(prefix="/categories", tags=["categories"])


class CategoryReqRes(Category):
    parent: CategoryReqRes | None = None
    children: list[CategoryReqRes] = []


@router.get("/{id}", response_model=CategoryReqRes)
async def get_category(request: Request, id: str | int) -> Response | dict:
    db = get_bs(request).dbc.db
    category = db_categories.get_category_with_parents_and_children(db, id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found.")
    try:
        return CategoryReqRes.model_validate(category)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail="Invalid category data.") from e


@router.get("", response_model=list[CategoryReqRes])
async def get_categories(request: Request, offset: int = 0, limit: int = 100) -> Response | dict:
    db = get_bs(request).dbc.db
    existing = db_categories.get_categories(db, offset=offset, limit=limit)
    if not existing:
        raise HTTPException(status_code=404, detail="No categories found.")
    return existing


@router.get("/{id}/tree", response_model=CategoryReqRes)
async def get_category_tree(request: Request, id: str) -> Response | dict:
    logger.debug(f"Fetching category tree for id: {id}")
    category = db_categories.get_category_tree(get_bs(request).dbc.db, collection_name="categories", id=id)
    logger.debug(f"Fetched category tree: {category}")
    if not category:
        raise HTTPException(status_code=404, detail="Category not found.")
    try:
        return category
    except ValidationError as e:
        raise HTTPException(status_code=400, detail="Invalid category data.") from e


@router.get("/search/", response_model=list[CategoryReqRes])
async def search_categories(request: Request, term: str) -> Response | dict:
    logger.debug(f"Searching categories with title query: {term}")
    db = get_bs(request).dbc.db
    categories = db_categories.find_categories_by_title(db, title_query=term)
    logger.debug(f"Found categories: {categories}")
    if not categories:
        raise HTTPException(status_code=404, detail="No categories found.")
    try:
        return [CategoryReqRes.model_validate(cat) for cat in categories]
    except ValidationError as e:
        raise HTTPException(status_code=400, detail="Invalid category data.") from e
