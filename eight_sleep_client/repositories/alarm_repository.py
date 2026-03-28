"""Repository for Eight Sleep alarm operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models.alarm import Alarm

if TYPE_CHECKING:
    from ..session import Session


class AlarmRepository:
    """Knows how to talk to the alarm API endpoints."""

    def __init__(self, session: Session) -> None:
        self._session = session

    async def all(self) -> list[Alarm]:
        """Fetch all alarms for the current user."""
        response = await self._session.get("app", "/v2/users/{user_id}/alarms")
        return [Alarm.from_dict(data) for data in response["alarms"]]
