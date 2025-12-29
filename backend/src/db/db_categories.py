from typing import Any

from loguru import logger
from pymongo.collection import Collection

from models.database import Category


def get_category_with_parents_and_children(db, category_key: str | int) -> dict:
    pipeline = [
        {"$match": {"_id": category_key}},
        {
            "$lookup": {
                "from": "categories",
                "localField": "parent_id",
                "foreignField": "_id",
                "as": "parent",
                "pipeline": [
                    {"$limit": 1},
                ],
            }
        },
        {
            "$lookup": {
                "from": "categories",
                "localField": "_id",
                "foreignField": "parent_id",
                "as": "children",
            }
        },
        {"$unwind": {"path": "$parent", "preserveNullAndEmptyArrays": True}},
    ]
    return next(db["categories"].aggregate(pipeline), None)


def get_category_tree(db, collection_name: str, id: str) -> Category | None:
    """Returns a recursive nested object"""
    collection: Collection = db[collection_name]
    logger.debug(f"Getting category tree for  code: {id} from collection: {collection_name}")
    if not (doc := collection.find_one({"_id": id})):
        return None
    doc = Category.model_validate(doc, strict=False)

    def get_category_recursive(id: str) -> dict[str, Any] | None:
        if not (doc := collection.find_one({"_id": id})):
            return None
        logger.debug(f"Fetching category for id: {id}, found document: {doc}")
        doc = Category.model_validate(doc, strict=False)
        if parent_key := doc.parent_key:
            doc.parent = get_category_recursive(parent_key)
        return doc

    try:
        return get_category_recursive(doc.key)
    except Exception as e:
        logger.exception(f"Error fetching category tree for id {id}: {e}")
        return None


def find_categories_by_title(db, title_query: str) -> list[dict]:
    regex_query = {"$regex": title_query, "$options": "i"}  # Case-insensitive search
    categories = list(db["categories"].find({"title": regex_query}))
    return categories


def get_categories(db, offset: int, limit: int) -> list[dict]:
    return list(db["categories"].find().skip(offset).limit(limit))
