"""Tests for the UserInfo model."""

import dataclasses

from eight_sleep_client.models.user_info import UserInfo


# --- class methods ---


def test_from_api_response_maps_fields():
    raw = {"userId": "abc123", "devices": ["dev1", "dev2"], "email": "test@example.com"}
    info = UserInfo.from_api_response(raw)

    assert info.user_id == "abc123"
    assert info.device_ids == ["dev1", "dev2"]
    assert info.raw is raw


def test_from_api_response_defaults_missing_devices_to_empty():
    info = UserInfo.from_api_response({"userId": "abc123"})
    assert info.device_ids == []


# --- instance behavior ---


def test_user_info_is_frozen():
    info = _make_user_info()
    try:
        info.user_id = "changed"  # type: ignore[misc]
        assert False, "Should have raised FrozenInstanceError"
    except dataclasses.FrozenInstanceError:
        pass


# --- helpers ---


def _make_user_info(**overrides) -> UserInfo:
    """Create a UserInfo with sensible defaults."""
    defaults = {
        "user_id": "test-user-id",
        "device_ids": ["test-device-id"],
        "raw": {"userId": "test-user-id", "devices": ["test-device-id"]},
    }
    defaults.update(overrides)
    return UserInfo(**defaults)
