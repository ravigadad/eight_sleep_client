"""Tests for the Authenticator."""

import httpx
import pytest
from mockito import mock, when, expect

from tests.helpers import mock_response
from eight_sleep_client.api.authenticator import Authenticator
from eight_sleep_client.api.constants import DEFAULT_AUTH_URL, DEFAULT_CLIENT_ID, DEFAULT_CLIENT_SECRET
from eight_sleep_client.api.exceptions import AuthenticationError, ConnectionError
from eight_sleep_client.models.token import Token


# --- authenticate ---


async def test_authenticate_returns_token_from_api_response():
    mock_http = mock(httpx.AsyncClient)
    mock_token = mock({"is_expired": False}, spec=Token)
    when(mock_http).post(DEFAULT_AUTH_URL, json=_expected_body()).thenReturn(
        mock_response(200, _auth_response())
    )
    when(Token).from_dict(_auth_response()).thenReturn(mock_token)

    auth = Authenticator(mock_http, email="user@example.com", password="pass123")
    assert await auth.authenticate() is mock_token


async def test_authenticate_invalid_credentials():
    mock_http = mock(httpx.AsyncClient)
    when(mock_http).post(DEFAULT_AUTH_URL, json=_expected_body("bad@example.com", "wrong")).thenReturn(
        mock_response(401, {"error": "invalid_grant"})
    )

    auth = Authenticator(mock_http, email="bad@example.com", password="wrong")
    with pytest.raises(AuthenticationError):
        await auth.authenticate()


async def test_authenticate_server_error():
    mock_http = mock(httpx.AsyncClient)
    when(mock_http).post(DEFAULT_AUTH_URL, json=_expected_body()).thenReturn(
        mock_response(500, {"error": "internal"})
    )

    auth = Authenticator(mock_http, email="user@example.com", password="pass123")
    with pytest.raises(AuthenticationError):
        await auth.authenticate()


async def test_authenticate_network_error():
    mock_http = mock(httpx.AsyncClient)
    when(mock_http).post(DEFAULT_AUTH_URL, json=_expected_body()).thenRaise(
        httpx.ConnectError("connection refused")
    )

    auth = Authenticator(mock_http, email="user@example.com", password="pass123")
    with pytest.raises(ConnectionError):
        await auth.authenticate()


# --- ensure_valid_token ---


async def test_ensure_valid_token_authenticates_when_no_token():
    mock_token = mock(Token)
    auth = Authenticator("http", email="x", password="y")
    expect(auth, times=1).authenticate().thenReturn(mock_token)

    assert await auth.ensure_valid_token() is mock_token


async def test_ensure_valid_token_returns_cached_when_fresh():
    fresh_token = mock({"is_expired": False}, spec=Token)
    auth = Authenticator("http", email="x", password="y")
    auth._token = fresh_token

    assert await auth.ensure_valid_token() is fresh_token


async def test_ensure_valid_token_refreshes_when_expired():
    expired_token = mock({"is_expired": True}, spec=Token)
    fresh_token = mock(Token)
    auth = Authenticator("http", email="x", password="y")
    auth._token = expired_token
    expect(auth, times=1).authenticate().thenReturn(fresh_token)

    assert await auth.ensure_valid_token() is fresh_token


# --- token property ---


async def test_token_is_none_before_authenticate():
    mock_http = mock(httpx.AsyncClient)
    auth = Authenticator(mock_http, email="user@example.com", password="pass123")
    assert auth.token is None


# --- helpers ---



def _expected_body(email: str = "user@example.com", password: str = "pass123") -> dict:
    return {
        "client_id": DEFAULT_CLIENT_ID,
        "client_secret": DEFAULT_CLIENT_SECRET,
        "grant_type": "password",
        "username": email,
        "password": password,
    }


def _auth_response() -> dict:
    return {
        "access_token": "test-access-token",
        "refresh_token": "test-refresh-token",
        "expires_in": 72000,
        "userId": "test-user-id",
    }
