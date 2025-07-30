# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azure.identity import DefaultAzureCredential
from .base_rest_client import BaseRestClient
import time


class RegistryManagementClient(BaseRestClient):
    """Python client for RegistrySyndicationManifestController (excluding S2S APIs).

    Handles authentication, token refresh, and provides methods for manifest and registry management.
    """

    def __init__(self, registry_name: str, primary_region: str = "eastus2euap", api_key: str = None, max_retries: int = 5, backoff_factor: int = 1) -> None:
        """
        Initialize the RegistryManagementClient.

        Args:
            primary_region (str): The Azure region for the registry.
            registry_name (str): The name of the AzureML registry.
            api_key (str, optional): Bearer token for authentication. If None, uses DefaultAzureCredential.
            max_retries (int): Maximum number of retries for failed requests.
            backoff_factor (int): Backoff factor for retry delays.
        """
        base_url = f"https://{primary_region}.api.azureml.ms"
        self._credential = None
        self._token_expires_on = None
        if api_key is None:
            # Use DefaultAzureCredential for authentication if no API key is provided
            self._credential = DefaultAzureCredential()
            token = self._credential.get_token("https://management.azure.com/.default")
            api_key = token.token
            self._token_expires_on = token.expires_on
        super().__init__(base_url, api_key=api_key, max_retries=max_retries, backoff_factor=backoff_factor)
        self.registry_name = registry_name

    def _refresh_api_key_if_needed(self) -> None:
        """Refresh the API key if using DefaultAzureCredential and the token is close to expiration."""
        # Only refresh if using DefaultAzureCredential
        if self._credential is not None:
            now = int(time.time())
            # Refresh if less than 10 minutes (600 seconds) left
            if not self._token_expires_on or self._token_expires_on - now < 600:
                token = self._credential.get_token("https://management.azure.com/.default")
                self.api_key = token.token
                self.session.headers.update({'Authorization': f'Bearer {self.api_key}'})
                self._token_expires_on = token.expires_on

    def create_or_update_manifest(self, manifest_dto: dict) -> dict:
        """
        Create or update the syndication manifest for the registry.

        Args:
            manifest_dto (dict): The manifest data transfer object.

        Returns:
            dict: The response from the service.
        """
        self._refresh_api_key_if_needed()
        url = f"{self.base_url}/registrymanagement/v1.0/registrySyndication/{self.registry_name}/createOrUpdateManifest"
        response = self.post(url, json=manifest_dto)
        return response.json()

    def resync_assets_in_manifest(self, resync_assets_dto: dict) -> dict:
        """
        Resynchronize assets in the syndication manifest.

        Args:
            resync_assets_dto (dict): The DTO specifying which assets to resync.

        Returns:
            dict: The response from the service.
        """
        self._refresh_api_key_if_needed()
        url = f"{self.base_url}/registrymanagement/v1.0/registrySyndication/{self.registry_name}/resyncAssetsInManifest"
        response = self.post(url, json=resync_assets_dto)
        return response.json()

    def delete_manifest(self) -> dict:
        """
        Delete the syndication manifest for the registry.

        Returns:
            dict: The response from the service.
        """
        self._refresh_api_key_if_needed()
        url = f"{self.base_url}/registrymanagement/v1.0/registrySyndication/{self.registry_name}/deleteManifest"
        response = self.post(url)
        return response.json()

    def get_manifest(self) -> dict:
        """
        Get the syndication manifest for the registry.

        Returns:
            dict: The manifest data.
        """
        self._refresh_api_key_if_needed()
        url = f"{self.base_url}/registrymanagement/v1.0/registrySyndication/{self.registry_name}/getManifest"
        response = self.get(url)
        return response.json()

    def discovery(self) -> dict:
        """
        Get discovery information for the registry.

        Returns:
            dict: The discovery information for the registry.
        """
        self._refresh_api_key_if_needed()
        url = f"{self.base_url}/registrymanagement/v1.0/registries/{self.registry_name}/discovery"
        response = self.get(url)
        return response.json()
