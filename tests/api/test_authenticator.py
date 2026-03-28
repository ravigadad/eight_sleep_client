"""Tests for the Authenticator."""

import json

import httpx
import pytest
import respx
import time_machine

from eight_sleep_client.api.authenticator import Authenticator
from eight_sleep_client.api.constants import DEFAULT_AUTH_URL, DEFAULT_CLIENT_ID, DEFAULT_CLIENT_SECRET
from eight_sleep_client.api.exceptions import AuthenticationError, ConnectionError
from eight_sleep_client.models.token import Token


# --- authenticate ---


@respx.mock
async def test_authenticate_sends_correct_body():
    route = respx.post(DEFAULT_AUTH_URL).mock(return_value=httpx.Response(200, json=_auth_response()))

    async with httpx.AsyncClient() as http:
        auth = Authenticator(http, email="user@example.com", password="pass123")
        await auth.authenticate()

    sent = json.loads(route.calls.last.request.content)
    assert sent == {
        "client_id": DEFAULT_CLIENT_ID,
        "client_secret": DEFAULT_CLIENT_SECRET,
        "grant_type": "password",
        "username": "user@example.com",
        "password": "pass123",
    }


@respx.mock
async def test_authenticate_returns_token():
    respx.post(DEFAULT_AUTH_URL).mock(return_value=httpx.Response(200, json=_auth_response()))

    async with httpx.AsyncClient() as http:
        auth = Authenticator(http, email="user@example.com", password="pass123")
        token = await auth.authenticate()

    assert isinstance(token, Token)


@respx.mock
async def test_authenticate_invalid_credentials():
    respx.post(DEFAULT_AUTH_URL).mock(return_value=httpx.Response(401, json={"error": "invalid_grant"}))

    async with httpx.AsyncClient() as http:
        auth = Authenticator(http, email="bad@example.com", password="wrong")
        with pytest.raises(AuthenticationError):
            await auth.authenticate()


@respx.mock
async def test_authenticate_server_error():
    respx.post(DEFAULT_AUTH_URL).mock(return_value=httpx.Response(500, json={"error": "internal"}))

    async with httpx.AsyncClient() as http:
        auth = Authenticator(http, email="user@example.com", password="pass123")
        with pytest.raises(AuthenticationError):
            await auth.authenticate()


@respx.mock
async def test_authenticate_network_error():
    respx.post(DEFAULT_AUTH_URL).mock(side_effect=httpx.ConnectError("connection refused"))

    async with httpx.AsyncClient() as http:
        auth = Authenticator(http, email="user@example.com", password="pass123")
        with pytest.raises(ConnectionError):
            await auth.authenticate()


# --- ensure_valid_token ---


@respx.mock
async def test_ensure_valid_token_authenticates_when_no_token():
    route = respx.post(DEFAULT_AUTH_URL).mock(return_value=httpx.Response(200, json=_auth_response()))

    async with httpx.AsyncClient() as http:
        auth = Authenticator(http, email="user@example.com", password="pass123")
        token = await auth.ensure_valid_token()

    assert isinstance(token, Token)
    assert route.call_count == 1


@respx.mock
async def test_ensure_valid_token_returns_cached_when_fresh():
    route = respx.post(DEFAULT_AUTH_URL).mock(return_value=httpx.Response(200, json=_auth_response()))

    async with httpx.AsyncClient() as http:
        auth = Authenticator(http, email="user@example.com", password="pass123")
        await auth.ensure_valid_token()
        await auth.ensure_valid_token()

    assert route.call_count == 1


@respx.mock
@time_machine.travel(1000000.0, tick=False)
async def test_ensure_valid_token_refreshes_when_expired(time_machine):
    route = respx.post(DEFAULT_AUTH_URL).mock(return_value=httpx.Response(200, json=_auth_response()))

    async with httpx.AsyncClient() as http:
        auth = Authenticator(http, email="user@example.com", password="pass123")
        await auth.ensure_valid_token()

        time_machine.move_to(1000000.0 + 72001)
        await auth.ensure_valid_token()

    assert route.call_count == 2


# --- token property ---


async def test_token_is_none_before_authenticate():
    async with httpx.AsyncClient() as http:
        auth = Authenticator(http, email="user@example.com", password="pass123")
        assert auth.token is None


# --- helpers ---


def _auth_response(**overrides) -> dict:
    defaults = {
        "access_token": "test-access-token",
        "refresh_token": "test-refresh-token",
        "expires_in": 72000,
        "userId": "test-user-id",
    }
    defaults.update(overrides)
    return defaults
