# Temperature

## Contents

- [Temperature State (client-api)](#temperature-state-client-api)
- [Temperature State (Full — app-api)](#temperature-state-full--app-api)
- [Temperature Control](#temperature-control)
  - [Turn On (Smart Mode)](#turn-on-smart-mode)
  - [Adjust Temperature (Tonight Only)](#adjust-temperature-tonight-only)
  - [Adjust Temperature (Permanent — "All Nights")](#adjust-temperature-permanent--all-nights)
  - [Update Bedtime Schedule](#update-bedtime-schedule)
  - [Turn Off](#turn-off)
- [Temperature Events](#temperature-events)
- [Level Scales](#level-scales)

## Temperature State (client-api)

```
GET https://client-api.8slp.net/v1/users/{userId}/temperature
```

Response:
```json
{
  "currentLevel": 0,
  "settings": {
    "scheduleType": "smart",
    "timeBased": {
      "level": 0,
      "durationSeconds": 0
    },
    "smart": {
      "bedTimeLevel": 21,
      "initialSleepLevel": 18,
      "finalSleepLevel": 8
    },
    "schedules": [
      {
        "id": "uuid",
        "enabled": true,
        "time": "22:30:00",
        "days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
        "tags": [],
        "startSettings": {
          "bedtime": 25
        }
      },
      "..."
    ],
    "smartProfiles": []
  },
  "nextScheduledTimestamp": "ISO8601",
  "currentState": {
    "type": "off|on|...",
    "instance": {
      "timestamp": "ISO8601"
    }
  },
  "currentSchedule": {
    "id": "uuid",
    "enabled": true,
    "time": "22:30:00",
    "days": ["monday", ...],
    "tags": [],
    "startSettings": {
      "bedtime": 25
    }
  },
  "nextSchedule": { "...same structure as currentSchedule..." },
  "nextBedtimeDisplayWindow": {
    "displayWindowHours": 16,
    "nextTimestampInWindow": true
  }
}
```

Notable fields:
- `currentLevel` — current temperature level (raw value, -100 to +100 range)
- `currentState.type` — whether the pod is currently active (`off`, `on`, etc.)
- `settings.scheduleType` — always `"smart"` in practice. `"timeBased"` appears as a possible value but is defunct (see below).
- `settings.timeBased` — legacy field, always `{"level": 0, "durationSeconds": 0}`. Attempting to activate `timeBased` mode returns 500 (app-api) or 400 `"does not match any of the allowed types"` (client-api). This mode is no longer functional.
- `settings.smart` — three-phase temperature schedule: bedtime → initial sleep → final sleep
- `settings.schedules[].startSettings.bedtime` — the raw level (-100 to +100) the pod heats/cools to when the schedule fires. This is separate from `smart.bedTimeLevel` which is on the smaller smart/dial scale (see [Level Scales](#level-scales)). The relationship between these two values is not fully understood — they appear to represent the same concept (bedtime temperature) on different scales.
- `nextScheduledTimestamp` — when the pod will next activate
- `nextBedtimeDisplayWindow` — used by the app to decide when to show bedtime UI

## Temperature State (Full — app-api)

```
GET https://app-api.8slp.net/v1/users/{userId}/temperature/all
```

This is the endpoint the app polls. Richer than the client-api endpoint above — includes device info, per-device current state, and historical temperature settings.

Response:
```json
{
  "devices": [
    {
      "device": {
        "deviceId": "string",
        "side": "solo|left|right",
        "specialization": "pod"
      },
      "currentLevel": 22,
      "currentDeviceLevel": -33,
      "overrideLevels": {},
      "currentState": {
        "type": "off|smart:bedtime|smart:initial|smart:final",
        "started": "ISO8601",
        "instance": {
          "timestamp": "ISO8601",
          "startedFrom": "user-initiated|scheduled"
        }
      },
      "smart": {
        "bedTimeLevel": 18,
        "initialSleepLevel": 15,
        "finalSleepLevel": 8
      }
    },
    "..."
  ],
  "temperatureSettings": [
    {
      "name": "deviceId or 'pod'",
      "bedTimeLevel": 18,
      "initialSleepLevel": 15,
      "finalSleepLevel": 8
    },
    "..."
  ],
  "nextScheduledTimestamp": "ISO8601",
  "schedules": [{ "...same as client-api..." }],
  "currentSchedule": { "..." },
  "nextSchedule": { "..." }
}
```

Notable differences from the client-api endpoint:
- `devices[]` — per-device/side with current state, levels, and overrides. Shared pods would have two entries.
- `currentDeviceLevel` — raw hardware target (different from user-facing `currentLevel`)
- `overrideLevels` — tonight-only overrides, empty `{}` when none active
- `temperatureSettings[]` — saved smart levels for every device the user has ever used (historical)
- `currentState.startedFrom` — distinguishes manual turn-on from scheduled

## Temperature Control

All temperature operations use a single endpoint:

```
PUT https://app-api.8slp.net/v1/users/{userId}/temperature/pod?ignoreDeviceErrors=false
```

### Turn On (Smart Mode)

Body:
```json
{
  "currentState": { "type": "smart" }
}
```

Response:
```json
{
  "devices": [{
    "device": { "deviceId": "...", "side": "solo", "specialization": "pod" },
    "currentLevel": 17,
    "currentDeviceLevel": -45,
    "overrideLevels": {},
    "currentState": {
      "type": "smart:bedtime",
      "started": "2026-03-14T23:31:02Z",
      "instance": { "timestamp": "...", "startedFrom": "user-initiated" }
    },
    "smart": {
      "bedTimeLevel": 5,
      "initialSleepLevel": 5,
      "finalSleepLevel": 13
    }
  }, "..."],
  "schedules": [{
    "id": "uuid",
    "enabled": true,
    "time": "22:30:00",
    "days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
    "startSettings": { "bedtime": 17 }
  }, "..."],
  "nextScheduledTimestamp": "2026-03-15T05:30:00Z"
}
```

Notes:
- `currentState.type` becomes `"smart:bedtime"` (or `"smart:initial"`, `"smart:final"` for later phases)
- `currentLevel` is the user-facing level, `currentDeviceLevel` is the raw device value
- `smart` object shows the three-phase temperature schedule (bedtime → initial sleep → final sleep)
- `schedules` shows the auto-on schedule with day-of-week config
- `startedFrom: "user-initiated"` distinguishes manual turn-on from scheduled

### Adjust Temperature (Tonight Only)

Body:
```json
{
  "overrideLevels": { "bedTime": -20 }
}
```

Notes:
- Overrides the current phase level for tonight only — does not change permanent `smart` levels
- Level range observed: `-20` to `20`. Whether these are relative adjustments or absolute values on the smart scale is not confirmed.
- App sends rapid PUTs (~1/sec) as user taps up/down
- Override clears automatically when turned off or at next scheduled session
- **Casing inconsistency**: PUT payload uses `bedTime` (camelCase with capital T), but the response returns `bedtime` (all lowercase) in `overrideLevels`

### Adjust Temperature (Permanent — "All Nights")

Body:
```json
{
  "smart": {
    "bedTimeLevel": 5,
    "initialSleepLevel": 25,
    "finalSleepLevel": -20
  },
  "overrideLevels": {}
}
```

Updates the permanent smart schedule levels and clears any tonight-only override. The app sends the full `smart` object with all three phases. Can be sent while the system is off — changes take effect at next session.

Note: when editing while the system is off, `ignoreDeviceErrors=true` is used instead of `false`.

### Update Bedtime Schedule

```
PUT https://app-api.8slp.net/v1/users/{userId}/bedtime?jsonErrorResponses=true
```

Body:
```json
{
  "schedules": [{
    "id": "schedule-uuid",
    "enabled": true,
    "time": "21:05:00",
    "days": ["monday", "tuesday", "wednesday"],
    "startSettings": {
      "bedtime": 10,
      "elevationPreset": "sleep",
      "pillowBedtime": 0
    }
  }, "..."]
}
```

Response includes full temperature state: `currentState`, `currentLevel`, `overrideLevels`, `currentDevice`, `nextScheduledTimestamp`, `settings` (with `scheduleType`, `timeBased`, `smart`, `schedules`), and `nextBedtimeDisplayWindow`.

Notes:
- `time` is the auto-on time in 24h format
- `days` array controls which days the schedule is active
- `startSettings.bedtime` is the raw level the pod starts at
- `startSettings.elevationPreset` — base preset to apply at bedtime (e.g. `"sleep"`). The app sends this even for pods without a base.
- `startSettings.pillowBedtime` — pillow temperature level at bedtime. Observed as `0`.
- `schedules` is an array — supports multiple schedules (weekday/weekend split). A second schedule with different days and time can be added in the same PUT.
- `id` references an existing schedule to update it. Omit `id` to create a new schedule (the server assigns one).
- To clear all schedules, send `"schedules": []` (empty array).

### Turn Off

Body:
```json
{
  "currentState": { "type": "off" }
}
```

Response shows `currentLevel: 0`, `overrideLevels: {}` (cleared), `smart` levels unchanged.

## Temperature Events

```
GET https://app-api.8slp.net/v1/users/{userId}/temp-events?from=2026-03-29T00:00:00Z
```

Returns a history of temperature state changes.

Response:
```json
{
  "events": [
    {
      "eventTime": "2026-03-30T04:26:18Z",
      "actionType": "smart",
      "deviceId": "deviceId",
      "currentPhase": "smart:bedtime",
      "previousPhase": "off",
      "currentLevel": 22
    },
    {
      "eventTime": "2026-03-30T01:00:19Z",
      "actionType": "dial-update",
      "deviceId": "deviceId",
      "currentPhase": "off",
      "previousPhase": "smart:bedtime",
      "previousLevel": 22
    },
    "..."
  ]
}
```

Notes:
- `actionType`: observed values `"smart"` (turn on/phase change), `"dial-update"` (level change or turn off).
- Each event includes the device ID — in a multi-device household, events for all devices appear.
- `currentLevel`/`previousLevel` appear depending on the action type.
- `from` query param filters by timestamp.

## Level Scales

The API uses two different level scales:

1. **Smart/dial levels** (`smart.bedTimeLevel`, etc.): small range. These map to the dial values shown in the app ("+1", "+2", "+3", etc.). Observed mapping:
   - `5` = "+1" (initial/final sleep), or "+2" (bedtime — possibly autopilot-adjusted)
   - `15` = "+2"
   - `25` = "+3"
   - `0` ≈ "0"
   - `-10` = "-1"
   - `-20` = "-2"
   - Approximate formula: **dial ≈ smart_level / 10** (each dial step ≈ 10 units)
   - Note: autopilot may adjust these levels between sessions (e.g., `finalSleepLevel` was `13` instead of the expected `10` for "+1")

2. **Raw levels** (`currentLevel`, `overrideLevels.bedTime`, `startSettings.bedtime`): range -100 to +100. Used for current state, overrides, autopilot adjustments, and schedule start levels. Maps to actual temperatures via lookup tables:
   - `0` → 27°C / 80°F
   - `17` → 30°C / 86°F
   - `27` → ~32°C / ~89°F
   - `-100` → 13°C / 55°F
   - `100` → 44°C / 111°F

3. **Device level** (`currentDeviceLevel`): a separate raw value that does not map to the same scale as `currentLevel` (observed `-45` when `currentLevel` was `17`). The relationship between these two values is not understood — `currentDeviceLevel` may represent the actual hardware target after accounting for ambient conditions, but this is not confirmed.
