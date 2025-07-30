# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azure.identity import DefaultAzureCredential
from .base_rest_client import BaseRestClient
import time
from json.decoder import JSONDecodeError

DEFAULT_API_VERSION = "2025-04-01"  # Default API version for Azure Resource Manager


class ArmClient(BaseRestClient):
    """Simple Azure Resource Manager (ARM) client leveraging BaseRestClient for GET, PATCH, PUT, and DELETE operations.

    Handles authentication via Bearer token (pass as api_key) and supports standard ARM resource operations.
    """

    def __init__(self, api_key=None, max_retries=5, backoff_factor=1):
        """
        Initialize the ArmClient.

        Args:
            api_key (str, optional): API key or bearer token. If None, uses DefaultAzureCredential.
            max_retries (int): Maximum number of retries for requests.
            backoff_factor (int): Backoff factor for retries.
        """
        base_url = "https://management.azure.com"
        self._credential = None
        self._token_expires_on = None
        if api_key is None:
            # Use DefaultAzureCredential for authentication if no API key is provided
            self._credential = DefaultAzureCredential()
            token = self._credential.get_token("https://management.azure.com/.default")
            api_key = token.token
            self._token_expires_on = token.expires_on
        super().__init__(base_url, api_key=api_key, max_retries=max_retries, backoff_factor=backoff_factor)

    def _refresh_api_key_if_needed(self) -> None:
        """Refresh the API key if using DefaultAzureCredential and the token is close to expiration."""
        if self._credential is not None:
            now = int(time.time())
            # Refresh if less than 10 minutes (600 seconds) left
            if not self._token_expires_on or self._token_expires_on - now < 600:
                token = self._credential.get_token("https://management.azure.com/.default")
                self.api_key = token.token
                self.session.headers.update({'Authorization': f'Bearer {self.api_key}'})
                self._token_expires_on = token.expires_on

    def get_resource(self, resource_id, api_version=DEFAULT_API_VERSION, **kwargs) -> object:
        """
        Get an ARM resource by its resource ID.

        Args:
            resource_id (str): The ARM resource ID.
            api_version (str): The API version to use.
            **kwargs: Additional arguments for the request.

        Returns:
            object: The resource as a dict if JSON, or text/None otherwise.
        """
        self._refresh_api_key_if_needed()
        url = f"{self.base_url}{resource_id}?api-version={api_version}"
        response = self.get(url, **kwargs)
        try:
            return response.json()
        except JSONDecodeError:
            raise ValueError(f"Failed to decode JSON response from {url}: {response.text.strip()}")

    def patch_resource(self, resource_id, patch_body, api_version=DEFAULT_API_VERSION, **kwargs) -> object:
        """
        Patch an ARM resource.

        Args:
            resource_id (str): The ARM resource ID.
            patch_body (dict): The patch body to send.
            api_version (str): The API version to use.
            **kwargs: Additional arguments for the request.

        Returns:
            object: The resource as a dict if JSON, or text/None otherwise.
        """
        self._refresh_api_key_if_needed()
        url = f"{self.base_url}{resource_id}?api-version={api_version}"
        headers = kwargs.pop('headers', {})
        headers['Content-Type'] = 'application/json'
        response = self.patch(url, json=patch_body, headers=headers, **kwargs)
        try:
            return response.json()
        except JSONDecodeError:
            return response.text or None

    def put_resource(self, resource_id, put_body, api_version=DEFAULT_API_VERSION, **kwargs) -> object:
        """
        Put (create or update) an ARM resource.

        Args:
            resource_id (str): The ARM resource ID.
            put_body (dict): The body to send for the resource.
            api_version (str): The API version to use.
            **kwargs: Additional arguments for the request.

        Returns:
            object: The resource as a dict if JSON, or text/None otherwise.
        """
        self._refresh_api_key_if_needed()
        url = f"{self.base_url}{resource_id}?api-version={api_version}"
        headers = kwargs.pop('headers', {})
        headers['Content-Type'] = 'application/json'
        response = self.put(url, json=put_body, headers=headers, **kwargs)
        try:
            return response.json()
        except JSONDecodeError:
            return response.text or None

    def delete_resource(self, resource_id, api_version=DEFAULT_API_VERSION, **kwargs) -> object:
        """
        Delete an ARM resource by its resource ID.

        Args:
            resource_id (str): The ARM resource ID.
            api_version (str): The API version to use.
            **kwargs: Additional arguments for the request.

        Returns:
            object: The resource as a dict if JSON, or text/None otherwise.
        """
        self._refresh_api_key_if_needed()
        url = f"{self.base_url}{resource_id}?api-version={api_version}"
        response = self.delete(url, **kwargs)
        try:
            return response.json()
        except JSONDecodeError:
            return response.text or None
