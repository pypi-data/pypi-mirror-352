import time
import logging

import requests

from epx.core.utils.config import (
    check_positive_integer,
    get_max_retry_value,
    read_auth_config,
)


logger = logging.getLogger(__name__)


def retry_request(
    method,
    url,
    headers=None,
    params=None,
    data=None,
    json=None,
    max_retries=None,
    backoff_factor=None,
):
    """
    Makes an HTTP request with retries and exponential backoff.

    Args:
        method (str): HTTP method to use ('GET', 'POST', etc.).
        url (str): The endpoint URL.
        headers (dict): Headers for the HTTP request.
        params (dict): Query parameters for GET requests.
        data (dict): Form data for POST requests.
        json (dict): JSON payload for POST requests.
        max_retries (int): Maximum number of retry attempts.
        backoff_factor (int): Factor by which the sleep time is increased.

    Returns:
        requests.Response: The HTTP response object.

    Raises:
        ConnectionError
            If all retries fail.
    """

    if max_retries is None:
        max_retries = get_max_retry_value("max_retries_connection", 3)
    max_retries = check_positive_integer(max_retries, "max-retries")

    if backoff_factor is None:
        try:
            backoff_factor = read_auth_config("backoff-factor")
        except Exception:
            backoff_factor = 2  # Default value

    backoff_factor = check_positive_integer(backoff_factor, "backoff-factor")

    for attempt in range(max_retries):
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=data,
                json=json,
            )
            return response
        except requests.exceptions.ConnectionError as e:
            if attempt < max_retries - 1:
                sleep_time = backoff_factor**attempt
                logger.error(
                    f"Connection reset error: {e} "
                    + f"--- Retrying in {sleep_time} seconds..."
                )
                time.sleep(sleep_time)
            else:
                logger.error("All retries FAILED:" + f" Connection reset error: {e}")
                raise e
