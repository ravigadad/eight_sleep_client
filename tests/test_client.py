"""Tests for Client."""

import httpx
import pytest
from mockito import mock, when, verify, patch, any as any_arg

from tests.helpers import mock_response
import eight_sleep_client.client as client_module
from eight_sleep_client.client import Client
from eight_sleep_client.api.authenticator import Authenticator
from eight_sleep_client.api.constants import DEFAULT_APP_API_URL, DEFAULT_CLIENT_API_URL
from eight_sleep_client.api.exceptions import AuthenticationError, RequestError
from eight_sleep_client.models.token import Token

ENDPOINT = f"{DEFAULT_CLIENT_API_URL}/some/endpoint"


# --- authenticate ---


async def test_authenticate_delegates_to_authenticator():
    mock_http = mock(httpx.AsyncClient)
    mock_authenticator = _stub_authenticator()

    client = Client(mock_http, email="user@example.com", password="pass123")
    await client.authenticate()

    verify(mock_authenticator).authenticate()


# --- request ---


async def test_request_not_authenticated():
    mock_http = mock(httpx.AsyncClient)
    _stub_authenticator()

    client = Client(mock_http, email="user@example.com", password="pass123")
    with pytest.raises(AuthenticationError):
        await client.request("GET", ENDPOINT)


async def test_request_sends_bearer_header():
    mock_http = mock(httpx.AsyncClient)
    _stub_authenticator()
    when(mock_http).request("GET", ENDPOINT, headers=any_arg()).thenReturn(
        mock_response(200, {"ok": True})
    )

    client = Client(mock_http, email="user@example.com", password="pass123")
    await client.authenticate()
    await client.request("GET", ENDPOINT)

    verify(mock_http).request("GET", ENDPOINT, headers={"Authorization": "Bearer test-access-token"})


async def test_request_401_triggers_refresh_and_retry():
    mock_http = mock(httpx.AsyncClient)
    mock_authenticator = _stub_authenticator()
    when(mock_http).request("GET", ENDPOINT, headers=any_arg()).thenReturn(
        mock_response(401, {"error": "unauthorized"})
    ).thenReturn(
        mock_response(200, {"ok": True})
    )

    client = Client(mock_http, email="user@example.com", password="pass123")
    await client.authenticate()
    result = await client.request("GET", ENDPOINT)

    assert result == {"ok": True}
    verify(mock_authenticator, times=2).authenticate()


async def test_request_401_retry_still_fails():
    mock_http = mock(httpx.AsyncClient)
    _stub_authenticator()
    when(mock_http).request("GET", ENDPOINT, headers=any_arg()).thenReturn(
        mock_response(401, {"error": "unauthorized"})
    ).thenReturn(
        mock_response(401, {"error": "unauthorized"})
    )

    client = Client(mock_http, email="user@example.com", password="pass123")
    await client.authenticate()
    with pytest.raises(AuthenticationError):
        await client.request("GET", ENDPOINT)


async def test_request_server_error():
    mock_http = mock(httpx.AsyncClient)
    _stub_authenticator()
    when(mock_http).request("GET", ENDPOINT, headers=any_arg()).thenReturn(
        mock_response(500, {"error": "internal"})
    )

    client = Client(mock_http, email="user@example.com", password="pass123")
    await client.authenticate()
    with pytest.raises(RequestError):
        await client.request("GET", ENDPOINT)


# --- get ---


async def test_get_prepends_base_url_and_delegates():
    mock_http = mock(httpx.AsyncClient)
    _stub_authenticator()
    sentinel = object()
    when(mock_http).request(
        "GET", f"{DEFAULT_APP_API_URL}/v2/users/user-123/alarms", headers=any_arg()
    ).thenReturn(mock_response(200, sentinel))

    client = Client(mock_http, email="user@example.com", password="pass123")
    await client.authenticate()
    result = await client.get("app", "/v2/users/user-123/alarms")

    assert result is sentinel


# --- helpers ---


def _stub_authenticator() -> Authenticator:
    mock_token = mock({"access_token": "test-access-token"}, spec=Token)
    mock_authenticator = mock(Authenticator)
    when(mock_authenticator).authenticate().thenReturn(mock_token)
    when(mock_authenticator).ensure_valid_token().thenReturn(mock_token)
    patch(client_module, "Authenticator", lambda *args, **kwargs: mock_authenticator)
    return mock_authenticator


