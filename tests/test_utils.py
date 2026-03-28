"""Tests for utility functions."""

import pytest

from eight_sleep_client.utils import camel_to_snake, snake_to_camel


@pytest.mark.parametrize("input,expected", [
    ("Vibration", "vibration"),
    ("Audio", "audio"),
    ("PickleDrumChocolate", "pickle_drum_chocolate"),
    ("LightSleep", "light_sleep"),
])
def test_camel_to_snake(input, expected):
    assert camel_to_snake(input) == expected


@pytest.mark.parametrize("input,expected", [
    ("power_level", "powerLevel"),
    ("enabled", "enabled"),
    ("light_sleep_enabled", "lightSleepEnabled"),
    ("sleep_cap_minutes", "sleepCapMinutes"),
])
def test_snake_to_camel(input, expected):
    assert snake_to_camel(input) == expected
