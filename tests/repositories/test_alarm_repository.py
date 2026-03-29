"""Tests for AlarmRepository."""

from mockito import mock, when

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


async def test_update_puts_data_to_alarm_endpoint():
    session = mock(Session)
    data = {"id": "alarm-1", "enabled": True}
    when(session).put("app", "/v1/users/{user_id}/alarms/alarm-1", json=data).thenReturn("response")

    repository = AlarmRepository(session)
    assert await repository.update("alarm-1", data) == "response"
