"""Tests for the Alarm model and settings classes."""

from datetime import datetime, timezone

import pytest
from mockito import mock, when, expect, patch

import eight_sleep_client.models.alarm as alarm_module
from eight_sleep_client.repositories.alarm_repository import AlarmRepository
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
    alarm = Alarm.from_dict({
        "id": "alarm-123",
        "time": "07:30:00",
        "enabled": True,
        "nextTimestamp": "2026-03-30T14:30:00Z",
        "startTimestamp": "2026-03-30T14:30:00Z",
        "endTimestamp": "2026-03-30T14:50:00Z",
        "skipNext": False,
        "snoozing": True,
        "snoozedUntil": "2026-03-30T14:39:00Z",
        "skippedUntil": "1970-01-01T00:00:00Z",
        "dismissedUntil": "2026-03-27T21:39:30Z",
        "tags": ["routine-abc"],
    })

    assert alarm.id == "alarm-123"
    assert alarm.time == "07:30:00"
    assert alarm.enabled is True
    assert alarm.next_timestamp == datetime(2026, 3, 30, 14, 30, tzinfo=timezone.utc)
    assert alarm.start_timestamp == datetime(2026, 3, 30, 14, 30, tzinfo=timezone.utc)
    assert alarm.end_timestamp == datetime(2026, 3, 30, 14, 50, tzinfo=timezone.utc)
    assert alarm.skip_next is False
    assert alarm.snoozing is True
    assert alarm.snoozed_until == datetime(2026, 3, 30, 14, 39, tzinfo=timezone.utc)
    assert alarm.skipped_until == datetime(1970, 1, 1, tzinfo=timezone.utc)
    assert alarm.dismissed_until == datetime(2026, 3, 27, 21, 39, 30, tzinfo=timezone.utc)
    assert alarm.tags == ["routine-abc"]


async def test_save_sends_writable_data_and_refreshes():
    repository = mock(AlarmRepository)
    alarm = Alarm.from_dict({"id": "alarm-1"}, repository=repository)

    writable = {"id": "alarm-1", "stubbed": True}
    when(alarm).writable_data().thenReturn(writable)

    response_alarm = {"id": "alarm-1", "refreshed": True}
    when(repository).update("alarm-1", writable).thenReturn(response_alarm)

    await alarm.save()

    assert alarm._data is response_alarm


async def test_enable():
    alarm = Alarm.from_dict({})
    expect(alarm, times=1).update(enabled=True)
    await alarm.enable()


async def test_enable_false():
    alarm = Alarm.from_dict({})
    expect(alarm, times=1).update(enabled=False)
    await alarm.enable(False)


async def test_disable():
    alarm = Alarm.from_dict({})
    expect(alarm, times=1).enable(False)
    await alarm.disable()


async def test_skip():
    alarm = Alarm.from_dict({})
    expect(alarm, times=1).update(skipNext=True)
    await alarm.skip()


async def test_skip_false():
    alarm = Alarm.from_dict({})
    expect(alarm, times=1).update(skipNext=False)
    await alarm.skip(False)


async def test_unskip():
    alarm = Alarm.from_dict({})
    expect(alarm, times=1).skip(False)
    await alarm.unskip()

async def test_snooze():
    repository = mock(AlarmRepository)
    alarm = Alarm.from_dict({"id": "alarm-1"}, repository=repository)
    expect(repository, times=1).snooze("alarm-1", 5)
    await alarm.snooze(5)


async def test_snooze_defaults_to_9_minutes():
    repository = mock(AlarmRepository)
    alarm = Alarm.from_dict({"id": "alarm-1"}, repository=repository)
    expect(repository, times=1).snooze("alarm-1", 9)
    await alarm.snooze()


async def test_dismiss():
    repository = mock(AlarmRepository)
    alarm = Alarm.from_dict({"id": "alarm-1"}, repository=repository)
    expect(repository, times=1).dismiss("alarm-1")
    await alarm.dismiss()


async def test_delete_delegates_to_repository():
    from mockito import verify
    repository = mock(AlarmRepository)
    alarm = Alarm.from_dict({"id": "alarm-1"}, repository=repository)
    when(repository).delete("alarm-1").thenReturn(None)

    await alarm.delete()

    verify(repository).delete("alarm-1")


async def test_update_sets_fields_then_saves():
    alarm = Alarm.from_dict({"id": "alarm-1", "skipNext": False})
    saved_data = {}
    when(alarm).save().thenAnswer(lambda: saved_data.update(alarm._data))

    await alarm.update(skipNext=True)

    assert saved_data["skipNext"] is True


def test_writable_data_reads_from_live_data():
    alarm = Alarm.from_dict({})
    alarm._data = {
        "id": "alarm-1",
        "enabled": True,
        "skipNext": True,
        "nextTimestamp": "should-be-excluded",
    }

    assert alarm.writable_data() == {
        "id": "alarm-1",
        "enabled": True,
        "skipNext": True,
    }


def test_alarm_timestamps_none_when_disabled():
    alarm = Alarm.from_dict({
        "id": "alarm-123",
        "time": "08:30:00",
        "enabled": False,
    })

    assert alarm.next_timestamp is None
    assert alarm.start_timestamp is None
    assert alarm.end_timestamp is None


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
