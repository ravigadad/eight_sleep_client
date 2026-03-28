"""Tests for the Token model."""

import dataclasses
import time

import time_machine

from eight_sleep_client.models.token import Token
from eight_sleep_client.api.constants import TOKEN_EXPIRY_BUFFER_SECONDS


# --- class methods ---


@time_machine.travel(1000000.0, tick=False)
def test_from_api_response_maps_fields():
    data = {
        "access_token": "tok123",
        "refresh_token": "ref456",
        "expires_in": 72000,
        "userId": "user789",
    }
    token = Token.from_api_response(data)

    assert token.access_token == "tok123"
    assert token.refresh_token == "ref456"
    assert token.user_id == "user789"


@time_machine.travel(1000000.0, tick=False)
def test_from_api_response_computes_expires_at_from_expires_in():
    token = Token.from_api_response({
        "access_token": "tok",
        "refresh_token": "ref",
        "expires_in": 72000,
        "userId": "user",
    })
    assert token.expires_at == 1000000.0 + 72000


# --- instance behavior ---


def test_is_expired_returns_false_when_fresh():
    token = _make_token(expires_at=time.time() + 72000)
    assert not token.is_expired


def test_is_expired_returns_true_when_within_buffer():
    token = _make_token(expires_at=time.time() + TOKEN_EXPIRY_BUFFER_SECONDS - 1)
    assert token.is_expired


def test_is_expired_returns_true_when_past():
    token = _make_token(expires_at=time.time() - 100)
    assert token.is_expired


def test_token_is_frozen():
    token = _make_token()
    try:
        token.access_token = "changed"  # type: ignore[misc]
        assert False, "Should have raised FrozenInstanceError"
    except dataclasses.FrozenInstanceError:
        pass


# --- helpers ---


def _make_token(**overrides) -> Token:
    """Create a Token with sensible defaults."""
    defaults = {
        "access_token": "test-access-token",
        "refresh_token": "test-refresh-token",
        "expires_at": time.time() + 72000,
        "user_id": "test-user-id",
    }
    defaults.update(overrides)
    return Token(**defaults)
