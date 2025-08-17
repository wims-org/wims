from datetime import datetime

from bson.objectid import ObjectId
from pymongo.database import Database

from models.database import User

COLLECTION_NAME = "users"


def create_user(user_data: User, db: Database) -> User:
    collection = db[COLLECTION_NAME]
    user_data_dict = user_data.dict()
    user_data_dict["created_at"] = datetime.now().isoformat()
    user_data_dict["updated_at"] = datetime.now().isoformat()
    result = collection.insert_one(user_data_dict)
    user_data_dict["_id"] = str(result.inserted_id)
    return User(**user_data_dict)


def get_user_by_name(name: str, db: Database) -> User | None:
    collection = db[COLLECTION_NAME]
    user = collection.find_one({"username": name})
    if not user:
        return None
    user["_id"] = str(user["_id"])
    return User(**user)


def get_user_by_id(id: str, db: Database) -> User | None:
    collection = db[COLLECTION_NAME]
    user = collection.find_one({"_id": ObjectId(id)})
    if user:
        user["_id"] = str(user["_id"])
    return User(**user) if user else None


def get_all_users(db: Database) -> list[User]:
    collection = db[COLLECTION_NAME]
    users = collection.find().to_list(length=None)
    for user in users:
        user["_id"] = str(user["_id"])
    return [User(**user) for user in users]


def update_user(id: str, user_data: User, db: Database) -> User | None:
    collection = db[COLLECTION_NAME]
    user_data_dict = user_data.dict()
    user_data_dict["updated_at"] = datetime.now().isoformat()
    result = collection.update_one({"_id": ObjectId(id)}, {"$set": user_data_dict})
    if result.matched_count:
        return get_user_by_id(id, db)
    return None


def delete_user(id: str, db: Database) -> bool:
    collection = db[COLLECTION_NAME]
    result = collection.delete_one({"_id": ObjectId(id)})
    return result.deleted_count > 0
