from typing import Any

from bson import ObjectId
from loguru import logger
from pymongo.collection import Collection


def get_category_with_parents_and_children(db, term: str | int) -> dict:
    logger.debug(f"Getting category with parents and children for term: {term}")
    pipeline = []
    try:
        _id = ObjectId(term)
        pipeline += [{"$match": {"_id": _id}}]
    except Exception as e:
        logger.debug(f"Term is not a valid ObjectId: {e}")
        pipeline += [{"$match": {"title": {"$regex": term, "$options": "i"}}}]

    pipeline += [
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


def get_category_tree_up(db, collection_name: str, id: str) -> dict | None:
    """Returns a recursive nested object"""
    collection: Collection = db[collection_name]
    logger.debug(f"Getting category tree for code: {id} from collection: {collection_name}")
    if not (doc := collection.find_one({"_id": id})):
        return None

    def get_category_recursive(id: str) -> dict[str, Any] | None:
        if not (doc := collection.find_one({"_id": id})):
            return None
        logger.debug(f"Fetching category for id: {id}, found document: {doc}")
        if parent_id := doc.get("parent_id"):
            doc["parent"] = get_category_recursive(parent_id)
        return doc

    try:
        return get_category_recursive(doc.id)
    except Exception as e:
        logger.exception(f"Error fetching category tree for id {id}: {e}")
        return None


def get_category_tree_down(db, collection_name: str, id: str) -> dict | None:
    """Returns a recursive nested object with children"""
    collection: Collection = db[collection_name]
    logger.debug(f"Getting category tree down for code: {id} from collection: {collection_name}")
    if not (doc := collection.find_one({"_id": id})):
        return None

    def get_category_recursive(id: str) -> dict[str, Any] | None:
        if not (doc := collection.find_one({"_id": id})):
            return None
        logger.debug(f"Fetching category for id: {id}, found document: {doc}")
        children_cursor = collection.find({"parent_id": doc["_id"]})
        doc["children"] = [get_category_recursive(child_doc["_id"]) for child_doc in children_cursor]
        return doc

    try:
        return get_category_recursive(doc["_id"])
    except Exception as e:
        logger.exception(f"Error fetching category tree for id {id}: {e}")
        return None


def get_root_categories(db, collection_name: str) -> list[dict]:
    return list(db[collection_name].find({"parent_id": None}))


def find_categories_by_title(db, title_query: str) -> list[dict]:
    # Case-insensitive search
    regex_query = {"$regex": title_query, "$options": "i"}
    categories = list(db["categories"].find({"title": regex_query}))
    return categories


def get_categories(db, offset: int, limit: int) -> list[dict]:
    # with id
    return list(db["categories"].find().skip(offset).limit(limit))
