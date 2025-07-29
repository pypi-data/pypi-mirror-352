import logging
from pydantic import BaseModel
import requests

from epx.core.cloud.auth import platform_api_headers
from epx.core.errors.api_errors import UnauthorizedUserError
from epx.core.types.error_type import ForbiddenResponse
from epx.core.utils.config import read_auth_config

logger = logging.getLogger(__name__)


class _GetSignedUploadUrl(BaseModel):
    """Response object of presigned url.

    Attributes
     ----------
    url: str
        The presigned url from s3 for uploading models.
    """

    url: str


def get_signed_upload_url(payload: dict) -> str:
    """Request to FRED Cloud API to get signed url for uploading models.

    Raises
    ------
    UnauthorizedUserError
        If the user does not have sufficient privileges to perform the
        specified action on FRED Cloud.
    RuntimeError
        If a FRED Cloud server error occurs.
    """

    endpoint_url = f"{read_auth_config('api-url')}/jobs"
    logger.debug("Request payload: %s", payload)
    response = requests.post(endpoint_url, headers=platform_api_headers(), json=payload)
    logger.debug(f"Post response: {response.text}")
    # Check HTTP response status code and raise exceptions as appropriate
    if not response.ok:
        if response.status_code == requests.codes.forbidden:
            logger.error(
                ForbiddenResponse.model_validate_json(response.text).description
            )
            raise UnauthorizedUserError(
                ForbiddenResponse.model_validate_json(response.text).description
            )
        else:
            logger.error(
                f"FRED Cloud error code: {response.status_code} : {response.text}"
            )
            raise RuntimeError(f"FRED Cloud error code: {response.status_code}")

    response_payload = response.text
    logger.debug("HTTP response body: %s", response.text)
    response_body = _GetSignedUploadUrl.model_validate_json(response_payload)
    return response_body.url


def upload_file_to_s3_with_presigned_url(file_path, presigned_url) -> bool:
    """Upload models as a zip file to FRED Cloud API using signed url."""

    try:
        # Open the file to upload
        with open(file_path, "rb") as file_data:
            # Upload the file to S3 using the presigned URL
            response = requests.put(presigned_url, data=file_data)
            # Check if the upload was successful
            if response.status_code == 200:
                print("File uploaded successfully!")
                logger.info("File uploaded successfully!")
                return True
            else:
                print("Failed to upload file.")
                logger.error("Failed to upload file.")
                return False

    except Exception as e:
        print("\n Exception=", e)
        logger.error("\n Exception=", e)
        return False
