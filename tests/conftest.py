"""Shared test configuration and fixtures."""

import pytest
from mockito import unstub


@pytest.fixture(autouse=True)
def _unstub():
    yield
    unstub()
