"""Tests for the Alarm model."""

from eight_sleep_client.models.alarm import Alarm


# --- properties ---


def test_from_dict_exposes_fields():
    alarm = Alarm.from_dict({"id": "alarm-123", "time": "07:30:00", "enabled": True})

    assert alarm.id == "alarm-123"
    assert alarm.time == "07:30:00"
    assert alarm.enabled is True
