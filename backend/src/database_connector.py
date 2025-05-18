from typing import Any

from loguru import logger
from pymongo import MongoClient
from pymongo.collection import Collection


class MongoDBConnector:
    def __init__(self, uri: str, database: str) -> None:
        self.client = MongoClient(
            uri,
            username="root",
            password="example",
            authSource="admin",
            authMechanism="SCRAM-SHA-256",
        )
        self.db = self.client[database]

    def create(self, collection_name: str, document: dict[str, Any]) -> str | None:
        collection: Collection = self.db[collection_name]
        result = collection.insert_one(document)
        return str(result.inserted_id)

    def find_by_rfid(self, collection_name: str, rfid: str) -> dict[str, Any] | None:
        collection: Collection = self.db[collection_name]
        # todo
        pipeline = [
            {"$match": {"tag_uuid": rfid}},
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
            {"$project": {"_id": 0, "container._id": 0}},
        ]
        return next(collection.aggregate(pipeline), None)

    def get_recursive_container_tags(self, collection_name: str, rfid: str) -> list[dict[str, Any]]:
        """ Returns a recursive nested object each containing their container tag and respective short_name attribute for a given RFID tag.
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
            doc = collection.find_one({"tag_uuid": tag_uuid}, {
                                      "_id": 0, "tag_uuid": 1, "short_name": 1, "container_tag_uuid": 1})
            if not doc:
                return None
            container_tag_uuid = doc.get("container_tag_uuid")
            container = get_container_recursive(
                container_tag_uuid) if container_tag_uuid and container_tag_uuid is not tag_uuid else None
            return {
                "tag_uuid": doc["tag_uuid"],
                "short_name": doc.get("short_name"),
                "container": container
            }

        result = get_container_recursive(rfid)
        return result if result else []

    def read(self, collection_name: str, query: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        collection: Collection = self.db[collection_name]
        documents = list(collection.find(
            query or {}, projection={"_id": False}))
        logger.debug(f"Documents found: {documents}")
        return documents

    def update(self, collection_name: str, query: dict[str, Any], update_values: dict[str, Any]) -> int:
        collection: Collection = self.db[collection_name]
        result = collection.update_many(query, {"$set": update_values})
        return result.modified_count

    def delete(self, collection_name: str, query: dict[str, Any]) -> int:
        collection: Collection = self.db[collection_name]
        result = collection.delete_many(query)
        return result.deleted_count

    def close(self) -> None:
        self.client.close()
