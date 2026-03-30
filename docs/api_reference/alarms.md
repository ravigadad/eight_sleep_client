# Alarms

The app uses a dedicated alarms API, **not** the legacy `/routines` endpoint. The legacy `GET /v2/.../routines` endpoint returns `routines: []` for alarms created in newer app versions.

## Contents

- [List Alarms](#list-alarms)
- [Create Alarm](#create-alarm)
- [Update Alarm (Permanent)](#update-alarm-permanent)
- [Override Next Occurrence Only](#override-next-occurrence-only)
- [Skip / Unskip](#skip--unskip)
- [Enable / Disable](#enable--disable)
- [Dismiss / Stop](#dismiss--stop)
- [Snooze](#snooze)
- [Delete Alarm](#delete-alarm)

## List Alarms

```
GET https://app-api.8slp.net/v2/users/{userId}/alarms
```

Response:
```json
{
  "recommendedAlarm": {
    "id": "",
    "enabled": false,
    "time": "07:00:00",
    "repeat": { "enabled": true, "weekDays": { "monday": true, "...": true } },
    "vibration": { "enabled": true, "powerLevel": 80, "pattern": "INTENSE" },
    "thermal": { "enabled": true, "level": 50 },
    "smart": { "lightSleepEnabled": false, "sleepCapEnabled": false, "sleepCapMinutes": 480 },
    "skipNext": false,
    "dismissedUntil": "1970-01-01T00:00:00Z",
    "skippedUntil": "1970-01-01T00:00:00Z",
    "snoozedUntil": "1970-01-01T00:00:00Z",
    "snoozing": false,
    "tags": []
  },
  "alarms": [
    {
      "id": "uuid",
      "enabled": true,
      "time": "07:30:00",
      "repeat": {
        "enabled": true,
        "weekDays": {
          "monday": true, "tuesday": true, "wednesday": true,
          "thursday": true, "friday": true, "saturday": false, "sunday": false
        }
      },
      "vibration": { "enabled": true, "powerLevel": 50, "pattern": "RISE" },
      "thermal": { "enabled": true, "level": 4 },
      "audio": { "enabled": false, "level": 30 },
      "smart": {
        "lightSleepEnabled": true,
        "sleepCapEnabled": false,
        "sleepCapMinutes": 480
      },
      "skipNext": false,
      "nextTimestamp": "2026-03-16T14:30:00Z",
      "startTimestamp": "2026-03-16T14:30:00Z",
      "endTimestamp": "2026-03-16T14:50:00Z",
      "dismissedUntil": "1970-01-01T00:00:00Z",
      "skippedUntil": "1970-01-01T00:00:00Z",
      "snoozedUntil": "1970-01-01T00:00:00Z",
      "snoozing": false,
      "tags": ["routine-uuid"]
    },
    "..."
  ]
}
```

**Timestamp fields:**
- `nextTimestamp` — when the alarm will next fire (or is currently firing). Absent when disabled.
- `startTimestamp` — start of the alarm's active window. Always observed equal to `nextTimestamp`.
- `endTimestamp` — end of the active window, always 20 minutes after `startTimestamp`. This is likely how long the Pod will attempt to wake you (vibration, thermal ramp) before auto-stopping.
- All three advance together when snoozed. The distinction between `nextTimestamp` and `startTimestamp` may matter for smart wake alarms where the thermal ramp begins before vibration, but this hasn't been confirmed.

**`recommendedAlarm`:** The alarm the app shows on its main dashboard. When `id` is empty (`""`), this is a suggested template for users with no alarms — toggling it on creates a new alarm from the template. When `id` is a real alarm ID, it's a copy of the next upcoming alarm (matching an entry in the `alarms` array).

**No explicit "ringing" state:** The API does not have a field indicating the alarm is currently active. A ringing alarm looks the same as a pending one — `snoozing: false`, `dismissedUntil` at epoch. To determine if an alarm is currently ringing, compare the current time against the `startTimestamp`/`endTimestamp` window.

## Create Alarm

```
POST https://app-api.8slp.net/v1/users/{userId}/alarms
```

Body (non-recurring example):
```json
{
  "enabled": true,
  "time": "09:00:00",
  "repeat": {
    "enabled": false,
    "weekDays": {
      "monday": false, "tuesday": false, "wednesday": false,
      "thursday": false, "friday": false, "saturday": false, "sunday": false
    }
  },
  "vibration": { "enabled": true, "powerLevel": 50, "pattern": "INTENSE" },
  "thermal": { "enabled": true, "level": 50 },
  "audio": { "enabled": false, "level": 30 },
  "smart": { "lightSleepEnabled": false, "sleepCapEnabled": false, "sleepCapMinutes": 480 },
  "skipNext": false
}
```

Notes:
- The app sends a client-generated `id` but the server assigns a new one.
- `isSuggested`: observed as `true` when creating from the recommended alarm template, absent or `false` otherwise. Included in the writable fields sent by the app.
- `snoozing`: the app sends `false` on create. Included in writable fields.
- `tags`: empty array on create.
- `vibration.pattern`: `"RISE"` or `"INTENSE"`. The server accepts both values for all device types. The release features endpoint reports `supportedPatterns: ["intense"]` and `allowPatternSelection: false` for Pod 2 Pro, vs `["intense", "rise"]` and `allowPatternSelection: true` for Pod 4 — but these are UI hints only. The server does not validate pattern against device capability, and the app displays both patterns in the alarm UI regardless. Whether the Pod 2 Pro hardware actually vibrates differently for RISE vs INTENSE has not been tested. Any other pattern value (e.g. `"BOGUS"`) returns 400 — the server validates against a known enum (`Eight.Alarm.VibrationPattern`) but not against device support.
- `vibration.powerLevel`: 20 (low), 50 (medium), 100 (high)
- `thermal.level`: -100 to 100 (unitless raw scale). Note: the List Alarms example shows `thermal.level: 4` while the Create example uses `50` — these may be on different scales, or the low value may reflect autopilot adjustment. The exact scale and range of this field has not been fully mapped.
- `audio`: `{ "enabled": false, "level": 30 }` — audio alarm settings. Sent even on pods without speakers.
- `smart.lightSleepEnabled`: false disables smart wake (alarm fires at exact time)

## Update Alarm (Permanent)

```
PUT https://app-api.8slp.net/v1/users/{userId}/alarms/{alarmId}
```

Body: full alarm object with updated fields. Top-level `time`, `thermal`, `vibration`, etc. are changed permanently.

**The API requires the full writable alarm payload.** Partial updates fail with validation errors (e.g. missing `repeat` causes "Only repeat alarms can skip next"). The `id` field must also be present in the body.

Writable fields (sent by the iOS app):
- `id`, `enabled`, `time`, `skipNext`, `snoozing`, `isSuggested`
- `repeat` (`enabled`, `weekDays`)
- `vibration` (`enabled`, `powerLevel`, `pattern`)
- `thermal` (`enabled`, `level`)
- `audio` (`enabled`, `level`)
- `smart` (`lightSleepEnabled`, `sleepCapEnabled`, `sleepCapMinutes`)
- `tags`

Read-only fields (returned by GET, not sent by the app on PUT):
- `nextTimestamp`, `startTimestamp`, `endTimestamp` — absent when alarm is disabled
- `dismissedUntil`, `skippedUntil`, `snoozedUntil`

Note: the iOS app sends `skippedUntil` during unskip/disable/enable, but testing confirms the server does not require it. The standard writable fields are sufficient for all mutations.

The API silently ignores read-only fields if included in the PUT body, but sending them is not recommended.

## Override Next Occurrence Only

Same `PUT` endpoint, but include a `oneTimeOverride` object alongside the unchanged top-level fields:

```json
{
  "time": "08:30:00",
  "oneTimeOverride": {
    "time": "08:31:00",
    "vibration": { "enabled": true, "powerLevel": 50, "pattern": "RISE" },
    "thermal": { "enabled": false, "level": 20 },
    "audio": { "enabled": false, "level": 30 },
    "smart": { "lightSleepEnabled": true, "sleepCapEnabled": false, "sleepCapMinutes": 480 }
  },
  ...rest of alarm unchanged...
}
```

Response adds `enabledSince` and `enabledUntil` timestamps to the override. After `enabledUntil` passes, the override auto-expires. The `nextTimestamp` advances to reflect the overridden time.

To clear an override, send the standard writable payload without the `oneTimeOverride` field. The server removes the override and resets `nextTimestamp` to the original time.

**All five fields are required** in the `oneTimeOverride` object: `time`, `vibration`, `thermal`, `audio`, `smart`. Partial overrides (e.g. just `time` and `thermal`) are silently ignored — the server returns an empty override and no change takes effect.

## Skip / Unskip

**Skip:** Same `PUT` endpoint with full writable payload and `skipNext: true`. Do not send `skippedUntil` — the server sets it automatically along with `dismissedUntil`, and advances `nextTimestamp` to the following occurrence.

**Important:** Only repeating alarms can be skipped. Non-repeating alarms return "Only repeat alarms can skip next".

**Unskip:** Same `PUT` endpoint with full writable payload and `skipNext: false`. The server resets `skippedUntil`, `dismissedUntil`, and `nextTimestamp` automatically.

## Enable / Disable

Same `PUT` endpoint with full writable payload and `enabled: true` or `enabled: false`.

## Dismiss / Stop

```
PUT https://app-api.8slp.net/v1/users/{userId}/alarms/{alarmId}/dismiss
```

Body:
```json
{
  "ignoreDeviceErrors": false
}
```

Used for both dismissing an alarm early (before it rings) and stopping a ringing alarm. There is no separate `/stop` endpoint — the app uses `/dismiss` for both actions. Response returns the full `alarms` list.

Note: the legacy pyEight integration used `PUT /v1/users/{userId}/routines` with `{"alarm": {"alarmId": "...", "dismissed": true}}` — that's the old API. The modern app uses this dedicated `/dismiss` endpoint.

## Snooze

```
PUT https://app-api.8slp.net/v1/users/{userId}/alarms/{alarmId}/snooze
```

Body:
```json
{
  "snoozeMinutes": 9,
  "ignoreDeviceErrors": false
}
```

Response: `200 OK` with empty body. Server sets `snoozing: true`, `snoozedUntil` to current time + snooze minutes, and advances `nextTimestamp`/`startTimestamp`/`endTimestamp` to the new ring time.

While snoozed, the alarm state shows:
- `snoozing: true`
- `snoozedUntil: "2026-03-29T03:40:00Z"` (when it will ring again)
- `nextTimestamp` / `startTimestamp` advanced to match `snoozedUntil`
- `endTimestamp` advanced (new 20-minute window from the snoozed time)

## Delete Alarm

```
DELETE https://app-api.8slp.net/v1/users/{userId}/alarms/{alarmId}
```

No request body. Response returns remaining `alarms` array.
