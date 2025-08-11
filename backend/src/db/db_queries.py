from datetime import datetime

from bson.objectid import ObjectId
from pymongo.database import Database

COLLECTION_NAME = "queries"


def create_query(query_data, db: Database):
    collection = db[COLLECTION_NAME]
    query_data_dict = query_data.dict()
    query_data_dict["created_at"] = datetime.now().isoformat()
    query_data_dict["updated_at"] = datetime.now().isoformat()
    result = collection.insert_one(query_data_dict)
    query_data_dict["_id"] = str(result.inserted_id)
    return query_data_dict


def get_query_by_name(name: str, db: Database):
    collection = db[COLLECTION_NAME]
    query = collection.find_one({"name": name})
    if query:
        query["_id"] = str(query["_id"])
    return query


def get_query_by_id(id: str, db: Database):
    collection = db[COLLECTION_NAME]
    query = collection.find_one({"_id": ObjectId(id)})
    if query:
        query["_id"] = str(query["_id"])
    return query


def get_all_queries(db: Database):
    collection = db[COLLECTION_NAME]
    queries = collection.find().to_list(length=None)
    for query in queries:
        query["_id"] = str(query["_id"])
    return queries


def update_query(id: str, query_data, db: Database):
    collection = db[COLLECTION_NAME]
    query_data_dict = query_data.dict()
    query_data_dict["updated_at"] = datetime.now().isoformat()
    result = collection.update_one({"_id": ObjectId(id)}, {"$set": query_data_dict})
    if result.matched_count:
        return get_query_by_id(id, db)
    return None


def delete_query(id: str, db: Database):
    collection = db[COLLECTION_NAME]
    result = collection.delete_one({"_id": ObjectId(id)})
    return result.deleted_count > 0
