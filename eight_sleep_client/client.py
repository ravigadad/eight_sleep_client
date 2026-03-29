"""Internal HTTP infrastructure for the Eight Sleep API."""

from __future__ import annotations

import httpx

from .api.authenticator import Authenticator
from .api.constants import DEFAULT_APP_API_URL, DEFAULT_CLIENT_API_URL
from .api.exceptions import AuthenticationError, RequestError

BASE_URLS = {
    "app": DEFAULT_APP_API_URL,
    "client": DEFAULT_CLIENT_API_URL,
}


class Client:
    """Authenticated HTTP client for the Eight Sleep API.

    This is an internal class — callers should use Session.create().
    """

    def __init__(self, http: httpx.AsyncClient, email: str, password: str) -> None:
        self._http = http
        self._authenticator = Authenticator(http, email=email, password=password)
        self._authenticated = False

    async def authenticate(self) -> None:
        """Authenticate with the API."""
        await self._authenticator.authenticate()
        self._authenticated = True

    async def request(self, method: str, url: str, **kwargs: object) -> dict:
        """Make an authenticated API request with automatic 401 retry."""
        if not self._authenticated:
            raise AuthenticationError("Not authenticated — call authenticate() first")

        token = await self._authenticator.ensure_valid_token()
        headers = {"Authorization": f"Bearer {token.access_token}"}

        response = await self._http.request(method, url, headers=headers, **kwargs)

        if response.status_code == 401:
            token = await self._authenticator.authenticate()
            headers = {"Authorization": f"Bearer {token.access_token}"}
            response = await self._http.request(method, url, headers=headers, **kwargs)

            if response.status_code == 401:
                raise AuthenticationError("Re-authentication failed")

        if response.status_code >= 500:
            raise RequestError(f"Server error: {response.status_code}")

        return response.json()

    async def api_request(self, method: str, api: str, path: str, **kwargs: object) -> dict:
        """Make an authenticated request to the given API and path."""
        url = f"{BASE_URLS[api]}{path}"
        return await self.request(method, url, **kwargs)

    async def get(self, api: str, path: str) -> dict:
        return await self.api_request("GET", api, path)

    async def put(self, api: str, path: str, **kwargs: object) -> dict:
        return await self.api_request("PUT", api, path, **kwargs)

    async def delete(self, api: str, path: str) -> dict:
        return await self.api_request("DELETE", api, path)
