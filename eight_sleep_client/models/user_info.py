"""User information from the Eight Sleep API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class UserInfo:
    """User profile information returned by the Eight Sleep API.

    Attributes:
        user_id: The user's unique ID.
        device_ids: List of device (Pod) IDs associated with the user.
        raw: The full API response dict, for accessing fields not yet modeled.
    """

    user_id: str
    device_ids: list[str]
    raw: dict[str, Any]

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> UserInfo:
        """Create a UserInfo from a /users/me API response's 'user' object."""
        return cls(
            user_id=data["userId"],
            device_ids=data.get("devices", []),
            raw=data,
        )
