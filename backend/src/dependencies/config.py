import json
import os
from pathlib import Path

import jsonschema
import yaml
from deepmerge import always_merger
from loguru import logger

from utils import update

# todo use pydantic config or similar?


def read_default_config() -> dict:
    """
    Reads the default config file and returns it as a dictionary.
    :return: Default config dictionary.
    """
    return {}  # it ain't much but its honest config


def read_file_config(config_file_path: dict) -> dict:
    """
    Reads the config file and validates it against the schema.
    :param config_file_path: Path to the config file.
    :return: Config dictionary.
    :raises FileNotFoundError: If the config file is not found.
    :raises ValueError: If the config file is not valid.
    """
    try:
        with open(config_file_path) as file:
            return yaml.safe_load(file)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Config file {config_file_path.absolute} not found") from e
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing config file: {e}") from e


def read_env_config(config: dict) -> dict:
    """
    Reads environment variables and updates the config dictionary by splitting dot-notated key-value pairs.
    :param config: Config dictionary.
    :return: Updated config dictionary.
    """
    for key in os.environ.copy():
        try:
            update(key, config, os.environ[key])
        except (KeyError, TypeError) as e:
            logger.error(f"Error updating config key {key}, check config file and environment variables: {e}")
    # This is maybe a bit too verbose, innit?
    # logger.debug(f"Config: {config}")
    return config


def validate_config(config: dict) -> bool:
    """
    Validates the config dictionary against the JSON schema and logs errors.
    :param config: Config dictionary.
    """
    with open(Path(__file__).parent.parent.parent / "schemas" / "config_schema.json") as file:
        config_schema = json.load(file)
    validator = jsonschema.Draft202012Validator(config_schema)
    for err in validator.iter_errors(config):
        logger.error(f"Config file validation error: {err}")


def read_config() -> dict:
    config = read_default_config()

    if path_env := os.environ.get("CONFIG_FILE"):
        config_file_path = Path(path_env)
    else:
        config_file_path = Path("__file__").parent.absolute() / "config.yml"
    try:
        config = always_merger.merge(config, read_file_config(config_file_path))
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Error reading config file: {e}")
        config = {}

    config = read_env_config(config)
    validate_config(config)
    return config
