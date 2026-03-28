"""Tests for Session."""

from unittest.mock import AsyncMock, Mock, patch

import httpx

from eight_sleep_client.session import Session
from eight_sleep_client.client import Client
from eight_sleep_client.models.user_info import UserInfo


# --- create ---


async def test_create_returns_session():
    mock_client = Mock(spec=Client)
    mock_client.authenticate = AsyncMock()
    mock_client.request = AsyncMock(return_value=_users_me_response())

    with patch("eight_sleep_client.client.Client", return_value=mock_client):
        async with httpx.AsyncClient() as http:
            session = await Session.create(http, email="user@example.com", password="pass123")

    assert isinstance(session, Session)
    mock_client.authenticate.assert_awaited_once()


# --- properties ---


def test_session_exposes_user_id():
    user_info = Mock(spec=UserInfo, user_id="user-abc")
    session = Session(client=Mock(spec=Client), user_info=user_info)
    assert session.user_id == "user-abc"


def test_session_exposes_device_ids():
    user_info = Mock(spec=UserInfo, device_ids=["dev1", "dev2"])
    session = Session(client=Mock(spec=Client), user_info=user_info)
    assert session.device_ids == ["dev1", "dev2"]


# --- helpers ---


def _users_me_response(**overrides) -> dict:
    defaults = {
        "userId": "user-123",
        "devices": ["device-abc"],
    }
    defaults.update(overrides)
    return defaults
