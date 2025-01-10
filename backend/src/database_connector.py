from typing import Any

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
        document = collection.find_one({"container_tag_id": rfid})
        return document

    def read(self, collection_name: str, query: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        collection: Collection = self.db[collection_name]
        documents = collection.find(query or {}, projection={"_id": False})
        return list(documents)

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
