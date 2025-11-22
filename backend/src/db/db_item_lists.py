from datetime import datetime

from pymongo.database import Database


def get_items_borrowed(db: Database):
    """Get a list of items borrowed by any user."""
    return db["items"].find({"borrowed_by": {"$regex": ".+"}}).sort("borrowed_at", -1)


def get_new_items_since(date: datetime, db: Database):
    """Get a list of items added since a specific date."""
    return db["items"].find({"created_at": {"$gte": date}}).sort("created_at", -1)


def get_new_items_latest(offset: int, db: Database):
    """Get a list of items added since a specific date."""
    return db["items"].find().sort("created_at", -1).skip(offset).limit(10)


def get_item_with_resolved_container(item_id: str, db: Database):
    """Get an item and resolve its container information."""
    item = db["items"].find_one({"tag_uuid": item_id})
    if item:
        item["container"] = db["containers"].find_one(
            {"_id": item["container_id"]})
    return item
