"""Global configuration for the EPX client."""

import os
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def get_storage_dir() -> Path:
    """Returns the path to the root storage directory for the EPX client.

    This directory includes `config.json` file and `job_data` directory
    If the environment variable ``EPX_STORAGE_DIR`` is set,
    this is used. Otherwise, the default location is ``~/.epx``.
    """

    try:
        return Path(os.environ["EPX_STORAGE_DIR"])
    except KeyError:
        return Path.home().resolve() / ".epx"


def get_job_storage_dir() -> Path:
    """Returns the path to the root storage directory for job data.

    This directory is used to store all data related to job executions
    such as input files, and output results.
    """

    return get_storage_dir() / "job_data"


def get_auth_config_dir() -> Path:
    return get_storage_dir() / "config.json"


def read_auth_config(key: str) -> str:
    # If the key is "api-url", try reading from the environment variable first
    if key == "api-url":
        env_value = os.environ.get("PLATFORM_API_URL")
        if env_value:
            return env_value
        logger.debug(
            "PLATFORM_API_URL not found in environment, falling back to config.json"
        )

    config_file = get_auth_config_dir()
    if not config_file.exists():
        raise FileNotFoundError(f"Config auth file not found at {config_file}")

    # Read content file config
    with config_file.open("r") as f:
        config = json.load(f)

    if key not in config:
        raise ValueError(
            f"Key '{key}' not found in config file. Please add in file config.json"
        )

    value = config[key]
    if not value:
        raise ValueError(
            f"Key '{key}' has no value or is empty in config file. Please add in file "
            "config.json"
        )

    return value


def check_positive_integer(value, attribute_name):
    if not isinstance(value, int) or value <= 0:
        raise ValueError(
            f"'{attribute_name}' must be a positive integer, but got {value}."
        )
    return value


def get_max_retry_value(attribute_name: str, default_value=1) -> int:
    """
    Retrieves the maximum retry value for a given attribute from the configuration.

    Arguments:
    attribute_name: str
        The name of the attribute to fetch from the configuration.
    default_value: int:
        The fallback value to use if the attribute is not found or an exception occurs.
        Default is 1.

    Returns:
        int: The maximum retry value
    Raises:
        ValueError: If the retrieved value is in valid.
    """

    try:
        max_retries = read_auth_config(attribute_name)
    except Exception:
        return default_value

    return check_positive_integer(max_retries, attribute_name)
