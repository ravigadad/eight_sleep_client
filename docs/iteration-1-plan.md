# Plan: eight_sleep_client — Iteration 1 (Auth + Get User)

## Status

**Repo:** `~/code/ravigadad/eight_sleep_client/`
**Progress:** Models done (Token, UserInfo). Next: Authenticator tests + implementation, then Client + Session.

### Completed
- [x] Package scaffolding (pyproject.toml, LICENSE, README, py.typed, all __init__.py)
- [x] `api/constants.py` — API URLs, default credentials (overridable via constructor)
- [x] `api/exceptions.py` — exception hierarchy (EightSleepError, AuthenticationError, RequestError, ConnectionError)
- [x] `models/token.py` — Token (frozen dataclass, `from_api_response`, `is_expired`)
- [x] `models/user_info.py` — UserInfo (frozen dataclass, `from_api_response`)
- [x] `tests/models/test_token.py` — 6 tests passing
- [x] `tests/models/test_user_info.py` — 3 tests passing
- [x] Dev environment: pyenv 3.12.8, venv, pytest + respx + time-machine installed
- [x] `docs/api_reference.md` — HA-agnostic API reference
- [x] `docs/plan.md` — client library roadmap
- [x] `CLAUDE.md` — project instructions

### Next up
- [ ] `tests/api/test_authenticator.py` — write tests first
- [ ] `api/authenticator.py` — implement to make tests pass
- [ ] `tests/test_session.py` — write tests first
- [ ] `session.py` — implement
- [ ] `tests/test_client.py` — write tests first
- [ ] `client.py` — implement (_request with 401 retry, authenticate returns session)
- [ ] Update `__init__.py` exports

## Context

Standalone async Python client library for the Eight Sleep Pod API. Built from scratch to replace the vendored `pyEight/` library in the `ravigadad/eight_sleep` HACS integration. This library has no Home Assistant dependencies — it's a pure API client.

Originally built inside `custom_components/eight_sleep/eight_sleep_client/` but extracted to its own repo to avoid Python parent-package import chain issues and to be independently publishable.

## Decisions made

- **httpx** (async) for HTTP — modern, clean API, HA supports it via `get_async_client(hass)`
- **respx** for test mocking — declarative HTTP stubbing for httpx
- **pytest** + **pytest-asyncio** + **time-machine** for testing
- **One class per file**, file named after the class
- **Semantic folder structure** — `api/` for HTTP infrastructure, `models/` for domain objects
- **Test folders mirror source folders** — tests/api/, tests/models/
- **Dependency injection** — caller provides `httpx.AsyncClient`, library never creates its own
- **No Home Assistant imports** anywhere in the library
- **Frozen dataclasses** for API response models
- **TDD** — write tests first, then implementation
- **Session pattern** — `EightSleepClient.authenticate()` returns an `EightSleepSession`
- **Constants are defaults, overridable via constructor** — supports HA options flow or env config

## File structure

```
eight_sleep_client/                  ← repo root
├── pyproject.toml
├── LICENSE
├── README.md
├── CLAUDE.md
├── docs/
│   ├── api_reference.md
│   └── plan.md
│
├── eight_sleep_client/              ← importable package
│   ├── __init__.py
│   ├── py.typed
│   ├── client.py                    ← EightSleepClient (TODO)
│   ├── session.py                   ← EightSleepSession (TODO)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── authenticator.py         ← Authenticator (TODO)
│   │   ├── constants.py             ✓
│   │   └── exceptions.py            ✓
│   └── models/
│       ├── __init__.py
│       ├── token.py                 ✓
│       └── user_info.py             ✓
│
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_client.py               (TODO)
    ├── test_session.py              (TODO)
    ├── api/
    │   ├── __init__.py
    │   └── test_authenticator.py    (TODO)
    └── models/
        ├── __init__.py
        ├── test_token.py            ✓ (6 tests)
        └── test_user_info.py        ✓ (3 tests)
```

## Classes

### `Token` (`models/token.py`) ✓
```python
@dataclass(frozen=True)
class Token:
    access_token: str
    refresh_token: str
    expires_at: float
    user_id: str

    @classmethod
    def from_api_response(cls, data: dict) -> Token: ...
    @property
    def is_expired(self) -> bool: ...
```

### `UserInfo` (`models/user_info.py`) ✓
```python
@dataclass(frozen=True)
class UserInfo:
    user_id: str
    device_ids: list[str]
    raw: dict

    @classmethod
    def from_api_response(cls, data: dict) -> UserInfo: ...
```

### `Authenticator` (`api/authenticator.py`) — TODO
```python
class Authenticator:
    def __init__(self, http: httpx.AsyncClient, email: str, password: str): ...
    async def authenticate(self) -> Token: ...
    async def ensure_valid_token(self) -> Token: ...
    @property
    def token(self) -> Token | None: ...
```

### `EightSleepClient` (`client.py`) — TODO
```python
class EightSleepClient:
    def __init__(self, http: httpx.AsyncClient, email: str, password: str): ...
    async def authenticate(self) -> EightSleepSession: ...
    async def _request(self, method: str, url: str, **kwargs) -> dict: ...
```

### `EightSleepSession` (`session.py`) — TODO
```python
class EightSleepSession:
    def __init__(self, client: EightSleepClient, token: Token, user_info: UserInfo): ...
    @property
    def user_id(self) -> str: ...
    @property
    def device_ids(self) -> list[str]: ...
```

## Tests remaining

### tests/api/test_authenticator.py
1. `test_authenticate_success` — correct POST body to AUTH_URL, returns Token
2. `test_authenticate_invalid_credentials` — 401 raises AuthenticationError
3. `test_authenticate_server_error` — 500 raises AuthenticationError
4. `test_authenticate_network_error` — connection failure raises ConnectionError
5. `test_ensure_valid_token_returns_cached_when_fresh` — no HTTP call if token not expired
6. `test_ensure_valid_token_refreshes_when_expired` — re-authenticates when token.is_expired
7. `test_ensure_valid_token_authenticates_when_no_token` — first call triggers authenticate

### tests/test_client.py
1. `test_authenticate_returns_session` — returns EightSleepSession with correct user_id/device_ids
2. `test_request_not_authenticated` — _request() before authenticate() raises AuthenticationError
3. `test_request_401_triggers_refresh_and_retry` — refresh + retry on 401, succeeds
4. `test_request_401_retry_still_fails` — no infinite loop, raises after one retry
5. `test_request_server_error` — 500 raises RequestError
6. `test_request_sends_bearer_header` — Authorization header uses Bearer token

### tests/test_session.py
1. `test_session_exposes_user_id`
2. `test_session_exposes_device_ids`

## Test conventions

- `# --- class methods ---` / `# --- instance behavior ---` / `# --- helpers ---` section comments
- Factory helpers (`_make_token()`, `_make_user_info()`) at bottom of test files
- Consistent test naming: `test_<method>_<behavior>`
- `from_api_response` tests: one golden-path test with multiple asserts for field mapping, separate tests for edge cases
- time-machine for freezing time in expiry tests

## Verification

1. `cd ~/code/ravigadad/eight_sleep_client && source .venv/bin/activate && pytest` — all tests pass
2. Manual smoke test with real credentials after client is complete
3. `grep -r "homeassistant" eight_sleep_client/` — verify no HA imports
