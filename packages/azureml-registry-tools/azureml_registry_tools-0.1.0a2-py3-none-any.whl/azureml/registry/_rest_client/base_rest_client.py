# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import requests
import time
import logging


class BaseRestClient:
    """Base REST client for making HTTP requests with retry logic and optional API key authentication."""

    def __init__(self, base_url: str, api_key: str = None, max_retries: int = 5, backoff_factor: int = 1) -> None:
        """
        Initialize the BaseRestClient.

        Args:
            base_url (str): The base URL for the REST API.
            api_key (str): Bearer token for authentication.
            max_retries (int): Maximum number of retries for failed requests.
            backoff_factor (int): Backoff factor for retry delays.
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    def _request_with_retry(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Make an HTTP request with retry logic for 5xx and 429 errors.

        Args:
            method (str): HTTP method (GET, POST, etc.).
            url (str): Full URL for the request.
            **kwargs: Additional arguments for requests.Session.request.

        Returns:
            requests.Response: The HTTP response object.
        """
        retries = 0
        while True:
            logging.info(f"Attempt {retries + 1}: {method} {url}")
            response = self.session.request(method, url, **kwargs)
            if response.status_code < 500 and response.status_code != 429:
                logging.info(f"Success: {method} {url} (status {response.status_code})")
                response.raise_for_status()
                return response
            # Handle 429 (Too Many Requests)
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                if retry_after:
                    try:
                        sleep_time = int(retry_after)
                    except ValueError:
                        sleep_time = self.backoff_factor * (2 ** retries)
                else:
                    sleep_time = self.backoff_factor * (2 ** retries)
                logging.info(f"Received 429. Retrying after {sleep_time} seconds...")
            else:
                # For all other 4xx errors, raise with details
                error_msg = (
                    f"HTTP {response.status_code} error for {method} {url}: "
                    f"{response.text.strip()}"
                )
                logging.error(f"Error: {error_msg}")
                raise Exception(error_msg)
            retries += 1
            if retries > self.max_retries:
                logging.error(f"Max retries exceeded for {method} {url}")
                response.raise_for_status()
            logging.info(f"Sleeping for {sleep_time} seconds before retry...")
            time.sleep(sleep_time)

    def get(self, url: str, **kwargs) -> requests.Response:
        """
        Make a GET request with retry logic.

        Args:
            url (str): The URL to request.
            **kwargs: Additional arguments for requests.Session.request.

        Returns:
            requests.Response: The HTTP response object.
        """
        return self._request_with_retry('GET', url, **kwargs)

    def post(self, url: str, **kwargs) -> requests.Response:
        """
        Make a POST request with retry logic.

        Args:
            url (str): The URL to request.
            **kwargs: Additional arguments for requests.Session.request.

        Returns:
            requests.Response: The HTTP response object.
        """
        return self._request_with_retry('POST', url, **kwargs)

    def put(self, url: str, **kwargs) -> requests.Response:
        """
        Make a PUT request with retry logic.

        Args:
            url (str): The URL to request.
            **kwargs: Additional arguments for requests.Session.request.

        Returns:
            requests.Response: The HTTP response object.
        """
        return self._request_with_retry('PUT', url, **kwargs)

    def patch(self, url: str, **kwargs) -> requests.Response:
        """
        Make a PATCH request with retry logic.

        Args:
            url (str): The URL to request.
            **kwargs: Additional arguments for requests.Session.request.

        Returns:
            requests.Response: The HTTP response object.
        """
        return self._request_with_retry('PATCH', url, **kwargs)

    def delete(self, url: str, **kwargs) -> requests.Response:
        """
        Make a DELETE request with retry logic.

        Args:
            url (str): The URL to request.
            **kwargs: Additional arguments for requests.Session.request.

        Returns:
            requests.Response: The HTTP response object.
        """
        return self._request_with_retry('DELETE', url, **kwargs)
