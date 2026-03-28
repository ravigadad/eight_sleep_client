# Plan: eight_sleep_client — Iteration 1 (Auth + Get User)

## Status: Complete

**Repo:** `~/code/ravigadad/eight_sleep_client/`

### Completed
- [x] Package scaffolding (pyproject.toml, LICENSE, README, py.typed, all __init__.py)
- [x] `api/constants.py` — API URLs, default credentials (overridable via constructor)
- [x] `api/exceptions.py` — exception hierarchy (EightSleepError, AuthenticationError, RequestError, ConnectionError)
- [x] `models/token.py` — Token (frozen dataclass, `from_api_response`, `is_expired`)
- [x] `models/user_info.py` — UserInfo (frozen dataclass, `from_api_response`)
- [x] `api/authenticator.py` — Authenticator (token lifecycle)
- [x] `client.py` — Client (internal; authenticated HTTP with 401 retry)
- [x] `session.py` — Session (public entry point via `Session.create()`)
- [x] `__init__.py` exports — Session is the public API
- [x] `tests/models/test_token.py` — 6 tests passing
- [x] `tests/models/test_user_info.py` — 3 tests passing
- [x] `tests/api/test_authenticator.py` — 8 tests passing
- [x] `tests/test_client.py` — 5 tests passing
- [x] `tests/test_session.py` — 3 tests passing
- [x] Dev environment: pyenv 3.12.8, venv, pytest + respx + time-machine + pytest-watch
- [x] `docs/api_reference.md` — API reference with live-captured response structures
- [x] `docs/plan.md` — client library roadmap with architecture
- [x] `CLAUDE.md` — project instructions
- [x] GitHub repo (public): ravigadad/eight_sleep_client
- [x] Smoke test with real credentials — Session.create() works end to end

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
- **mockito** for declarative mocking — strict by default, `when`/`verify` style
- **Constants are defaults, overridable via constructor**

## Verification

1. `pytest` — 24 tests passing
2. Smoke test with real credentials — confirmed working
3. `grep -r "homeassistant" eight_sleep_client/` — no HA imports
