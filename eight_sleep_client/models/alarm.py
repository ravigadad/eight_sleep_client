"""Alarm model and settings classes for the Eight Sleep API."""

from __future__ import annotations

from typing import Any

from .settings import Settings, settings_property


class Alarm:
    """An alarm on the Eight Sleep Pod."""

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

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
