"""Tests for Client."""

import httpx
import pytest
from mockito import mock, when, expect, any as any_arg

from tests.helpers import mock_response
from eight_sleep_client.client import Client
from eight_sleep_client.api.authenticator import Authenticator
from eight_sleep_client.api.constants import DEFAULT_APP_API_URL, DEFAULT_CLIENT_API_URL
from eight_sleep_client.api.exceptions import AuthenticationError, RequestError
from eight_sleep_client.models.token import Token

ENDPOINT = f"{DEFAULT_CLIENT_API_URL}/some/endpoint"


# --- authenticate ---


async def test_authenticate_delegates_to_authenticator():
    mock_authenticator = mock(Authenticator)
    expect(mock_authenticator, times=1).authenticate().thenReturn(None)

    client = Client("http", email="user@example.com", password="pass123")
    client._authenticator = mock_authenticator
    await client.authenticate()

    assert client._authenticated is True


# --- request ---


async def test_request_not_authenticated():
    client = Client("http", email="user@example.com", password="pass123")

    with pytest.raises(AuthenticationError):
        await client.request("GET", ENDPOINT)


async def test_request_sends_bearer_header():
    mock_http = mock(httpx.AsyncClient)
    client = _authenticated_client(mock_http)

    expect(mock_http, times=1).request(
        "GET", ENDPOINT, headers={"Authorization": "Bearer test-access-token"}
    ).thenReturn(mock_response(200, {"ok": True}))

    await client.request("GET", ENDPOINT)


async def test_request_401_triggers_refresh_and_retry():
    mock_http = mock(httpx.AsyncClient)
    client = _authenticated_client(mock_http)
    when(mock_http).request("GET", ENDPOINT, headers=any_arg()).thenReturn(
        mock_response(401, {"error": "unauthorized"})
    ).thenReturn(
        mock_response(200, {"ok": True})
    )

    result = await client.request("GET", ENDPOINT)

    assert result == {"ok": True}


async def test_request_401_retry_still_fails():
    mock_http = mock(httpx.AsyncClient)
    client = _authenticated_client(mock_http)
    when(mock_http).request("GET", ENDPOINT, headers=any_arg()).thenReturn(
        mock_response(401, {"error": "unauthorized"})
    ).thenReturn(
        mock_response(401, {"error": "unauthorized"})
    )

    with pytest.raises(AuthenticationError):
        await client.request("GET", ENDPOINT)


async def test_request_server_error():
    mock_http = mock(httpx.AsyncClient)
    client = _authenticated_client(mock_http)
    when(mock_http).request("GET", ENDPOINT, headers=any_arg()).thenReturn(
        mock_response(500, {"error": "internal"})
    )

    with pytest.raises(RequestError):
        await client.request("GET", ENDPOINT)


async def test_request_returns_none_for_empty_body():
    mock_http = mock(httpx.AsyncClient)
    client = _authenticated_client(mock_http)
    response = mock({"status_code": 200, "content": b""}, spec=httpx.Response)
    when(mock_http).request("PUT", ENDPOINT, headers=any_arg()).thenReturn(response)

    result = await client.request("PUT", ENDPOINT)

    assert result is None


# --- HTTP method helpers ---


@pytest.mark.parametrize("method,kwargs", [
    ("get", {}),
    ("post", {"json": {"time": "08:00:00"}}),
    ("put", {"json": {"skipNext": True}}),
    ("delete", {}),
])
async def test_http_methods_prepend_base_url_and_delegate(method, kwargs):
    mock_http = mock(httpx.AsyncClient)
    client = _authenticated_client(mock_http)
    when(mock_http).request(
        method.upper(), f"{DEFAULT_APP_API_URL}/v1/some/path", headers=any_arg(), **kwargs
    ).thenReturn(mock_response(200, "response"))

    result = await getattr(client, method)("app", "/v1/some/path", **kwargs)

    assert result == "response"


# --- helpers ---


def _authenticated_client(mock_http: httpx.AsyncClient) -> Client:
    mock_token = mock({"access_token": "test-access-token"}, spec=Token)
    mock_authenticator = mock(Authenticator)
    when(mock_authenticator).authenticate().thenReturn(mock_token)
    when(mock_authenticator).ensure_valid_token().thenReturn(mock_token)

    client = Client(mock_http, email="user@example.com", password="pass123")
    client._authenticator = mock_authenticator
    client._authenticated = True
    return client
