"""Default API URLs and client credentials for the Eight Sleep API.

These are the defaults used when no overrides are provided to the client.
Consumers can override any of these by passing values to the EightSleepClient
constructor.
"""

DEFAULT_AUTH_URL = "https://auth-api.8slp.net/v1/tokens"
DEFAULT_CLIENT_API_URL = "https://client-api.8slp.net/v1"
DEFAULT_APP_API_URL = "https://app-api.8slp.net"

DEFAULT_CLIENT_ID = "0894c7f33bb94800a03f1f4df13a4f38"
DEFAULT_CLIENT_SECRET = "f0954a3ed5763ba3d06834c73731a32f15f168f47d4f164751275def86db0c76"

TOKEN_EXPIRY_BUFFER_SECONDS = 120
