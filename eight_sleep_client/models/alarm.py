"""Alarm model and settings classes for the Eight Sleep API."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .settings import Settings, settings_property


class Alarm:
    """An alarm on the Eight Sleep Pod."""

    WRITABLE_FIELDS = frozenset({
        "id", "enabled", "time", "skipNext", "snoozing", "isSuggested",
        "repeat", "vibration", "thermal", "audio", "smart", "tags",
        "oneTimeOverride",
    })

    def __init__(self, data: dict[str, Any], repository: Any = None) -> None:
        self._data = data
        self._repository = repository

    @classmethod
    def from_dict(cls, data: dict[str, Any], repository: Any = None) -> Alarm:
        """Create an Alarm from a dict."""
        return cls(data, repository=repository)

    # --- mutations ---

    async def enable(self, enabled: bool = True) -> None:
        """Enable or disable the alarm."""
        await self.update(enabled=enabled)

    async def disable(self) -> None:
        """Disable the alarm."""
        await self.enable(False)

    async def skip(self, skip: bool = True) -> None:
        """Skip or unskip the next occurrence."""
        await self.update(skipNext=skip)

    async def unskip(self) -> None:
        """Unskip the next occurrence."""
        await self.skip(False)

    async def override_next(self, **overrides: Any) -> None:
        """Override the next occurrence with different settings.

        Only the fields you pass are changed; the rest are filled
        from the alarm's current settings.
        """
        override = {
            "time": overrides.get("time", self._data["time"]),
            "vibration": overrides.get("vibration", self._data["vibration"]),
            "thermal": overrides.get("thermal", self._data["thermal"]),
            "audio": overrides.get("audio", self._data["audio"]),
            "smart": overrides.get("smart", self._data["smart"]),
        }
        await self.update(oneTimeOverride=override)

    async def clear_override(self) -> None:
        """Remove a one-time override."""
        await self.update(oneTimeOverride=None)

    async def snooze(self, minutes: int = 9) -> None:
        """Snooze a ringing alarm."""
        await self._repository.snooze(self.id, minutes)

    async def dismiss(self) -> None:
        """Dismiss or stop a ringing alarm."""
        await self._repository.dismiss(self.id)

    async def delete(self) -> None:
        """Delete this alarm."""
        await self._repository.delete(self.id)

    async def update(self, **changes: Any) -> None:
        """Apply changes to the alarm data and persist."""
        self._data.update(changes)
        await self.save()

    async def save(self) -> None:
        """Persist the current writable state to the API."""
        self._data = await self._repository.update(self.id, self.writable_data())

    def writable_data(self) -> dict[str, Any]:
        """Return only the writable fields from the alarm data, stripping None values."""
        return {k: v for k, v in self._data.items() if k in self.WRITABLE_FIELDS and v is not None}

    # --- properties ---

    def _datetime(self, key: str) -> datetime | None:
        value = self._data.get(key)
        return datetime.fromisoformat(value) if value else None

    @property
    def id(self) -> str:
        return self._data["id"]

    @property
    def time(self) -> str:
        return self._data["time"]

    @property
    def enabled(self) -> bool:
        return self._data["enabled"]

    @property
    def next_timestamp(self) -> datetime | None:
        return self._datetime("nextTimestamp")

    @property
    def start_timestamp(self) -> datetime | None:
        return self._datetime("startTimestamp")

    @property
    def end_timestamp(self) -> datetime | None:
        return self._datetime("endTimestamp")

    @property
    def skip_next(self) -> bool:
        return self._data["skipNext"]

    @property
    def snoozing(self) -> bool:
        return self._data["snoozing"]

    @property
    def snoozed_until(self) -> datetime:
        return self._datetime("snoozedUntil")

    @property
    def skipped_until(self) -> datetime:
        return self._datetime("skippedUntil")

    @property
    def dismissed_until(self) -> datetime:
        return self._datetime("dismissedUntil")

    @property
    def tags(self) -> list[str]:
        return self._data["tags"]

    audio: AlarmAudioSettings = settings_property("AlarmAudioSettings")  # type: ignore[assignment]
    repeat: AlarmRepeatSettings = settings_property("AlarmRepeatSettings")  # type: ignore[assignment]
    smart: AlarmSmartSettings = settings_property("AlarmSmartSettings")  # type: ignore[assignment]
    thermal: AlarmThermalSettings = settings_property("AlarmThermalSettings")  # type: ignore[assignment]
    vibration: AlarmVibrationSettings = settings_property("AlarmVibrationSettings")  # type: ignore[assignment]


class AlarmAudioSettings(Settings):
    enabled: bool
    level: int


class AlarmRepeatSettings(Settings):
    enabled: bool

    @property
    def days(self) -> list[str]:
        return [day for day, active in self._data["weekDays"].items() if active]


class AlarmSmartSettings(Settings):
    light_sleep_enabled: bool
    sleep_cap_enabled: bool
    sleep_cap_minutes: int


class AlarmThermalSettings(Settings):
    enabled: bool
    level: int


class AlarmVibrationSettings(Settings):
    enabled: bool
    power_level: int
    pattern: str
