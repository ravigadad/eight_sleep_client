"""Tests for Session."""

import httpx
from mockito import mock, when, verify, patch

import eight_sleep_client.client as client_module
from eight_sleep_client.session import Session
from eight_sleep_client.client import Client
from eight_sleep_client.api.constants import DEFAULT_CLIENT_API_URL
from eight_sleep_client.models.user_info import UserInfo
import eight_sleep_client.session as session_module
from eight_sleep_client.repositories.alarm_repository import AlarmRepository

USERS_ME_URL = f"{DEFAULT_CLIENT_API_URL}/users/me"


# --- create ---


async def test_create_delegates_to_client_and_user_info():
    mock_client = mock(Client)
    user_data = {"userId": "user-123", "devices": ["device-abc"]}

    when(mock_client).authenticate().thenReturn(None)
    when(mock_client).request("GET", USERS_ME_URL).thenReturn({"user": user_data})
    when(UserInfo).from_dict(user_data).thenReturn("user_info")
    patch(client_module, "Client", lambda *args, **kwargs: mock_client)

    async with httpx.AsyncClient() as http:
        session = await Session.create(http, email="user@example.com", password="pass123")

    assert isinstance(session, Session)
    verify(mock_client).request("GET", USERS_ME_URL)
    verify(UserInfo).from_dict(user_data)


# --- properties ---


def test_session_exposes_user_id():
    user_info = mock({"user_id": "user-abc"}, spec=UserInfo)
    session = Session(client=mock(Client), user_info=user_info)
    assert session.user_id == "user-abc"


def test_session_exposes_device_ids():
    user_info = mock({"device_ids": ["dev1", "dev2"]}, spec=UserInfo)
    session = Session(client=mock(Client), user_info=user_info)
    assert session.device_ids == ["dev1", "dev2"]


# --- get ---


async def test_get_interpolates_user_id_and_delegates_to_client():
    mock_client = mock(Client)
    user_info = mock({"user_id": "user-123"}, spec=UserInfo)
    when(mock_client).get("app", "/v2/users/user-123/alarms").thenReturn("get_response")

    session = Session(client=mock_client, user_info=user_info)
    result = await session.get("app", "/v2/users/{user_id}/alarms")

    assert result == "get_response"


# --- alarms ---


def test_alarms_passes_session_to_repository():
    session = Session(client=mock(Client), user_info=mock({"user_id": "u"}, spec=UserInfo))
    patch(session_module, "AlarmRepository", lambda s: f"repo_for_{id(s)}")

    assert session.alarms == f"repo_for_{id(session)}"
