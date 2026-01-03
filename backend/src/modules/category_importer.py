import argparse
import asyncio
import json
from collections.abc import Generator
from datetime import datetime
from pathlib import Path

import pymongo
from loguru import logger
from pydantic import ValidationError

from database_connector import MongoDBConnector
from models.database import Category

category_import_metadata_file = "category_data.import.json"


def collection_is_complete(db_connector: MongoDBConnector, collection_name: str, filepath: str) -> bool:
    """Reads the hash file next to the data file and compares it to the current collection hash"""
    import_file = Path(filepath).parent / category_import_metadata_file
    if not import_file.exists():
        logger.warning(f"Import file not found, category import was never successful: {import_file}")
        return False
    result = json.loads(import_file.read_text() or "{}")
    expected_md5 = result.get("md5", {})
    if not expected_md5:
        logger.error(f"MD5 hash not found in import file: {import_file}")
        import_file.unlink(missing_ok=True)
        return False
    res_data = db_connector.db.command({"dbHash": 1, "collections": [collection_name]})
    md5 = res_data.get("collections", {}).get(collection_name, None)
    logger.debug(f"DB Hash for {collection_name}: {res_data}, {md5} expected: {expected_md5}")
    if md5 != expected_md5:
        logger.error(f"MD5 mismatch for {collection_name}: {md5} != {expected_md5}")
        import_file.unlink(missing_ok=True)
        return False
    return True


def write_md5_to_file(db_connector: MongoDBConnector, collection_name: str, filepath: str) -> None:
    """Puts a hash file next to the data file to indicate successful import"""
    import_file = Path(filepath).parent / category_import_metadata_file
    res_data = db_connector.db.command({"dbHash": 1, "collections": [collection_name]})

    logger.debug(f"Writing DB Hash for {collection_name}: {res_data} to {import_file}")
    import_file.write_text(json.dumps({"md5": res_data.get("collections", {}).get(collection_name, None)}))


def import_category_data(db_connector: MongoDBConnector, collection_name: str, file_path: str | None = None):
    # supported format https://www.ungm.org/Public/category
    start_time = datetime.now()
    if file_path is None:
        file_path = str(Path(__file__).parent.parent.parent / "data" / "category_data.json")

    def create_category(cat_data: dict, parent_id: str | None = None) -> Generator[dict]:
        try:
            category = Category(
                title=cat_data.get("title"), description=cat_data.get("description"), parent_id=parent_id
            )
            result_id = None
            try:
                logger.info(f"Importing category data... insert {category.title}")
                result = db_connector.db[collection_name].insert_one(category.model_dump())
                result_id = result.inserted_id
            except pymongo.errors.DuplicateKeyError as e:
                print(e)
                result_id = db_connector.db[collection_name].find_one({"title": category.title}).get("_id", None)
            except pymongo.errors.PyMongoError as e:
                logger.warning(
                    f"Result importing category batch: {[(k, len(v)) for k, v in e.details.items() if type(v) is list]}"
                )

            if result_id:
                for child in cat_data.get("children", []):
                    create_category(child, result_id)
        except ValidationError as e:
            logger.warning(f"Skipped bad category {e}")

    for category in json.loads(Path(file_path).read_text()):
        create_category(category)
    logger.info(f"category data import completed successfully. Took {datetime.now() - start_time}")


def check_and_import_category_data(db_connector: MongoDBConnector, collection_name: str, file_path: str | None = None):
    try:
        if collection_name not in db_connector.db.list_collection_names():
            db_connector.db.create_collection(collection_name)
            db_connector.db[collection_name].create_index("parent_key")
            db_connector.db[collection_name].create_index("title", unique=True)
            logger.info(f"Category collection '{collection_name}' created.")
        if not collection_is_complete(db_connector, collection_name, file_path or ""):
            import_category_data(db_connector, collection_name, file_path)
            write_md5_to_file(db_connector, collection_name, file_path or "")
            logger.info(f"category data imported into collection '{collection_name}'.")
        else:
            logger.info(f"category data in collection '{collection_name}' is already complete.")
    except Exception as e:
        logger.exception(f"Error importing category data: {e}")


if __name__ == "__main__":
    logger.info("Starting category Importer")
    # read options from command line arguments for script usage
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file-path",
        type=str,
        default=str(Path(__file__).parent.parent.parent / "data" / "category_data.xlsx"),
        help="Path to the category data Excel file",
    )
    parser.add_argument("--config", type=dict, default={}, help="Configuration dictionary")
    args = parser.parse_args()

    db_connector = MongoDBConnector(
        uri=f"mongodb://{args.config.get('host', 'localhost')}:{args.config.get('port', '27017')}",
        database=args.config.get("database", "inventory"),
    )
    asyncio.run(
        check_and_import_category_data(
            db_connector,
            collection_name=args.collection,
            file_path=args.file_path,
        )
    )
