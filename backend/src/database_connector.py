from typing import Any

import pydantic
from loguru import logger
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import ServerSelectionTimeoutError


class RecursiveContainerObject(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    tag_uuid: str
    short_name: str | None = None
    container: RecursiveContainerObject | None = None


class MongoDBConnector:
    def __init__(self, uri: str, database: str) -> None:
        try:
            self.client = MongoClient(
                uri,
                username="root",
                password="example",
                authSource="admin",
                authMechanism="SCRAM-SHA-256",
            )
            # Attempt to trigger server selection to catch connection errors early
            self.client.server_info()
            self.db = self.client[database]
        except ServerSelectionTimeoutError as e:
            logger.error(f"Could not connect to MongoDB server: {e}")
            self.client = None
            self.db = None

    def create(self, collection_name: str, document: dict[str, Any]) -> str | None:
        if self.db is None:
            logger.error("No database connection available for create operation.")
            return None
        collection: Collection = self.db[collection_name]
        result = collection.insert_one(document)
        return str(result.inserted_id)

    def find_by_rfid(self, collection_name: str, rfid: str) -> dict[str, Any] | None:
        if self.db is None:
            logger.error("No database connection available for find_by_rfid operation.")
            return None
        collection: Collection = self.db[collection_name]
        pipeline = [
            {"$match": {"tag_uuid": rfid}},
            {
                "$lookup": {
                    "from": "items",
                    "let": {"tag": "$tag_uuid"},
                    "pipeline": [
                        {"$match": {"$expr": {"$eq": ["$container_tag_uuid", "$$tag"]}}},
                        {"$project": {"_id": 1}},
                        {"$limit": 1},
                    ],
                    "as": "contained",
                },
            },
            {
                "$addFields": {
                    "container_tag_exists": {"$ne": ["$container_tag_uuid", None]},
                    "container_tag_uuid_copy": "$container_tag_uuid",
                }
            },
            {
                "$lookup": {
                    "from": "items",
                    "localField": "container_tag_uuid_copy",
                    "foreignField": "tag_uuid",
                    "as": "container",
                }
            },
            {"$unwind": {"path": "$container", "preserveNullAndEmptyArrays": True}},
        ]
        return next(collection.aggregate(pipeline), None)

    def get_recursive_container_tags(self, collection_name: str, rfid: str) -> RecursiveContainerObject | None:
        """Returns a recursive nested object each containing their container tag and
            respective short_name attribute for a given RFID tag.
         example:
        {
            "tag_uuid": "RFID1",
            "short_name": "RFID1",
            "container": {
                    "tag_uuid": "RFID2",
                    "short_name": "RFID2",
                    "container": {
                            "tag_uuid": "RFID3",
                            "short_name": "RFID3",
                            "container": None
                        }
                }
        }
        """
        collection: Collection = self.db[collection_name]

        def get_container_recursive(tag_uuid: str) -> dict[str, Any] | None:
            doc = collection.find_one(
                {"tag_uuid": tag_uuid}, {"_id": 0, "tag_uuid": 1, "short_name": 1, "container_tag_uuid": 1}
            )
            if not doc:
                return None
            container_tag_uuid = doc.get("container_tag_uuid")
            container = (
                get_container_recursive(container_tag_uuid)
                if container_tag_uuid and container_tag_uuid is not tag_uuid
                else None
            )
            return {"tag_uuid": doc["tag_uuid"], "short_name": doc.get("short_name"), "container": container}

        return get_container_recursive(rfid)

    def read(self, collection_name: str, query: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        if self.db is None:
            logger.error("No database connection available for read operation.")
            return []
        collection: Collection = self.db[collection_name]
        documents = list(collection.find(query or {}, projection={"_id": False}))
        return documents

    def update(
        self, collection_name: str, query: dict[str, Any], update_values: dict[str, Any], upsert: bool = False
    ) -> int:
        if self.db is None:
            logger.error("No database connection available for update operation.")
            return 0
        collection: Collection = self.db[collection_name]
        result = collection.update_many(query, {"$set": update_values}, upsert=upsert)
        return result.modified_count

    def delete(self, collection_name: str, query: dict[str, Any]) -> int:
        if self.db is None:
            logger.error("No database connection available for delete operation.")
            return 0
        collection: Collection = self.db[collection_name]
        result = collection.delete_many(query)
        return result.deleted_count

    def close(self) -> None:
        self.client.close()

    def is_connected(self) -> bool:
        if self.client is None:
            return False
        try:
            self.client.server_info()
            return True
        except ServerSelectionTimeoutError:
            return False

    def check_category_collection_exists(self) -> bool:
        if self.db is None:
            logger.error("No database connection available to check category collection.")
            return False
        return "categories" in self.db.list_collection_names()

    def create_category_collection(self) -> None:
        if self.db is None:
            logger.error("No database connection available to create category collection.")
            return
        self.db.create_collection("categories")
        self.db["categories"].create_index("title", unique=True)
