# Plan: eight_sleep_client — Iteration 2 (Alarms)

## Status: Complete

**Progress:** Full alarm CRUD + actions implemented and smoke tested.

### Completed
- [x] MITM capture of alarm operations (skip, unskip, enable, disable, dismiss, snooze, create, delete, override)
- [x] `models/alarm.py` — Alarm model with all read properties, settings classes, and mutation methods
- [x] `models/settings.py` — Settings metaclass and settings_property descriptor
- [x] `utils.py` — snake_to_camel, camel_to_snake utilities
- [x] `repositories/alarm_repository.py` — AlarmRepository with all, create, update, delete, snooze, dismiss
- [x] Session.alarms property wired
- [x] Client/Session put, post, delete methods with base URL resolution
- [x] Client handles empty response bodies (snooze/dismiss return 200 with no content)
- [x] Client uses cached_property for authenticator (cleaner test injection)
- [x] Migrated all tests to mockito with expect, strict boundaries
- [x] API reference updated with all alarm mutation findings
- [x] `__init__.py` exports updated
- [x] Smoke tested: create, update, delete, skip, unskip, override_next, clear_override

## Decisions made

- **Full payload required for updates** — API rejects partial updates; Alarm.writable_data() extracts writable fields
- **Sub-resource endpoints for snooze/dismiss** — different from the main PUT update
- **Dismiss = stop** — no separate stop endpoint; app uses /dismiss for both
- **No explicit ringing state** — infer from current time vs startTimestamp/endTimestamp window
- **Settings classes via metaclass** — auto-generated properties from annotations, snake_to_camel conversion
- **settings_property descriptor** — lazy class resolution for forward references
- **Alarm.update() sets fields then saves** — convenience methods (skip, enable, etc.) delegate to update
- **override_next merges with current settings** — API requires all five fields; caller passes only changes
- **writable_data strips None values** — enables clear_override via update(oneTimeOverride=None)
- **Repository is pure transport** — doesn't know which fields are writable; Alarm owns that knowledge

## Alarm API

```python
session = await Session.create(http, email="...", password="...")

# Read
alarms = await session.alarms.all()
alarm.time              # "08:30:00"
alarm.enabled           # True
alarm.skip_next         # False
alarm.next_timestamp    # datetime
alarm.vibration.enabled # True (settings objects)
alarm.repeat.days       # ["saturday", "sunday"]

# Mutations
await alarm.skip()              # skip next occurrence
await alarm.unskip()            # alias for skip(False)
await alarm.enable()            # enable alarm
await alarm.disable()           # alias for enable(False)
await alarm.update(time="09:00:00", thermal={"enabled": True, "level": 50})
await alarm.save()              # persist current state
await alarm.override_next(time="08:45:00", thermal={"enabled": True, "level": 100})
await alarm.clear_override()

# Sub-resource actions
await alarm.snooze(5)           # snooze for 5 minutes (default 9)
await alarm.dismiss()           # dismiss/stop ringing alarm

# CRUD
alarm = await session.alarms.create({...})
await alarm.delete()
```
