# CLAUDE.md

## Project

- Async Python client library for the Eight Sleep Pod API
- Uses httpx (async) for HTTP — caller injects `httpx.AsyncClient`
- No Home Assistant or framework dependencies — pure Python
- Comprehensive API reference at `docs/api_reference.md` (reverse-engineered from iOS app via MITM proxy, March 2026)
- Architecture and roadmap at `docs/plan.md`

## Architecture

Layered: **Model → Repository → Session → Client**

- `Session` — public entry point via `Session.create()`. Owns repositories.
- `Client` — internal. Authenticated HTTP with 401 retry. Only Session knows it exists.
- `Repository` (per domain) — knows API URLs/request shapes. Constructs models.
- `Model` — mutable objects with behavior that delegates to its repository.

Short class names — `Session`, `Client`, `Token` (package provides namespace).

## Structure

- `eight_sleep_client/` — importable package
  - `session.py` — Session (public entry point)
  - `client.py` — Client (internal, authenticated HTTP)
  - `api/` — HTTP/auth infrastructure
    - `authenticator.py` — Authenticator (token management)
    - `constants.py` — API URLs, default client credentials
    - `exceptions.py` — exception hierarchy
  - `utils.py` — shared utilities (snake_to_camel, camel_to_snake)
  - `models/` — domain objects
    - `alarm.py` — Alarm model + settings classes
    - `settings.py` — Settings metaclass and settings_property descriptor
    - `token.py` — Token (frozen dataclass, infrastructure)
    - `user_info.py` — UserInfo (frozen dataclass, infrastructure)
  - `repositories/` — domain repositories (one per domain)
    - `alarm_repository.py` — AlarmRepository
- `tests/` — test suite (mirrors source structure)
  - `helpers.py` — shared test helpers (e.g. `mock_response`)
  - `api/` — tests for api/ classes
  - `models/` — tests for model classes
  - `repositories/` — tests for repositories
- `docs/api_reference.md` — full API reference
- `docs/plan.md` — architecture and roadmap

## API Base URLs

- `auth-api.8slp.net/v1/tokens` — authentication
- `client-api.8slp.net/v1` — device data, user profiles, LED brightness
- `app-api.8slp.net` — temperature, alarms, base, features (v1 and v2 paths)

## Design Principles

- One class per file, file named after the class
- Semantic folder structure — `api/` for HTTP infrastructure, `models/` for domain objects
- Dependency injection — never create our own httpx client
- Frozen dataclasses for infrastructure models (Token, UserInfo)
- Domain models (Alarm, etc.) are mutable with behavior, delegating to repositories
- Factory methods (`from_api_response`) for parsing API JSON into models
- Custom exceptions (no framework dependencies in exception hierarchy)

## Testing

- pytest + mockito (declarative mocking with strict verification)
- TDD — write tests first, then implementation
- Unit tests only — no "integrated" tests that cross object boundaries
- Stub collaborators at boundaries; never let a test execute code in a collaborator
- Use `mock(ClassName)` for strict mocks; `mock({"attr": val}, spec=Class)` for attribute stubs
- Use `when(obj).method(args).thenReturn(val)` for stubbing; `verify(obj).method(args)` for assertions
- `when` sets up behavior (use matchers like `any()` or `...`); `verify` asserts the interaction
- Pure value objects (frozen dataclasses) don't need mocking — test them directly
- Shared test helpers in `tests/helpers.py`; factory helpers at bottom of test files
- Test file structure mirrors source structure

## Rules

- No Home Assistant imports anywhere in the library
- All API calls use httpx async
- Follow existing code style (Python, async/await, type hints)
- Constants are defaults, overridable via constructor parameters

## Commits

- Subject line: max 50 chars, imperative mood, no trailing period
- Body: wrap at 72 chars, separated from subject by blank line
- Body should explain the "why" behind the change, not the "what"
- Do NOT include "Co-Authored-By" or any attribution trailers
