"""Authentication token from the Eight Sleep API."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from ..api.constants import TOKEN_EXPIRY_BUFFER_SECONDS


@dataclass(frozen=True)
class Token:
    """An authentication token returned by the Eight Sleep API.

    Attributes:
        access_token: Bearer token for authenticating API requests.
        refresh_token: Token for obtaining a new access token (future use).
        expires_at: Unix timestamp when the access token expires.
        user_id: The authenticated user's ID.
    """

    access_token: str
    refresh_token: str
    expires_at: float
    user_id: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Token:
        """Create a Token from a dict."""
        return cls(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            expires_at=time.time() + data["expires_in"],
            user_id=data["userId"],
        )

    @property
    def is_expired(self) -> bool:
        """Return True if the token is expired or will expire within the buffer window."""
        return time.time() + TOKEN_EXPIRY_BUFFER_SECONDS >= self.expires_at
