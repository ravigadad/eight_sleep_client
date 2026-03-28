"""Alarm model for the Eight Sleep API."""

from __future__ import annotations

from typing import Any


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
