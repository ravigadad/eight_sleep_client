"""Alarm model and settings classes for the Eight Sleep API."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .settings import Settings, settings_property


class Alarm:
    """An alarm on the Eight Sleep Pod."""

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    def _datetime(self, key: str) -> datetime | None:
        value = self._data.get(key)
        return datetime.fromisoformat(value) if value else None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Alarm:
        """Create an Alarm from a dict."""
        return cls(data)

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
