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
    when(Alarm).from_dict({"id": "a1"}).thenReturn("alarm_1")
    when(Alarm).from_dict({"id": "a2"}).thenReturn("alarm_2")

    repository = AlarmRepository(session)
    assert await repository.all() == ["alarm_1", "alarm_2"]


async def test_all_returns_empty_list_when_no_alarms():
    session = mock(Session)
    when(session).get("app", "/v2/users/{user_id}/alarms").thenReturn({"alarms": []})

    repository = AlarmRepository(session)
    assert await repository.all() == []
