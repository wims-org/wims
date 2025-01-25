import logging
import os
from pathlib import Path

import yaml

from utils import update

global config

logger = logging.getLogger("uvicorn.error")


def read_config():
    config = {}
    try:
        with open(Path("__file__").parent.absolute() / "config.yml") as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        logger.error(
            "Config file not found. You may create a config file at src/config.yml by coping the example file."
        )
        return {}
    except yaml.YAMLError as e:
        logger.error(f"Error reading config file: {e}")
    for key in os.environ.copy():
        update(key, config, os.environ[key])
    logger.debug(f"Config: {config}")
    return config
