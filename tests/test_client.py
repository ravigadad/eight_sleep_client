"""Tests for Client."""

from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest
import respx

from eight_sleep_client.client import Client
from eight_sleep_client.api.authenticator import Authenticator
from eight_sleep_client.api.constants import DEFAULT_CLIENT_API_URL
from eight_sleep_client.api.exceptions import AuthenticationError, RequestError
from eight_sleep_client.models.token import Token


# --- request ---


async def test_request_not_authenticated():
    async with httpx.AsyncClient() as http:
        with patch("eight_sleep_client.client.Authenticator", return_value=_make_mock_authenticator()):
            client = Client(http, email="user@example.com", password="pass123")
            with pytest.raises(AuthenticationError):
                await client.request("GET", f"{DEFAULT_CLIENT_API_URL}/some/endpoint")


@respx.mock
async def test_request_sends_bearer_header():
    route = respx.get(f"{DEFAULT_CLIENT_API_URL}/some/endpoint").mock(
        return_value=httpx.Response(200, json={"ok": True})
    )

    async with httpx.AsyncClient() as http:
        with patch("eight_sleep_client.client.Authenticator", return_value=_make_mock_authenticator()):
            client = Client(http, email="user@example.com", password="pass123")
            await client.authenticate()
            await client.request("GET", f"{DEFAULT_CLIENT_API_URL}/some/endpoint")

    auth_header = route.calls.last.request.headers["authorization"]
    assert auth_header == "Bearer test-access-token"


@respx.mock
async def test_request_401_triggers_refresh_and_retry():
    route = respx.get(f"{DEFAULT_CLIENT_API_URL}/some/endpoint").mock(
        side_effect=[
            httpx.Response(401, json={"error": "unauthorized"}),
            httpx.Response(200, json={"ok": True}),
        ]
    )

    async with httpx.AsyncClient() as http:
        with patch("eight_sleep_client.client.Authenticator", return_value=_make_mock_authenticator()):
            client = Client(http, email="user@example.com", password="pass123")
            await client.authenticate()
            result = await client.request("GET", f"{DEFAULT_CLIENT_API_URL}/some/endpoint")

    assert result == {"ok": True}
    assert route.call_count == 2


@respx.mock
async def test_request_401_retry_still_fails():
    respx.get(f"{DEFAULT_CLIENT_API_URL}/some/endpoint").mock(
        return_value=httpx.Response(401, json={"error": "unauthorized"})
    )

    async with httpx.AsyncClient() as http:
        with patch("eight_sleep_client.client.Authenticator", return_value=_make_mock_authenticator()):
            client = Client(http, email="user@example.com", password="pass123")
            await client.authenticate()
            with pytest.raises(AuthenticationError):
                await client.request("GET", f"{DEFAULT_CLIENT_API_URL}/some/endpoint")


@respx.mock
async def test_request_server_error():
    respx.get(f"{DEFAULT_CLIENT_API_URL}/some/endpoint").mock(
        return_value=httpx.Response(500, json={"error": "internal"})
    )

    async with httpx.AsyncClient() as http:
        with patch("eight_sleep_client.client.Authenticator", return_value=_make_mock_authenticator()):
            client = Client(http, email="user@example.com", password="pass123")
            await client.authenticate()
            with pytest.raises(RequestError):
                await client.request("GET", f"{DEFAULT_CLIENT_API_URL}/some/endpoint")


# --- helpers ---


def _make_mock_authenticator() -> Mock:
    mock_token = Mock(spec=Token, access_token="test-access-token")
    mock_authenticator = Mock(spec=Authenticator)
    mock_authenticator.authenticate = AsyncMock(return_value=mock_token)
    mock_authenticator.ensure_valid_token = AsyncMock(return_value=mock_token)
    return mock_authenticator
