"""Token-based authentication for the Eight Sleep API."""

from __future__ import annotations

import httpx

from .constants import DEFAULT_AUTH_URL, DEFAULT_CLIENT_ID, DEFAULT_CLIENT_SECRET
from .exceptions import AuthenticationError, ConnectionError
from ..models.token import Token


class Authenticator:
    """Manages authentication and token lifecycle for the Eight Sleep API."""

    def __init__(
        self,
        http: httpx.AsyncClient,
        email: str,
        password: str,
        *,
        auth_url: str = DEFAULT_AUTH_URL,
        client_id: str = DEFAULT_CLIENT_ID,
        client_secret: str = DEFAULT_CLIENT_SECRET,
    ) -> None:
        self._http = http
        self._email = email
        self._password = password
        self._auth_url = auth_url
        self._client_id = client_id
        self._client_secret = client_secret
        self._token: Token | None = None

    async def authenticate(self) -> Token:
        """Authenticate with the Eight Sleep API and return a Token."""
        try:
            response = await self._http.post(
                self._auth_url,
                json={
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                    "grant_type": "password",
                    "username": self._email,
                    "password": self._password,
                },
            )
        except httpx.ConnectError as err:
            raise ConnectionError(str(err)) from err

        if response.status_code != 200:
            raise AuthenticationError(
                f"Authentication failed with status {response.status_code}"
            )

        self._token = Token.from_dict(response.json())
        return self._token

    async def ensure_valid_token(self) -> Token:
        """Return a valid token, re-authenticating if needed."""
        if self._token is None or self._token.is_expired:
            return await self.authenticate()
        return self._token

    @property
    def token(self) -> Token | None:
        """The current token, or None if not yet authenticated."""
        return self._token
