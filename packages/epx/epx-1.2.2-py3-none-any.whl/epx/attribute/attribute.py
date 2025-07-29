from typing import Optional, Dict
import logging
from epx.core.types.common import (
    UploadAttributeParams,
    AttributeSpec,
    AttributeResponse,
    UploadAttributeResponse,
    GetStatusUploadAttrRes,
)
from epx.core.utils.http_request import retry_request

logger = logging.getLogger(__name__)


class Attribute:
    def __init__(self, api_url=None):
        if not api_url:
            raise ValueError("The 'api_url' is required for call attribute api.")
        self.api_url = f"{api_url}/api/v1"

    def get_list_attribute(
        self,
        attribute_set: Optional[str] = None,
        max_retries: Optional[int] = None,
        backoff_factor: Optional[int] = None,
    ) -> AttributeResponse:
        """Retrieve a list attribute object from a attribute_set.

        Parameters
        ----------
        attribute_set : str
            The attribute_set of the attribute to retrieve.
        max_retries : int, optional
            Maximum number of retry attempts.
        backoff_factor : int, optional
            Factor by which the sleep time is increased.

        Returns
        -------
            ApiResponse
            A validated ApiResponse object containing 'message' and 'result' from
            the API response.
        """

        params: Dict[str, str] = {}
        if attribute_set:
            params["attribute_set"] = attribute_set
        endpoint_url = f"{self.api_url}/list"

        response = retry_request(
            method="GET",
            url=endpoint_url,
            params=params,
            json=None,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
        )
        data = response.json()

        if not response.ok:
            raise RuntimeError(f"Server error code: {response.status_code}")
        return AttributeResponse(**data)

    def get_status_upload(
        self,
        upload_id: str,
        max_retries: Optional[int] = None,
        backoff_factor: Optional[int] = None,
    ) -> GetStatusUploadAttrRes:
        """Response status upload attribute requests.

        Parameters
        ----------
        upload_id: str
        The upload_id is returned from the upload attribute.
        max_retries : int, optional
            Maximum number of retry attempts.
        backoff_factor : int, optional
            Factor by which the sleep time is increased.

        Returns
         -------
         dict
            A dictionary containing 'message' and 'result' from the API response.

        Raises
        ------
        ConnectionError
            If network connection issues.
        RuntimeError
            If a server error occurs.
        """
        if not upload_id:
            raise ValueError("The 'upload_id' is required.")

        endpoint_url = f"{self.api_url}/upload/{upload_id}"

        # Get status upload attribute by upload_id
        response = retry_request(
            method="GET",
            url=endpoint_url,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
        )

        data = response.json()

        if not response.ok:
            raise RuntimeError(f"Server error code: {response.status_code}")

        return GetStatusUploadAttrRes(**data)

    def delete_attribute(
        self,
        attribute_set: str,
        attribute_name: str,
        version: int,
        max_retries: Optional[int] = None,
        backoff_factor: Optional[int] = None,
    ) -> None:
        """Response delete attribute requests by attribute_set, attribute_name, version.
        Parameters
        ----------
        attribute_name: str
            The name of the attribute.
        attribute_set: str
            The name of the attribute set
        version: int
            The version of the desired attribute.
        attribute_set : str
            The attribute_set of the attribute to retrieve.
        max_retries : int, optional
            Maximum number of retry attempts.
        backoff_factor : int, optional
            Factor by which the sleep time is increased.

         Returns
         -------
         dict
            A dictionary containing 'message' and 'result' from the API response.

        Raises
        ------
        ConnectionError
            If network connection issues.
        RuntimeError
            If a server error occurs.
        """
        if not attribute_set:
            raise ValueError("The 'attribute_set' is required.")
        if not attribute_name:
            raise ValueError("The 'attribute_name' is required.")
        if version is None:
            raise ValueError("The 'version' is required.")

        def confirm() -> bool:
            answer = input(f"Delete attribute '{attribute_name}'? [y/N]")
            if answer.lower() in ["y", "yes"]:
                return True
            else:
                return False

        def proceed():
            endpoint_url = f"{self.api_url}/delete"

            payload = {}
            payload["attribute_set"] = attribute_set
            payload["attribute_name"] = attribute_name
            payload["version"] = version

            # Delete attribute
            response = retry_request(
                method="DELETE",
                url=endpoint_url,
                json=payload,
                max_retries=max_retries,
                backoff_factor=backoff_factor,
            )
            # Check HTTP response status code and raise exceptions as appropriate
            if not response.ok:
                raise RuntimeError(f"Server error code: {response.status_code}")

            print(f"Attribute {attribute_name} deleted successfully.")

        if confirm():
            proceed()

    def upload_attribute(
        self,
        spec: AttributeSpec,
        attribute_set: str,
        synth_pops: list[str],
        max_retries: Optional[int] = None,
        backoff_factor: Optional[int] = None,
    ) -> UploadAttributeResponse:
        """Handles the request to upload attribute data using the provided parameters.

        Parameters
        ----------
        spec : AttributeSpec
            The detailed specifications for the attribute to be uploaded.
        attribute_set : str
            The name of the attribute set (e.g., "epistemix").
        synth_pops : list[str]
            A list of synchronized population sets, e.g., ["0"]
        max_retries : int, optional
            Maximum number of retry attempts.
        backoff_factor : int, optional
            Factor by which the sleep time is increased.

        Returns
            -------
        UploadAttributeResponse
            A response object containing 'message' and 'upload_id' from the API

        Raises
        ------

        ConnectionError
            If network connection issues occur.
        RuntimeError
            If a server error occurs.
        """
        try:
            # Validate required fields
            params = UploadAttributeParams(
                spec=spec, attribute_set=attribute_set, synth_pops=synth_pops
            )

            # Prepare payload and API endpoint
            payload = params.model_dump(by_alias=True)

            endpoint_url = f"{self.api_url}/upload"

            # Make the API request to upload the attribute
            response = retry_request(
                method="POST",
                url=endpoint_url,
                json=payload,
                max_retries=max_retries,
                backoff_factor=backoff_factor,
            )
            data = response.json()

            # Check HTTP response status code
            if not response.ok:
                raise RuntimeError(f"Error: {response.status_code} - {response.text}")

            return UploadAttributeResponse(**data)
        except ValueError as e:
            logger.error(e)
            raise
