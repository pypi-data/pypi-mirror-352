from typing import Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time

from sai_rl.sai_console import SAIConsole
from sai_rl.error import AuthenticationError, NetworkError
from sai_rl.api.requestor_options import RequestorOptions


class APIRequestor:
    def __init__(
        self,
        console: SAIConsole,
        options: RequestorOptions,
    ):
        self._console = console
        self._options = options
        self._session = self._create_session_with_retries()

    def _create_session_with_retries(self):
        session = requests.Session()
        retries = Retry(
            total=self._options.max_network_retries,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def _add_headers(self, headers: Optional[dict] = None) -> dict:
        headers = headers or {}
        headers["X-API-Key"] = f"{self._options.api_key}"
        return headers

    def _log_request(self, method: str, endpoint: str, start_time: float):
        elapsed_time = time.time() - start_time
        self._console.debug(
            f"{method.upper()}: Finished request to {endpoint} completed in {elapsed_time:.4f} seconds"
        )

    def _handle_request_error(
        self, err: requests.exceptions.RequestException, url: str
    ):
        if isinstance(err, requests.exceptions.HTTPError):
            if err.response.status_code == 401:
                raise AuthenticationError("Invalid API key. Please check your API key.")
            elif err.response.status_code == 403:
                raise AuthenticationError(
                    "You do not have permission to access this resource."
                )
            elif err.response.status_code == 404:
                raise NetworkError(f"Resource not found at {url}")
            elif err.response.status_code >= 500:
                raise NetworkError(f"Server error occurred: {err}")
            else:
                raise NetworkError(f"HTTP error occurred: {err}")
        elif isinstance(err, requests.exceptions.ConnectionError):
            raise NetworkError(f"Failed to connect to server: {err}")
        elif isinstance(err, requests.exceptions.Timeout):
            raise NetworkError(f"Request timed out: {err}")
        else:
            raise NetworkError(f"Request error occurred: {err}")

    def get(self, endpoint: str, headers=None, **kwargs):
        url = f"{self._options.api_base}{endpoint}"
        headers = self._add_headers(headers)
        self._console.debug(f"GET: Started request to {endpoint}")
        start_time = time.time()

        try:
            response = self._session.get(url, headers=headers, **kwargs)
            response.raise_for_status()
            self._log_request("GET", endpoint, start_time)
            return response
        except requests.exceptions.RequestException as err:
            self._handle_request_error(err, url)

    def post(self, endpoint: str, data=None, json=None, headers=None, **kwargs):
        url = f"{self._options.api_base}{endpoint}"
        headers = self._add_headers(headers)
        self._console.debug(f"POST: Started request to {endpoint}")

        start_time = time.time()
        try:
            response = self._session.post(
                url, data=data, json=json, headers=headers, **kwargs
            )
            response.raise_for_status()
            self._log_request("POST", endpoint, start_time)
            return response
        except requests.exceptions.RequestException as err:
            self._handle_request_error(err, url)

    def put(self, endpoint: str, data=None, json=None, headers=None, **kwargs):
        url = f"{self._options.api_base}{endpoint}"
        headers = self._add_headers(headers)
        self._console.debug(f"PUT: Started request to {endpoint}")

        start_time = time.time()
        try:
            response = self._session.put(
                url, data=data, json=json, headers=headers, **kwargs
            )
            response.raise_for_status()
            self._log_request("PUT", endpoint, start_time)
            return response
        except requests.exceptions.RequestException as err:
            self._handle_request_error(err, url)

    def delete(self, endpoint: str, headers=None, **kwargs):
        url = f"{self._options.api_base}{endpoint}"
        headers = self._add_headers(headers)
        self._console.debug(f"DELETE: Started request to {endpoint}")

        start_time = time.time()
        try:
            response = self._session.delete(url, headers=headers, **kwargs)
            response.raise_for_status()
            self._log_request("DELETE", endpoint, start_time)
            return response
        except requests.exceptions.RequestException as err:
            self._handle_request_error(err, url)
