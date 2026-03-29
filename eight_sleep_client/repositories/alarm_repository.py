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
        return [Alarm.from_dict(data, repository=self) for data in response["alarms"]]

    async def create(self, data: dict) -> Alarm:
        """Create a new alarm."""
        response = await self._session.post("app", "/v1/users/{user_id}/alarms", json=data)
        return Alarm.from_dict(response["alarm"], repository=self)

    async def snooze(self, alarm_id: str, minutes: int) -> None:
        """Snooze a ringing alarm."""
        await self._session.put(
            "app", f"/v1/users/{{user_id}}/alarms/{alarm_id}/snooze",
            json={"snoozeMinutes": minutes, "ignoreDeviceErrors": False},
        )

    async def dismiss(self, alarm_id: str) -> None:
        """Dismiss or stop an alarm."""
        await self._session.put(
            "app", f"/v1/users/{{user_id}}/alarms/{alarm_id}/dismiss",
            json={"ignoreDeviceErrors": False},
        )

    async def delete(self, alarm_id: str) -> None:
        """Delete an alarm."""
        await self._session.delete("app", f"/v1/users/{{user_id}}/alarms/{alarm_id}")

    async def update(self, alarm_id: str, data: dict) -> dict:
        """PUT the full writable payload for an alarm."""
        response = await self._session.put("app", f"/v1/users/{{user_id}}/alarms/{alarm_id}", json=data)
        return response["alarm"]
