# Eight Sleep Client Library Plan

Async Python client for the Eight Sleep Pod API. Based on reverse-engineering the iOS app API via MITM proxy (March 2026). Full API reference: `docs/api_reference.md`.

## Architecture

### Layers

```
Model → Repository → Session → Client
```

- **Client** — internal. Authenticated HTTP with automatic 401 retry. Only Session knows it exists.
- **Session** — public entry point via `Session.create()`. Owns repositories. Exposes them to callers.
- **Repository** (per domain, e.g. `AlarmRepository`) — public. Knows API URLs and request/response shapes. Constructs models with a back-reference to itself.
- **Model** (e.g. `Alarm`) — public. Mutable objects with behavior (e.g. `alarm.snooze()`) that delegates to its repository. Not frozen dataclasses.

Each layer only knows the one below it. Callers interact with Sessions, Repositories, and Models — never Client.

### Infrastructure

- **Token**, **UserInfo** — frozen dataclasses. Internal infrastructure data, not caller-facing domain objects.
- **Authenticator** — token lifecycle (credential exchange, caching, refresh). Used by Client.

### Design choices

- **httpx** (async) for HTTP — caller injects `httpx.AsyncClient`
- **Dependency injection** — library never creates its own httpx client
- **One class per file**, file named after the class
- **Semantic folder structure** — `api/` for HTTP infrastructure, `models/` for domain objects
- **Short class names** — `Session`, `Client`, `Token` (package provides namespace)
- **TDD** — pytest + mockito, strict mocking at boundaries, tests mirror source structure
- **Constants are defaults, overridable via constructor**

## Iteration 1: Auth + User Discovery (complete)

Foundation: authenticate with the API and fetch user info.

- `Authenticator` — POST to `/v1/tokens`, token storage, auto-refresh on expiry
- `Client` — internal; authenticated HTTP requests with 401 retry
- `Session` — public entry point via `Session.create()`; convenience properties for user_id and device_ids
- `Token` — frozen dataclass with `is_expired` property
- `UserInfo` — frozen dataclass with `from_api_response` factory

## Iteration 2: Alarms

Full CRUD for the `/alarms` API.

**API endpoints:**
- List: `GET /v2/users/{userId}/alarms`
- Create: `POST /v1/users/{userId}/alarms`
- Update: `PUT /v1/users/{userId}/alarms/{alarmId}` (permanent changes at top level, `oneTimeOverride` for next-occurrence-only)
- Delete: `DELETE /v1/users/{userId}/alarms/{alarmId}`
- Skip/unskip: `PUT .../alarms/{alarmId}` with `skipNext: true/false`

**Architecture:**
- `AlarmRepository` — knows alarm API endpoints, constructs Alarm models
- `Alarm` — mutable model with behavior (`snooze()`, `delete()`, `skip()`, etc.) that delegates to AlarmRepository
- `Session.alarms` — exposes the AlarmRepository

## Iteration 3: Temperature Control

Migrate to `/temperature/pod` endpoint with full smart schedule support.

**API endpoints:**
- `PUT /v1/users/{userId}/temperature/pod` — on/off, override levels, permanent schedule
- `PUT /v1/users/{userId}/bedtime` — bedtime schedule time
- `PUT /v1/users/{userId}/level-suggestions-mode` — autopilot + ambient response toggles

## Iteration 4: Away Mode

Migrate to household `current-set` endpoint.

**API endpoints:**
- `GET /v1/household/users/{userId}/summary` — household state
- `DELETE /v1/household/users/{userId}/current-set` + `X-8S-Return-Date` header — start away
- `PUT /v1/household/users/{userId}/current-set` — end away

## Iteration 5: Additional Features

Low-effort features that add value: nap mode, hot flash mode, LED brightness, snore mitigation, tap gesture settings, priming, bed base control.
