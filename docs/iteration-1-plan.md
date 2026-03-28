# Plan: eight_sleep_client — Iteration 1 (Auth + Get User)

## Status

**Repo:** `~/code/ravigadad/eight_sleep_client/`
**Progress:** Authenticator, Client, and Session implemented. Next: update `__init__.py` exports, smoke test with real credentials.

### Completed
- [x] Package scaffolding (pyproject.toml, LICENSE, README, py.typed, all __init__.py)
- [x] `api/constants.py` — API URLs, default credentials (overridable via constructor)
- [x] `api/exceptions.py` — exception hierarchy (EightSleepError, AuthenticationError, RequestError, ConnectionError)
- [x] `models/token.py` — Token (frozen dataclass, `from_api_response`, `is_expired`)
- [x] `models/user_info.py` — UserInfo (frozen dataclass, `from_api_response`)
- [x] `api/authenticator.py` — Authenticator (token lifecycle)
- [x] `client.py` — Client (internal; authenticated HTTP with 401 retry)
- [x] `session.py` — Session (public entry point via `Session.create()`)
- [x] `tests/models/test_token.py` — 6 tests passing
- [x] `tests/models/test_user_info.py` — 3 tests passing
- [x] `tests/api/test_authenticator.py` — 8 tests passing
- [x] `tests/test_client.py` — 5 tests passing
- [x] `tests/test_session.py` — 3 tests passing
- [x] Dev environment: pyenv 3.12.8, venv, pytest + respx + time-machine + pytest-watch
- [x] `docs/api_reference.md` — API reference
- [x] `docs/plan.md` — client library roadmap with architecture
- [x] `CLAUDE.md` — project instructions
- [x] GitHub repo (public): ravigadad/eight_sleep_client

### Next up
- [ ] Update `__init__.py` exports
- [ ] Manual smoke test with real credentials

## Context

Standalone async Python client library for the Eight Sleep Pod API. Built from scratch to replace the vendored `pyEight/` library in the `ravigadad/eight_sleep` HACS integration. This library has no Home Assistant dependencies — it's a pure API client.

## Decisions made

- **Layered architecture** — Model→Repository→Session→Client (see plan.md)
- **Session.create()** is the public entry point — callers never touch Client
- **Short class names** — Session, Client, Token (package provides namespace)
- **httpx** (async) for HTTP — caller injects `httpx.AsyncClient`
- **respx** for test mocking — declarative HTTP stubbing for httpx
- **pytest** + **pytest-asyncio** + **time-machine** for testing
- **One class per file**, file named after the class
- **Semantic folder structure** — `api/` for HTTP infrastructure, `models/` for domain objects
- **Test folders mirror source folders** — tests/api/, tests/models/
- **Dependency injection** — caller provides `httpx.AsyncClient`, library never creates its own
- **No Home Assistant imports** anywhere in the library
- **Frozen dataclasses** for infrastructure models (Token, UserInfo) — domain models (future) will be mutable with behavior
- **TDD** — write tests first, then implementation
- **Constants are defaults, overridable via constructor**

## File structure

```
eight_sleep_client/                  ← repo root
├── pyproject.toml
├── LICENSE
├── README.md
├── CLAUDE.md
├── docs/
│   ├── api_reference.md
│   ├── plan.md
│   └── iteration-1-plan.md
│
├── eight_sleep_client/              ← importable package
│   ├── __init__.py
│   ├── py.typed
│   ├── client.py                    ✓ Client (internal)
│   ├── session.py                   ✓ Session (public entry point)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── authenticator.py         ✓ Authenticator
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
    ├── test_client.py               ✓ (5 tests)
    ├── test_session.py              ✓ (3 tests)
    ├── api/
    │   ├── __init__.py
    │   └── test_authenticator.py    ✓ (8 tests)
    └── models/
        ├── __init__.py
        ├── test_token.py            ✓ (6 tests)
        └── test_user_info.py        ✓ (3 tests)
```

## Test conventions

- `# --- section ---` comments to organize tests
- Factory helpers (`_make_token()`, etc.) at bottom of test files
- Consistent test naming: `test_<method>_<behavior>`
- Always use `Mock(spec=Class)` — never unconstrained mocks
- Stub collaborators at boundaries; don't construct real instances
- time-machine for freezing time in expiry tests

## Verification

1. `pytest` — 25 tests passing
2. Manual smoke test with real credentials (next)
3. `grep -r "homeassistant" eight_sleep_client/` — verify no HA imports
