"""Tests for Session."""

import pytest
from mockito import mock, when, expect, patch

import eight_sleep_client.client as client_module
import eight_sleep_client.session as session_module
from eight_sleep_client.session import Session
from eight_sleep_client.client import Client
from eight_sleep_client.api.constants import DEFAULT_CLIENT_API_URL
from eight_sleep_client.models.user_info import UserInfo
from eight_sleep_client.repositories.alarm_repository import AlarmRepository

USERS_ME_URL = f"{DEFAULT_CLIENT_API_URL}/users/me"


# --- create ---


async def test_create_authenticates_fetches_user_and_returns_session():
    mock_client = mock(Client)
    user_data = {"userId": "user-123", "devices": ["device-abc"]}

    client_factory = mock()
    when(client_factory).__call__("the_http", email="user@example.com", password="pass123").thenReturn(mock_client)
    expect(mock_client, times=1).authenticate()
    when(mock_client).request("GET", USERS_ME_URL).thenReturn({"user": user_data})
    when(UserInfo).from_dict(user_data).thenReturn("user_info")
    patch(client_module, "Client", client_factory)

    session = await Session.create("the_http", email="user@example.com", password="pass123")

    assert session._client is mock_client
    assert session._user_info == "user_info"


# --- properties ---


def test_session_exposes_user_id():
    user_info = mock({"user_id": "user-abc"}, spec=UserInfo)
    session = Session(client="a_client", user_info=user_info)
    assert session.user_id == "user-abc"


def test_session_exposes_device_ids():
    user_info = mock({"device_ids": ["dev1", "dev2"]}, spec=UserInfo)
    session = Session(client="a_client", user_info=user_info)
    assert session.device_ids == ["dev1", "dev2"]


# --- HTTP methods ---


@pytest.mark.parametrize("method", ["get", "post", "put", "delete"])
async def test_http_methods_interpolate_and_delegate(method):
    mock_client = mock(Client)
    user_info = mock({"user_id": "user-123"}, spec=UserInfo)
    getattr(when(mock_client), method)("app", "/v2/users/user-123/alarms").thenReturn("response")

    session = Session(client=mock_client, user_info=user_info)
    assert await getattr(session, method)("app", "/v2/users/{user_id}/alarms") == "response"


# --- alarms ---


def test_alarms_passes_session_to_repository():
    session = Session(client=mock(Client), user_info=mock({"user_id": "u"}, spec=UserInfo))
    patch(session_module, "AlarmRepository", lambda s: f"repo_for_{id(s)}")

    assert session.alarms == f"repo_for_{id(session)}"
