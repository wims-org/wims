import json
from pathlib import Path
from threading import Thread

import openai
from loguru import logger

from database_connector import MongoDBConnector
from modules import category_importer, chatgpt
from utils import find


class BackendService:
    def __init__(self, db_config, config):
        self.config = config
        self.dbc_legacy = MongoDBConnector(
            uri=f"mongodb://{db_config.get('host', 'localhost')}:{db_config.get('port', '27017')}",
            database=db_config.get("database", "inventory"),
        )

        # Read the schema from the file
        with open(Path(__file__).parent.parent.parent / "schemas" / "llm_schema.json") as schema_file:
            schema = json.load(schema_file)

        try:
            self.llm_completion = chatgpt.ChatGPT(
                api_key=find(key := "features.openai.api_key", config), response_schema=schema
            )
        except (KeyError, TypeError, openai.OpenAIError) as e:
            logger.error(f"Error getting config key {key}, check config file and environment variables: {e}")
            self.llm_completion = None


        # Start category data import in the background, if needed
        if (cat_file := (Path(__file__).parent.parent.parent / "data" / "categories.json")).exists():
            import_thread = Thread(
                target=category_importer.check_and_import_category_data,
                args=(self.dbc, "categories", str(cat_file)),
            )
            import_thread.start()
        else:
            logger.warning(
                f"Category data file '{cat_file}' not found. Skipping category import."
                f"Add the file to enable automatic category import on startup."
            )
        logger.info("BackendService initialized")

    def is_ready(self) -> bool:
        return self.dbc.is_connected()
