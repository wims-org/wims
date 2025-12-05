from typing import Any

from loguru import logger
from pymongo.collection import Collection

from models.database import Category


def get_category_with_parents_and_children(db, category_key: str | int) -> dict:
    pipeline = [
        {"$match": {"unspsc_code": category_key}},
        {
            "$lookup": {
                "from": "categories",
                "localField": "parent_key",
                "foreignField": "key",
                "as": "parent",
                "pipeline": [
                    {"$limit": 1},
                ],
            }
        },
        {
            "$lookup": {
                "from": "categories",
                "localField": "key",
                "foreignField": "parent_key",
                "as": "children",
            }
        },
        {"$unwind": {"path": "$parent", "preserveNullAndEmptyArrays": True}},
    ]
    return next(db["categories"].aggregate(pipeline), None)


def get_category_tree(db, collection_name: str, unspsc_code: str) -> Category | None:
    """Returns a recursive nested object"""
    collection: Collection = db[collection_name]
    logger.debug(f"Getting category tree for UNSPSC code: {unspsc_code} from collection: {collection_name}")
    if not (doc := collection.find_one({"unspsc_code": unspsc_code})):
        return None
    doc = Category.model_validate(doc, strict=False)

    def get_category_recursive(unspsc_code: str) -> dict[str, Any] | None:
        if not (doc := collection.find_one({"key": unspsc_code})):
            return None
        logger.debug(f"Fetching category for UNSPSC code: {unspsc_code}, found document: {doc}")
        doc = Category.model_validate(doc, strict=False)
        if parent_key := doc.parent_key:
            doc.parent = get_category_recursive(parent_key)
        return doc

    try:
        return get_category_recursive(doc.key)
    except Exception as e:
        logger.exception(f"Error fetching category tree for UNSPSC code {unspsc_code}: {e}")
        return None


def find_categories_by_title(db, title_query: str) -> list[dict]:
    regex_query = {"$regex": title_query, "$options": "i"}  # Case-insensitive search
    categories = list(db["categories"].find({"title": regex_query}))
    return categories

def get_categories(db, offset: int, limit: int) -> list[dict]:
    return list(db["categories"].find().skip(offset).limit(limit))