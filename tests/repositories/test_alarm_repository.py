"""Tests for AlarmRepository."""

from mockito import mock, when, verify, expect

from eight_sleep_client.models.alarm import Alarm
from eight_sleep_client.repositories.alarm_repository import AlarmRepository
from eight_sleep_client.session import Session


# --- all ---


async def test_all_constructs_alarms_from_response():
    session = mock(Session)
    when(session).get("app", "/v2/users/{user_id}/alarms").thenReturn({
        "alarms": [{"id": "a1"}, {"id": "a2"}],
    })
    repository = AlarmRepository(session)

    when(Alarm).from_dict({"id": "a1"}, repository=repository).thenReturn("alarm_1")
    when(Alarm).from_dict({"id": "a2"}, repository=repository).thenReturn("alarm_2")

    assert await repository.all() == ["alarm_1", "alarm_2"]


async def test_all_returns_empty_list_when_no_alarms():
    session = mock(Session)
    when(session).get("app", "/v2/users/{user_id}/alarms").thenReturn({"alarms": []})

    repository = AlarmRepository(session)
    assert await repository.all() == []


# --- update ---


async def test_create_posts_data_and_returns_alarm():
    session = mock(Session)
    data = {"time": "08:00:00", "enabled": True}
    when(session).post("app", "/v1/users/{user_id}/alarms", json=data).thenReturn({
        "alarm": {"id": "new-1", "time": "08:00:00"},
    })

    repository = AlarmRepository(session)
    when(Alarm).from_dict({"id": "new-1", "time": "08:00:00"}, repository=repository).thenReturn("new_alarm")

    result = await repository.create(data)

    assert result == "new_alarm"


async def test_delete_sends_delete_to_alarm_endpoint():
    session = mock(Session)
    when(session).delete("app", "/v1/users/{user_id}/alarms/alarm-1").thenReturn(None)

    repository = AlarmRepository(session)
    await repository.delete("alarm-1")

    verify(session).delete("app", "/v1/users/{user_id}/alarms/alarm-1")


# --- snooze ---


async def test_snooze_puts_to_snooze_endpoint():
    session = mock(Session)
    repository = AlarmRepository(session)

    expect(session, times=1).put(
        "app", "/v1/users/{user_id}/alarms/alarm-1/snooze",
        json={"snoozeMinutes": 5, "ignoreDeviceErrors": False},
    ).thenReturn(None)

    await repository.snooze("alarm-1", 5)


# --- dismiss ---


async def test_dismiss_puts_to_dismiss_endpoint():
    session = mock(Session)
    repository = AlarmRepository(session)

    expect(session, times=1).put(
        "app", "/v1/users/{user_id}/alarms/alarm-1/dismiss",
        json={"ignoreDeviceErrors": False},
    ).thenReturn(None)

    await repository.dismiss("alarm-1")


# --- update ---


async def test_update_puts_data_and_returns_alarm_dict():
    session = mock(Session)
    data = {"id": "alarm-1", "enabled": True}
    alarm_dict = {"id": "alarm-1", "enabled": True, "nextTimestamp": "2026-04-01T14:30:00Z"}
    when(session).put("app", "/v1/users/{user_id}/alarms/alarm-1", json=data).thenReturn({
        "alarm": alarm_dict,
        "alarms": [],
    })

    repository = AlarmRepository(session)
    assert await repository.update("alarm-1", data) == alarm_dict
