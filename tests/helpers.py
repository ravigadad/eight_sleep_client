"""Shared test helpers."""

import httpx
from mockito import mock, when


def mock_response(status_code: int, json_data: dict) -> httpx.Response:
    """Create a mock httpx.Response with the given status code and JSON body."""
    response = mock({"status_code": status_code}, spec=httpx.Response)
    when(response).json().thenReturn(json_data)
    return response
