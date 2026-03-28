# Eight Sleep Client Library Plan

Async Python client for the Eight Sleep Pod API. Based on reverse-engineering the iOS app API via MITM proxy (March 2026). Full API reference: `docs/api_reference.md`.

## Architecture

- **httpx** (async) for HTTP
- **Dependency injection** — caller provides `httpx.AsyncClient`
- **One class per file**, semantic folder structure (`api/`, `models/`)
- **Session pattern** — `EightSleepClient.authenticate()` returns an `EightSleepSession` that carries user/device context for all subsequent operations
- **TDD** — pytest + respx, tests mirror source structure

## Iteration 1: Auth + User Discovery (in progress)

Foundation: authenticate with the API and fetch user info.

- `Authenticator` — POST to `/v1/tokens`, token storage, auto-refresh on expiry
- `EightSleepClient` — entry point, creates sessions, handles authenticated requests with 401 retry
- `EightSleepSession` — carries authenticated context (token, user_id, device_ids)
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

**Models:** `Alarm` with fields: `id`, `enabled`, `time`, `repeat` (weekdays map), `vibration`, `thermal`, `audio`, `smart`, `skipNext`, `nextTimestamp`, `snoozing`, `snoozedUntil`, `oneTimeOverride`

**Client methods:**
- `list_alarms()` → `list[Alarm]`
- `create_alarm(...)` → `Alarm`
- `update_alarm(alarm_id, ...)` → `Alarm`
- `delete_alarm(alarm_id)`
- `skip_next(alarm_id)` / `unskip(alarm_id)`
- `override_next(alarm_id, ...)` → `Alarm` (one-time override)
- `snooze_alarm(alarm_id, minutes)` / `stop_alarm(alarm_id)`

## Iteration 3: Temperature Control

Migrate to `/temperature/pod` endpoint with full smart schedule support.

**API endpoints:**
- `PUT /v1/users/{userId}/temperature/pod` — on/off, override levels, permanent schedule
- `PUT /v1/users/{userId}/bedtime` — bedtime schedule time
- `PUT /v1/users/{userId}/level-suggestions-mode` — autopilot + ambient response toggles

**Models:** `TemperatureState` (current levels, state, schedule), `SmartSchedule` (bedtime/initial/final levels)

**Client methods:**
- `get_temperature_state()` → `TemperatureState`
- `turn_on()` / `turn_off()`
- `override_tonight(bedtime=N, initial=N, final=N)`
- `set_smart_levels(bedtime=N, initial=N, final=N)` (permanent)
- `set_bedtime_schedule(time, days)`
- `set_autopilot(enabled)` / `set_ambient_response(enabled)`

## Iteration 4: Away Mode

Migrate to household `current-set` endpoint.

**API endpoints:**
- `GET /v1/household/users/{userId}/summary` — household state
- `DELETE /v1/household/users/{userId}/current-set` + `X-8S-Return-Date` header — start away
- `PUT /v1/household/users/{userId}/current-set` — end away

**Client methods:**
- `start_away(return_date)` / `end_away()`

## Iteration 5: Additional Features

Low-effort features that add value:

### Nap mode
- `start_nap(duration, level)` / `cancel_nap()` / `extend_nap()`
- `get_nap_status()` → active, remaining time, phase

### Hot flash mode
- `set_hot_flash(enabled, duration)`
- `get_hot_flash()` → enabled, duration

### LED brightness
- `set_led_brightness(level)` (0–100)

### Snore mitigation
- `set_snore_mitigation(enabled, level)` — low/medium/high

### Tap gesture settings
- `set_alarm_tap_action(action)` — snooze/stop
- `set_quad_tap_action(action)` — hot-flash-mode/thermal-alarm/nap

### Priming
- `prime_now()`
- `set_priming_schedule(enabled, time)`

### Bed base
- `set_base_preset(preset)` — sleep/reading/relaxing/flat
- `set_base_angles(torso, leg)`
- `get_base_state()` → angles, preset, moving status
