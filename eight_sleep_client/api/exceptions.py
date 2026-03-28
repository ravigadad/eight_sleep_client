"""Exception hierarchy for the Eight Sleep API client."""


class EightSleepError(Exception):
    """Base exception for all Eight Sleep client errors."""


class AuthenticationError(EightSleepError):
    """Raised when authentication fails (bad credentials, expired token, etc.)."""


class RequestError(EightSleepError):
    """Raised when an API request fails (HTTP 4xx/5xx, non-auth)."""


class ConnectionError(EightSleepError):
    """Raised when a network-level failure occurs (timeout, DNS, etc.)."""
