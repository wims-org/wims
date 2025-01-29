import json
import logging
import os
from pathlib import Path

import jsonschema
import yaml

from utils import update

global config

logger = logging.getLogger("uvicorn.error")


def read_config():
    config = {}
    try:
        with open(Path(__file__).parent.parent.parent / "schemas" / "config_schema.json") as file:
            config_schema = json.load(file)
        with open(Path("__file__").parent.absolute() / "config.yml") as file:
            config = yaml.safe_load(file)
        validator = jsonschema.Draft202012Validator(config_schema)
        for err in validator.iter_errors(config):
            logger.error(f"Config file validation error: {err}")
    except FileNotFoundError as e:
        logger.error(
            f"Config file not found. You may create an instance-agnostic config file at /app/src/config.yml by coping \
the example file. Config values can be overridden by environment variables. {e}"
        )
        return {}
    except yaml.YAMLError as e:
        logger.error(f"Error reading config file: {e}")
    for key in os.environ.copy():
        try:
            update(key, config, os.environ[key])
        except (KeyError, TypeError) as e:
            logger.error(
                f"Error updating config key {
                         key}, check config file and environment variables: {e}"
            )
    logger.debug(f"Config: {config}")
    return config
