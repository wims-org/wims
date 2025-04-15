import json
import os
from pathlib import Path

import jsonschema
import yaml
from loguru import logger

from utils import update


def read_config(config_file_path: Path = None) -> dict:
    """
    Reads the config file and validates it against the schema.
    :param config_file_path: Path to the config file.
    :return: Config dictionary.
    :raises FileNotFoundError: If the config file is not found.
    :raises ValueError: If the config file is not valid.
    """
    try:
        with open(Path(__file__).parent.parent.parent / "schemas" / "config_schema.json") as file:
            config_schema = json.load(file)
        with open(config_file_path or (Path("__file__").parent.absolute() / "config.yml")) as file:
            config = yaml.safe_load(file)
        validator = jsonschema.Draft202012Validator(config_schema)
        for err in validator.iter_errors(config):
            logger.error(f"Config file validation error: {err}")
        return config
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Config file {config_file_path.absolute} not found") from e
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing config file: {e}") from e


def read_env_config(config: dict) -> dict:
    """
    Reads environment variables and updates the config dictionary.
    :param config: Config dictionary.
    :return: Updated config dictionary.
    """
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
