"""Authenticated session for the Eight Sleep API."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from .api.constants import DEFAULT_CLIENT_API_URL
from .models.user_info import UserInfo

if TYPE_CHECKING:
    from .client import Client


class Session:
    """An authenticated context for the Eight Sleep API.

    Use the ``create`` classmethod to obtain a session — callers
    should never need to construct one directly.
    """

    def __init__(self, client: Client, user_info: UserInfo) -> None:
        self._client = client
        self._user_info = user_info

    @classmethod
    async def create(cls, http: httpx.AsyncClient, email: str, password: str) -> Session:
        """Authenticate, fetch user info, and return a ready-to-use session."""
        from .client import Client

        client = Client(http, email=email, password=password)
        await client.authenticate()

        response = await client.request("GET", f"{DEFAULT_CLIENT_API_URL}/users/me")
        user_info = UserInfo.from_dict(response["user"])

        return cls(client=client, user_info=user_info)

    @property
    def user_id(self) -> str:
        return self._user_info.user_id

    @property
    def device_ids(self) -> list[str]:
        return self._user_info.device_ids

    async def get(self, api: str, path: str) -> dict:
        """Interpolate user context into path and delegate to Client."""
        resolved = path.format_map({"user_id": self.user_id})
        return await self._client.get(api, resolved)
