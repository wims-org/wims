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
    category = db_categories.get_category_tree_up(get_bs(request).dbc.db, collection_name="categories", id=id)
    logger.debug(f"Fetched category tree: {category}")
    if not category:
        raise HTTPException(status_code=404, detail="Category not found.")
    try:
        return category
    except ValidationError as e:
        raise HTTPException(status_code=400, detail="Invalid category data.") from e


@router.get("/tree", response_model=list[CategoryReqRes])
async def get_all_categories_tree(request: Request) -> list[CategoryReqRes] | Response:
    logger.debug("Fetching all root categories for category tree")
    root_categories = db_categories.get_root_categories(get_bs(request).dbc.db, collection_name="categories")
    if not root_categories:
        raise HTTPException(status_code=404, detail="No category tree found.")
    for root_category in root_categories:
        tree = db_categories.get_category_tree_down(
            get_bs(request).dbc.db, collection_name="categories", id=root_category["_id"]
        )
        if tree:
            root_category.setdefault("children", tree["children"] or [])
    try:
        return root_categories
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


@router.post("/", response_model=CategoryReqRes)
async def create_category(request: Request, category: CategoryReqRes) -> Response | dict:
    db = get_bs(request).dbc.db
    category_dict = category.model_dump(exclude_unset=True, exclude={"children", "parent"})
    result = db["categories"].insert_one(category_dict)
    created_category = db["categories"].find_one({"_id": result.inserted_id})
    if not created_category:
        raise HTTPException(status_code=500, detail="Failed to create category.")
    try:
        return CategoryReqRes.model_validate(created_category)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail="Invalid category data.") from e
