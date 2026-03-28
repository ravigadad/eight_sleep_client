# Plan: eight_sleep_client — Iteration 2 (Alarms)

## Status

**Progress:** Not started.

## Goal

First domain feature using the full Model→Repository→Session→Client architecture. Alarms are a good proving ground — clear CRUD operations, well-documented API, and rich model behavior (snooze, skip, override).

## API Endpoints

All on `app-api.8slp.net`:

- **List:** `GET /v2/users/{userId}/alarms`
- **Create:** `POST /v1/users/{userId}/alarms`
- **Update:** `PUT /v1/users/{userId}/alarms/{alarmId}`
- **Delete:** `DELETE /v1/users/{userId}/alarms/{alarmId}`
- **Skip/unskip:** `PUT /v1/users/{userId}/alarms/{alarmId}` with `skipNext: true/false`
- **Snooze/stop:** `PUT /v1/users/{userId}/alarms/{alarmId}` with snooze payload

See `docs/api_reference.md` for full request/response structures.

## Classes

### `Alarm` (`models/alarm.py`)

Mutable domain model with behavior. Holds a back-reference to its repository.

```python
class Alarm:
    id: str
    enabled: bool
    time: str
    repeat: dict[str, bool]
    vibration: dict
    thermal: dict
    skip_next: bool
    # ... other fields from API

    async def snooze(self, minutes: int = 9) -> None: ...
    async def stop(self) -> None: ...
    async def skip(self) -> None: ...
    async def unskip(self) -> None: ...
    async def delete(self) -> None: ...
    async def update(self, **changes) -> None: ...
    async def override_next(self, **changes) -> None: ...
```

### `AlarmRepository` (`repositories/alarm_repository.py`)

Knows alarm API endpoints. Constructs Alarm models with back-reference to itself.

```python
class AlarmRepository:
    def __init__(self, session: Session) -> None: ...
    async def list(self) -> list[Alarm]: ...
    async def create(self, ...) -> Alarm: ...
    async def update(self, alarm_id: str, **changes) -> Alarm: ...
    async def delete(self, alarm_id: str) -> None: ...
    async def snooze(self, alarm_id: str, minutes: int) -> None: ...
    async def stop(self, alarm_id: str) -> None: ...
    async def skip(self, alarm_id: str) -> None: ...
    async def unskip(self, alarm_id: str) -> None: ...
    async def override_next(self, alarm_id: str, **changes) -> None: ...
```

### Session changes

Session gains an `alarms` property that returns the AlarmRepository.

```python
session = await Session.create(http, email="...", password="...")
alarms = await session.alarms.list()
await alarms[0].snooze(minutes=10)
```

## File structure (new files)

```
eight_sleep_client/
├── repositories/
│   ├── __init__.py
│   └── alarm_repository.py
└── models/
    └── alarm.py

tests/
├── repositories/
│   ├── __init__.py
│   └── test_alarm_repository.py
└── models/
    └── test_alarm.py
```

## Tasks

- [ ] Capture live alarm API responses for test fixtures
- [ ] `tests/models/test_alarm.py` — write tests first
- [ ] `models/alarm.py` — Alarm model with behavior
- [ ] `tests/repositories/test_alarm_repository.py` — write tests first
- [ ] `repositories/alarm_repository.py` — AlarmRepository
- [ ] Wire `Session.alarms` property
- [ ] Update `tests/test_session.py` for alarms property
- [ ] Smoke test with real credentials
- [ ] Update `__init__.py` exports

## Open questions

- Should `AlarmRepository` take a `Session` or a `Client`? Session gives access to `user_id` which is needed for URL construction. Client is the lower-level HTTP layer. Leaning toward Session since the repository needs user context, not just HTTP.
- How should we handle the `oneTimeOverride` vs permanent update distinction? Separate methods (`update` vs `override_next`) seem clearest.
- The list endpoint is v2 but create/update/delete are v1 — need to handle mixed base URLs.
