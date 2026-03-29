"""Tests for the UserInfo model."""

import dataclasses

import pytest

from eight_sleep_client.models.user_info import UserInfo


# --- class methods ---


def test_from_dict_maps_fields():
    raw = {"userId": "abc123", "devices": ["dev1", "dev2"], "email": "test@example.com"}
    info = UserInfo.from_dict(raw)

    assert info.user_id == "abc123"
    assert info.device_ids == ["dev1", "dev2"]
    assert info.raw is raw


def test_from_dict_defaults_missing_devices_to_empty():
    info = UserInfo.from_dict({"userId": "abc123"})
    assert info.device_ids == []


# --- instance behavior ---


def test_user_info_is_frozen():
    info = UserInfo.from_dict({"userId": "abc123"})
    with pytest.raises(dataclasses.FrozenInstanceError):
        info.user_id = "changed"  # type: ignore[misc]
