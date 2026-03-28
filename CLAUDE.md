# CLAUDE.md

## Project

- Async Python client library for the Eight Sleep Pod API
- Uses httpx (async) for HTTP — caller injects `httpx.AsyncClient`
- No Home Assistant or framework dependencies — pure Python
- Comprehensive API reference at `docs/api_reference.md` (reverse-engineered from iOS app via MITM proxy, March 2026)
- Target hardware: Pod 4 Ultra (no speaker/audio features)

## Structure

- `eight_sleep_client/` — importable package
  - `client.py` — EightSleepClient (entry point, creates sessions)
  - `session.py` — EightSleepSession (authenticated context for all operations)
  - `api/` — HTTP/auth infrastructure
    - `authenticator.py` — Authenticator (token management)
    - `constants.py` — API URLs, default client credentials
    - `exceptions.py` — exception hierarchy
  - `models/` — domain objects (one class per file)
    - `token.py` — Token
    - `user_info.py` — UserInfo
- `tests/` — test suite (mirrors source structure)
  - `api/` — tests for api/ classes
  - `models/` — tests for model classes
- `docs/api_reference.md` — full API reference
- `docs/plan.md` — implementation plan

## API Base URLs

- `auth-api.8slp.net/v1/tokens` — authentication
- `client-api.8slp.net/v1` — device data, user profiles, LED brightness
- `app-api.8slp.net` — temperature, alarms, base, features (v1 and v2 paths)

## Design Principles

- One class per file, file named after the class
- Semantic folder structure — `api/` for HTTP infrastructure, `models/` for domain objects
- Dependency injection — never create our own httpx client
- Frozen dataclasses for API response models
- All behavior lives on the model it belongs to (e.g., `Token.is_expired`)
- Factory methods (`from_api_response`) for parsing API JSON into models
- Custom exceptions (no framework dependencies in exception hierarchy)
- Session pattern — `authenticate()` returns a session that carries context

## Testing

- pytest + respx (declarative HTTP mocking for httpx)
- TDD — write tests first, then implementation
- Unit + integration tests only — no "integrated" tests that cross object boundaries
- Test file structure mirrors source structure
- Factory helpers (`_make_token()`, etc.) at bottom of test files

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
