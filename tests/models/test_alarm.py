"""Tests for the Alarm model and settings classes."""

import pytest
from mockito import patch

import eight_sleep_client.models.alarm as alarm_module
from eight_sleep_client.models.alarm import (
    Alarm,
    AlarmAudioSettings,
    AlarmRepeatSettings,
    AlarmSmartSettings,
    AlarmThermalSettings,
    AlarmVibrationSettings,
)


# --- Alarm ---


def test_alarm_from_dict_exposes_fields():
    alarm = Alarm.from_dict({"id": "alarm-123", "time": "07:30:00", "enabled": True})

    assert alarm.id == "alarm-123"
    assert alarm.time == "07:30:00"
    assert alarm.enabled is True


@pytest.mark.parametrize("property_name,class_name", [
    ("vibration", "AlarmVibrationSettings"),
    ("thermal", "AlarmThermalSettings"),
    ("audio", "AlarmAudioSettings"),
    ("smart", "AlarmSmartSettings"),
    ("repeat", "AlarmRepeatSettings"),
])
def test_alarm_passes_data_to_settings(property_name, class_name):
    patch(alarm_module, class_name, lambda data: data)
    alarm = Alarm.from_dict({property_name: "the_value"})
    assert getattr(alarm, property_name) == "the_value"


# --- Settings classes ---


@pytest.mark.parametrize("cls,data,expectations", [
    (AlarmVibrationSettings, {"enabled": True, "powerLevel": 50, "pattern": "RISE"}, [
        ("enabled", True), ("power_level", 50), ("pattern", "RISE"),
    ]),
    (AlarmThermalSettings, {"enabled": True, "level": 4}, [
        ("enabled", True), ("level", 4),
    ]),
    (AlarmAudioSettings, {"enabled": False, "level": 30}, [
        ("enabled", False), ("level", 30),
    ]),
    (AlarmSmartSettings, {"lightSleepEnabled": True, "sleepCapEnabled": False, "sleepCapMinutes": 480}, [
        ("light_sleep_enabled", True), ("sleep_cap_enabled", False), ("sleep_cap_minutes", 480),
    ]),
])
def test_settings_expose_fields(cls, data, expectations):
    settings = cls(data)
    for attr, expected in expectations:
        assert getattr(settings, attr) == expected


def test_repeat_settings_exposes_days():
    settings = AlarmRepeatSettings({
        "enabled": True,
        "weekDays": {"monday": True, "tuesday": True, "wednesday": False},
    })

    assert settings.enabled is True
    assert settings.days == ["monday", "tuesday"]
