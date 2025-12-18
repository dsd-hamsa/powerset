"""
PowerTrack API Client Module
===========================

Unified API client for all PowerTrack API interactions.
Handles authentication, retries, error handling, and request formatting.

Usage:
    from powertrack.api import make_request

    # GET request
    data = make_request('/api/sitehardware/S60308')

    # POST request
    result = make_request('/api/modeling', method='PUT', payload=model_data)
"""

import time
import requests
from typing import Dict, Any, Optional, Union
from urllib.parse import urljoin

try:
    # Try relative imports (when used as package)
    from .auth import load_env, update_auth_from_fetch, get_auth_headers, validate_auth
    from .pt_logging import get_logger
except ImportError:
    # Fall back to absolute imports (when run directly)
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from auth import load_env, update_auth_from_fetch, get_auth_headers, validate_auth
    from pt_logging import get_logger


class PowerSetAPIError(Exception):
    """Custom exception for PowerSet API errors."""
    pass


class APIClient:
    """Unified API client for PowerTrack operations."""

    def __init__(self, auth_vars: Optional[Dict[str, Any]] = None, max_retries: int = 5):
        """
        Initialize API client.

        Args:
            auth_vars: Pre-loaded auth variables (optional, will load if not provided)
            max_retries: Maximum number of auth retries before prompting user
        """
        self.logger = get_logger('api_client')
        self.max_retries = max_retries
        self.session = requests.Session()

        # Load or use provided auth
        self.auth_vars = auth_vars or load_env()

        if not validate_auth(self.auth_vars):
            raise PowerSetAPIError("Invalid authentication configuration")

        # Pre-emptive auth refresh
        self._refresh_auth_if_needed()

    def _refresh_auth_if_needed(self) -> None:
        """Check for fresh fetch file and update auth before making requests."""
        update_auth_from_fetch()
        self.auth_vars = load_env()  # Reload after potential update

    def _handle_auth_failure(self, attempt: int) -> bool:
        """
        Handle authentication failure with retry logic.

        Args:
            attempt: Current attempt number

        Returns:
            True if should retry, False if should stop
        """
        if attempt >= self.max_retries:
            self.logger.error(f"Authentication failed after {self.max_retries} attempts")
            print("❌ Authentication failed repeatedly. Please:")
            print("1. Open PowerTrack in Chrome and log in")
            print("2. Press F12 → Network tab → Copy any API request as fetch (Node.js)")
            print("3. Paste into auth/mostRecentFetch.js")
            print("4. Re-run the script")
            return False

        self.logger.warning(f"Auth attempt {attempt} failed, retrying with fresh auth...")
        time.sleep(2 ** attempt)  # Exponential backoff

        # Try refreshing auth
        self._refresh_auth_if_needed()

        return True

    def make_request(
        self,
        endpoint: str,
        method: str = 'GET',
        payload: Optional[Dict[str, Any]] = None,
        referer: Optional[str] = None,
        timeout: int = 30
    ) -> Union[Dict[str, Any], str, None]:
        """
        Make an authenticated API request to PowerTrack.

        Args:
            endpoint: API endpoint (e.g., '/api/sitehardware/S60308')
            method: HTTP method (GET, POST, PUT, DELETE)
            payload: Request payload for POST/PUT (dict or JSON string)
            referer: Custom referer URL (optional)
            timeout: Request timeout in seconds

        Returns:
            Parsed JSON response, or raw text if not JSON

        Raises:
            PowerSetAPIError: For API errors or auth failures
        """
        url = urljoin(self.auth_vars['base_url'], endpoint)
        headers = get_auth_headers(self.auth_vars, referer)

        # Add content-type for POST/PUT
        if method in ['POST', 'PUT'] and payload:
            headers['content-type'] = 'application/json'
            if isinstance(payload, dict):
                import json
                payload = json.dumps(payload)

        attempt = 0
        while attempt < self.max_retries:
            attempt += 1

            try:
                self.logger.debug(f"Making {method} request to {endpoint}")

                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    data=payload,
                    timeout=timeout
                )

                # Handle different response codes
                if response.status_code == 200:
                    try:
                        return response.json()
                    except ValueError:
                        return response.text

                elif response.status_code == 401:
                    self.logger.warning("401 Unauthorized - attempting auth refresh")
                    if not self._handle_auth_failure(attempt):
                        raise PowerSetAPIError("Authentication failed - please update mostRecentFetch.js")

                elif response.status_code == 403:
                    raise PowerSetAPIError(f"403 Forbidden - check permissions for endpoint: {endpoint}")

                elif response.status_code == 404:
                    raise PowerSetAPIError(f"404 Not Found - endpoint may not exist: {endpoint}")

                elif response.status_code >= 500:
                    self.logger.warning(f"Server error {response.status_code}, retrying...")
                    time.sleep(1)
                    continue

                else:
                    raise PowerSetAPIError(f"API error {response.status_code}: {response.text}")

            except requests.RequestException as e:
                self.logger.error(f"Request failed: {e}")
                if attempt >= self.max_retries:
                    raise PowerSetAPIError(f"Request failed after {self.max_retries} attempts: {e}")
                time.sleep(1)

        raise PowerSetAPIError("Max retries exceeded")


# Convenience function for simple usage
def make_request(
    endpoint: str,
    method: str = 'GET',
    payload: Optional[Dict[str, Any]] = None,
    referer: Optional[str] = None,
    timeout: int = 30
) -> Union[Dict[str, Any], str, None]:
    """
    Convenience function for single API requests.

    Creates a new APIClient instance for each call. For multiple requests,
    create an APIClient instance and reuse it.
    """
    client = APIClient()
    return client.make_request(endpoint, method, payload, referer, timeout)