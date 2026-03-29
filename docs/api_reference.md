# Eight Sleep API Reference

Reverse-engineered from the Eight Sleep iOS app via MITM proxy (March 2026).

## Authentication

```
POST https://auth-api.8slp.net/v1/tokens
```

Body:
```json
{
  "client_id": "0894c7f33bb94800a03f1f4df13a4f38",
  "client_secret": "f0954a3ed5763ba3d06834c73731a32f15f168f47d4f164751275def86db0c76",
  "grant_type": "password",
  "username": "<email>",
  "password": "<password>"
}
```

Response includes `access_token`, `expires_in` (72000s), `refresh_token`, `userId`.

Use `Authorization: Bearer <access_token>` on all subsequent requests. Tokens expire quickly in practice — re-auth before each batch of calls.

## Base URLs

- **client-api**: `https://client-api.8slp.net/v1`
- **app-api**: `https://app-api.8slp.net`

## User Info

```
GET https://client-api.8slp.net/v1/users/me
```

Response:
```json
{
  "user": {
    "userId": "string",
    "email": "string",
    "firstName": "string",
    "lastName": "string",
    "gender": "male|female",
    "tempPreference": "warm|cool",
    "tempPreferenceUpdatedAt": "ISO8601",
    "dob": "ISO8601",
    "zip": 11111,
    "emailVerified": true,
    "sharingMetricsTo": ["userId", ...],
    "sharingMetricsFrom": ["userId", ...],
    "notifications": {
      "weeklyReportEmail": true,
      "sessionProcessed": true,
      "temperatureRecommendation": false,
      "healthInsight": false,
      "sleepInsight": false,
      "marketingUpdates": false,
      "bedtimeReminder": false,
      "alarmWakeupPush": false
    },
    "displaySettings": {
      "useRealTemperatures": false,
      "locale": "en-US",
      "clockSystem": "12-hour|24-hour",
      "measurementSystem": "imperial|metric"
    },
    "createdAt": "ISO8601",
    "experimentalFeatures": true,
    "autopilotEnabled": false,
    "lastReset": "ISO8601",
    "nextReset": "ISO8601",
    "sleepTracking": {
      "enabledSince": "ISO8601"
    },
    "chronotype": "late|early|...",
    "isChronotypeCalibrating": false,
    "chronotypeDate": "ISO8601",
    "autoPodTemperatureOff": false,
    "features": ["warming", "cooling", "vibration", "tapControls", "elevation", "alarms"],
    "currentDevice": {
      "id": "string",
      "side": "solo|left|right",
      "timeZone": "America/Los_Angeles",
      "specialization": "pod"
    },
    "hotelGuest": false,
    "devices": ["deviceId", ...]
  }
}
```

Notable fields:
- `currentDevice.side` — which side of the bed this user occupies (`solo` for single-user pods)
- `features` — capabilities of the user's pod
- `devices` — flat list of device IDs (same as `currentDevice.id` for single-device accounts)
- `sharingMetricsTo` / `sharingMetricsFrom` — linked user IDs (e.g. partner on another pod)

---

## Device Info

```
GET https://client-api.8slp.net/v1/devices/{deviceId}
```

Response:
```json
{
  "result": {
    "deviceId": "string",
    "ownerId": "userId",
    "leftUserId": "userId",
    "rightUserId": "userId",
    "leftHeatingLevel": -42,
    "leftTargetHeatingLevel": 0,
    "leftNowHeating": false,
    "leftHeatingDuration": 0,
    "leftSchedule": {
      "daysUTC": { "sunday": false, "monday": false, ... },
      "enabled": false
    },
    "rightHeatingLevel": -42,
    "rightTargetHeatingLevel": 0,
    "rightNowHeating": false,
    "rightHeatingDuration": 0,
    "rightSchedule": {
      "daysUTC": { "sunday": false, "monday": false, ... },
      "enabled": false
    },
    "priming": false,
    "lastLowWater": "ISO8601",
    "needsPriming": false,
    "hasWater": true,
    "ledBrightnessLevel": 0,
    "sensorInfo": {
      "label": "string",
      "partNumber": "string",
      "sku": "string",
      "hwRevision": "string",
      "serialNumber": "string",
      "lastConnected": "ISO8601",
      "skuName": "queen|king|...",
      "model": "Pod4|...",
      "version": 4,
      "supportsMaintenanceInserts": true,
      "connected": true
    },
    "sensors": [ { "...same fields as sensorInfo..." } ],
    "expectedPeripherals": null,
    "hubInfo": "string",
    "timezone": "America/Los_Angeles",
    "mattressInfo": {
      "firstUsedDate": null,
      "eightMattress": null,
      "brand": null
    },
    "firmwareCommit": "string",
    "firmwareVersion": "string",
    "firmwareUpdated": true,
    "firmwareUpdating": false,
    "lastFirmwareUpdateStart": "ISO8601",
    "lastHeard": "ISO8601",
    "online": true,
    "leftKelvin": {
      "targetLevels": [21, 18, 8],
      "alarms": [],
      "scheduleProfiles": [
        {
          "enabled": true,
          "startLocalTime": "22:30:00",
          "weekDays": { "monday": true, ... }
        }
      ],
      "phases": [],
      "level": 0,
      "currentTargetLevel": 0,
      "active": false,
      "currentActivity": "off"
    },
    "rightKelvin": { "...same structure as leftKelvin..." },
    "features": ["warming", "cooling", "vibration", "tapControls", "elevation", "alarms"],
    "leftUserInvitationPending": false,
    "rightUserInvitationPending": false,
    "modelString": "Pod 4",
    "hubSerial": "string",
    "wifiInfo": {
      "signalStrength": -53,
      "ssid": "string",
      "ipAddr": "192.168.1.x",
      "macAddr": "AA:BB:CC:DD:EE:FF",
      "asOf": "ISO8601"
    },
    "awaySides": {
      "leftUserId": "userId",
      "rightUserId": "userId"
    },
    "lastPrime": "ISO8601",
    "isTemperatureAvailable": true,
    "deactivated": {}
  }
}
```

Notable fields:
- `leftUserId` / `rightUserId` — per-side user assignment. Both are the same user for `solo` pods. Different users for shared beds.
- `sensorInfo.model` — hardware model (e.g. `Pod4`)
- `sensorInfo.skuName` — bed size (e.g. `queen`)
- `online`, `lastHeard`, `connected` — connectivity status
- `wifiInfo` — signal strength, IP, SSID, MAC
- `leftKelvin` / `rightKelvin` — per-side temperature state, schedules, and current activity
- `ledBrightnessLevel` — current LED brightness (0–100)
- `priming`, `needsPriming`, `hasWater`, `lastPrime` — water/maintenance status
- `firmwareVersion`, `firmwareUpdating` — firmware state
- `features` — device capabilities (same list as on user endpoint)
- Side assignment is on the device, not the user. The user endpoint's `currentDevice.side` reflects which side they're assigned to on this device.

---

## Alarms

The app uses a dedicated alarms API, **not** the legacy `/routines` endpoint. The legacy `GET /v2/.../routines` endpoint returns `routines: []` for alarms created in newer app versions.

### List Alarms

```
GET https://app-api.8slp.net/v2/users/{userId}/alarms
```

Response:
```json
{
  "recommendedAlarm": { ... },
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
    }
  ]
}
```

**Timestamp fields:**
- `nextTimestamp` — when the alarm will next fire (or is currently firing). Absent when disabled.
- `startTimestamp` — start of the alarm's active window. Always observed equal to `nextTimestamp`.
- `endTimestamp` — end of the active window, always 20 minutes after `startTimestamp`. This is likely how long the Pod will attempt to wake you (vibration, thermal ramp) before auto-stopping.
- All three advance together when snoozed. The distinction between `nextTimestamp` and `startTimestamp` may matter for smart wake alarms where the thermal ramp begins before vibration, but this hasn't been confirmed.

**No explicit "ringing" state:** The API does not have a field indicating the alarm is currently active. A ringing alarm looks the same as a pending one — `snoozing: false`, `dismissedUntil` at epoch. To determine if an alarm is currently ringing, compare the current time against the `startTimestamp`/`endTimestamp` window.

### Create Alarm

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
- `vibration.pattern`: `"RISE"` or `"INTENSE"`
- `vibration.powerLevel`: 20 (low), 50 (medium), 100 (high)
- `thermal.level`: -100 to 100 (unitless raw scale)
- `smart.lightSleepEnabled`: false disables smart wake (alarm fires at exact time)

### Update Alarm (Permanent)

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

### Override Next Occurrence Only

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

Response adds `enabledSince` and `enabledUntil` timestamps to the override. After `enabledUntil` passes, the override auto-expires.

### Skip Next Occurrence

Same `PUT` endpoint with full writable payload and `skipNext: true`. Do not send `skippedUntil` — the server sets it automatically along with `dismissedUntil`, and advances `nextTimestamp` to the following occurrence.

**Important:** Only repeating alarms can be skipped. Non-repeating alarms return "Only repeat alarms can skip next".

### Unskip

Same `PUT` endpoint with full writable payload and `skipNext: false`. The server resets `skippedUntil`, `dismissedUntil`, and `nextTimestamp` automatically.

### Enable/Disable Alarm

Same `PUT` endpoint with full writable payload and `enabled: true` or `enabled: false`.

### Dismiss / Stop Alarm

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

### Snooze Alarm

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


### Delete Alarm

```
DELETE https://app-api.8slp.net/v1/users/{userId}/alarms/{alarmId}
```

No request body. Response returns remaining `alarms` array.

---

## Bed Base / Elevation

### Get Base State

```
GET https://app-api.8slp.net/v1/users/{userId}/base
```

Response:
```json
{
  "left": {
    "torso": { "currentAngle": 2, "moving": false },
    "leg": { "currentAngle": 5, "moving": false },
    "preset": { "name": "sleep", "modified": false },
    "inSnoreMitigation": false
  },
  "right": { ... },
  "hardwareInfo": {
    "sku": "TriMix",
    "hardwareVersion": "4",
    "softwareVersion": "25",
    "macAddress": "3C:A5:51:99:FF:28"
  }
}
```

Notes:
- `preset` key only appears when a preset is active. Absent when flat or custom angles.
- While moving: includes `startingAngle`, `targetAngle`, and `moving: true`.
- `modified: false` means angles still match the preset definition.

### Get Presets

```
GET https://app-api.8slp.net/v2/users/{userId}/base/presets
```

Returns all available presets with angles. Structure:
```json
{
  "presets": [
    { "name": "sleep", "torsoAngle": 2, "legAngle": 5, "isDefault": false, "isEditable": true, "aliasOf": "sleep-custom" },
    { "name": "sleep-custom", "torsoAngle": 2, "legAngle": 5, "metaOf": "sleep", "isDefault": false, "isEditable": true },
    { "name": "flat", "torsoAngle": 0, "legAngle": 0, "isDefault": true, "isEditable": false },
    { "name": "anti-snore", "torsoAngle": 6, "isDefault": true, "isEditable": true, "aliasOf": "anti-snore-low" },
    ...
  ]
}
```

Preset hierarchy:
- Top-level presets: `sleep`, `reading`, `relaxing`, `anti-snore`, `flat`
- Sub-presets linked via `metaOf`: e.g. `sleep-flat`, `sleep-low`, `sleep-medium`, `sleep-custom`
- `aliasOf` points to the currently selected sub-preset
- `isEditable: true` means user can customize the angles

### Set Preset

```
POST https://app-api.8slp.net/v1/users/{userId}/base/angle?ignoreDeviceErrors=false
```

Body:
```json
{
  "preset": "sleep",
  "snoreMitigation": false
}
```

### Set Manual Angles

Same endpoint, but with angle values instead of preset:

```json
{
  "torsoAngle": 3,
  "legAngle": 5
}
```

Notes:
- The app sends both `torsoAngle` and `legAngle` even if only one changed.
- No `deviceId`, `deviceOnline`, or `enableOfflineMode` needed (the integration sends these but they're unnecessary).
- After setting, app polls `GET .../base` until `moving: false`.

---

## Snore Mitigation

Separate from the base `inSnoreMitigation` sensor. This controls the autopilot snore response settings.

### Get/Set Snore Mitigation

```
PUT https://app-api.8slp.net/v1/users/{userId}/autopilotDetails/snoringMitigation
```

Request:
```json
{
  "snoringMitigation": {
    "enabled": true,
    "mitigationLevel": "medium"
  }
}
```

`mitigationLevel`: `"low"`, `"medium"`, or `"high"`

Response includes additional read-only fields:
```json
{
  "snoringMitigation": {
    "enabled": true,
    "sleepStyle": "back",
    "mitigationLevel": "medium",
    "mitigationCount": 4,
    "daysWithMitigation": 291,
    "smartElevation": {
      "bedtimePreset": "sleep",
      "offPreset": "flat"
    }
  }
}
```

---

## Temperature State

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
      }
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
- `settings.scheduleType` — `smart` or `timeBased`
- `settings.smart` — three-phase temperature schedule: bedtime → initial sleep → final sleep
- `schedules` — configured bedtime schedules with per-day enablement
- `nextScheduledTimestamp` — when the pod will next activate
- `nextBedtimeDisplayWindow` — used by the app to decide when to show bedtime UI

---

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
  }],
  "schedules": [{
    "id": "uuid",
    "enabled": true,
    "time": "22:30:00",
    "days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
    "startSettings": { "bedtime": 17 }
  }],
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
- Level range observed: `-20` to `20` (relative adjustment, not absolute)
- App sends rapid PUTs (~1/sec) as user taps up/down
- Override clears automatically when turned off or at next scheduled session

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
    "id": "13947888-e8d6-456f-86c4-8fb22a3f04b8",
    "enabled": true,
    "time": "22:35:00",
    "days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
    "startSettings": { "bedtime": 17 }
  }]
}
```

Response includes full temperature state: `currentState`, `smart` levels, `hotFlash` settings, all `schedules`, `nextScheduledTimestamp`, and `nextBedtimeDisplayWindow`.

Notes:
- `time` is the auto-on time in 24h format
- `days` array controls which days the schedule is active
- `startSettings.bedtime` is the raw level the pod starts at (17 → 30°C/86°F)
- `schedules` is an array — supports multiple schedules (weekday/weekend split)
- `id` references an existing schedule to update it

### Update Autopilot Options (Ambient Response)

```
PUT https://app-api.8slp.net/v1/users/{userId}/level-suggestions-mode
```

Body:
```json
{
  "autopilotOptions": { "ambientTempEnabled": false }
}
```

Response:
```json
{
  "autopilotMode": "automatic",
  "autopilotEnabled": true,
  "autopilotOptions": {
    "ambientTempEnabled": false,
    "llmEnabled": false
  }
}
```

Also used to toggle autopilot itself: `{"autopilotEnabled": true/false}`

### Turn Off

Body:
```json
{
  "currentState": { "type": "off" }
}
```

Response shows `currentLevel: 0`, `overrideLevels: {}` (cleared), `smart` levels unchanged.

### Level Scales

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

3. **Device level** (`currentDeviceLevel`): yet another raw value (observed `-45` when `currentLevel` was `17`), likely the actual hardware target accounting for ambient conditions.

---

## Nap Mode

### Get Nap Settings

```
GET https://app-api.8slp.net/v1/users/{userId}/temperature/nap-mode
```

### Get Nap Alarm/Vibration Config

```
GET https://app-api.8slp.net/v1/users/{userId}/temporary-mode/nap-mode
```

### Save Nap Alarm/Vibration Config

```
PUT https://app-api.8slp.net/v1/users/{userId}/temporary-mode/nap-mode
```

```json
{
  "vibrationEnabled": true,
  "vibrationLevel": 100,
  "vibrationPattern": "intense",
  "audioEnabled": false,
  "audioLevel": 30
}
```

### Start Nap

```
POST https://app-api.8slp.net/v1/users/{userId}/temperature/nap-mode/activate
```

```json
{
  "duration": "00:21:00",
  "levels": { "pod": 15 },
  "alarmRequested": true
}
```

Response:
```json
{
  "sessionId": "uuid",
  "active": true,
  "phase": "nap",
  "startTime": "2026-03-14T22:23:01Z",
  "remainingTime": "00:21:00",
  "duration": "00:21:00",
  "endTime": "2026-03-14T22:44:01Z",
  "levels": { "pod": 15 },
  "alarmRequested": true,
  "extensionCount": 0
}
```

### Check Nap Status

```
GET https://app-api.8slp.net/v1/users/{userId}/temperature/nap-mode/status
```

Returns same structure as activate response, with live `remainingTime` countdown.

### Extend Nap

```
POST https://app-api.8slp.net/v1/users/{userId}/temperature/nap-mode/extend
```

```json
{
  "additionalDuration": "00:10:00"
}
```

Response shows updated `duration`, `endTime`, `remainingTime`, and incremented `extensionCount`.

### Cancel Nap

```
PUT https://app-api.8slp.net/v1/users/{userId}/temperature/nap-mode/deactivate
```

No request body. Response shows `active: false` with `endTime` set to actual stop time.

---

## Hot Flash Mode

Hot flash mode triggers a burst of cooling when a hot flash is detected during sleep.

### Get Settings

```
GET https://app-api.8slp.net/v1/users/{userId}/temperature/hot-flash-mode
```

Response:
```json
{
  "enabled": false,
  "levelDelta": -100,
  "hotFlashDuration": "0:15:00"
}
```

### Update Settings

```
PUT https://app-api.8slp.net/v1/users/{userId}/temperature/hot-flash-mode
```

Body:
```json
{
  "hotFlashSettings": {
    "enabled": true,
    "levelDelta": -100,
    "hotFlashDuration": "00:20:00"
  }
}
```

Response returns the flat object (no wrapper):
```json
{
  "enabled": true,
  "levelDelta": -100,
  "hotFlashDuration": "0:20:00"
}
```

Notes:
- `levelDelta`: appears fixed at `-100` (max cooling). The app UI does not expose this as configurable.
- `hotFlashDuration`: duration of the cooling burst. Default `"0:15:00"` (15 min). App allows adjustment.
- Duration format: server normalizes `"00:20:00"` → `"0:20:00"`.
- Settings persist across enable/disable — disabling keeps the configured duration.
- Request wraps in `hotFlashSettings`, response returns the flat object.

---

## Away Mode (Household Current-Set)

The app no longer uses the legacy `PUT /v1/users/{userId}/away-mode` endpoint. Instead, away mode works by detaching the user from their household "set" (device group).

### Get Household State

```
GET https://app-api.8slp.net/v1/household/users/{userId}/summary
```

Response (when home):
```json
{
  "currentSet": "f67ccf73-463e-4105-b7ce-057b5cf757d4",
  "households": [{
    "householdId": "...",
    "sets": [{
      "setId": "f67ccf73-463e-4105-b7ce-057b5cf757d4",
      "setName": "Main Bedroom",
      "devices": [{
        "deviceId": "...",
        "specialization": "pod",
        "pairing": { "leftUserId": "...", "rightUserId": "..." },
        "assignment": { "leftUserId": "...", "rightUserId": "..." }
      }]
    }],
    "users": [{
      "userId": "...",
      "schedules": []
    }]
  }]
}
```

Response (when away):
```json
{
  "currentSet": "default",
  "previousSet": "f67ccf73-...",
  "households": [{
    "sets": [{
      "devices": [{
        "pairing": {},
        "assignment": { "leftUserId": "...", "rightUserId": "..." }
      }]
    }],
    "users": [{
      "userId": "...",
      "schedules": [{
        "setId": "f67ccf73-...",
        "dateToReturn": "2026-03-17T07:00:00Z"
      }]
    }]
  }]
}
```

Key differences when away: `currentSet` becomes `"default"`, `previousSet` appears, device `pairing` empties, user gains a `schedules` entry with the return date.

### Set Away

```
DELETE https://app-api.8slp.net/v1/household/users/{userId}/current-set
```

- No request body (`Content-Length: 0`)
- Return date passed via custom header: `X-8S-Return-Date: 2026-03-17T07:00:00Z`
- Also sends header: `X-8S-Include-Partner: false`
- Response: `{}`

### End Away (Come Back)

Two simultaneous requests:

```
PUT https://app-api.8slp.net/v1/household/users/{userId}/current-set
```

Body:
```json
{
  "setId": "f67ccf73-463e-4105-b7ce-057b5cf757d4",
  "side": "solo"
}
```

Response:
```json
{
  "setId": "f67ccf73-...",
  "devices": [{
    "deviceId": "...",
    "specialization": "pod",
    "side": "solo",
    "timezone": "America/Los_Angeles"
  }]
}
```

Plus, simultaneously:
```
DELETE https://app-api.8slp.net/v1/household/users/{userId}/schedule/{setId}
```

No body. Clears the return-date schedule entry.

Notes:
- The `side` field is `"solo"` for single-user pods, likely `"left"` or `"right"` for dual.
- The `setId` comes from the `previousSet` in the summary response (or from the user's `schedules` array).
- A legacy `PUT /v1/users/{userId}/away-mode` endpoint also exists with `{"awayPeriod": {"start": "..."}}` / `{"awayPeriod": {"end": "..."}}`. This may still work but is not what the current app uses.

---

## Jet Lag Protocol (Beta)

Travel-based sleep protocol that adjusts sleep/wake times before and after flights to reduce jet lag. Only triggers when the timezone shift is large enough (a 2-hour shift was rejected as "no protocol needed"; a 3-hour shift triggered a full plan).

### Flight Lookup

```
GET https://app-api.8slp.net/v1/travel/flight-status?date=2026-04-20&flightNumber=ua1496
```

Response:
```json
{
  "legs": [{
    "departureAirport": "PDX",
    "departureAirportName": "PORTLAND INTL",
    "departureCity": "PORTLAND",
    "departureTimezone": "-07:00",
    "scheduledDepartureTime": "2026-04-20T14:00:00Z",
    "arrivalAirport": "ORD",
    "arrivalAirportName": "O HARE INTERNATIONAL",
    "arrivalCity": "CHICAGO",
    "arrivalTimezone": "-05:00",
    "scheduledArrivalTime": "2026-04-20T18:09:00Z",
    "aircraft": "738",
    "duration": "PT4H9M",
    "flightNumber": "1496",
    "carrierCode": "UA"
  }]
}
```

Notes:
- `flightNumber` param is lowercase carrier+number (e.g., `ua1496`)
- Each connecting flight is looked up separately
- No auth required beyond the standard Bearer token

### Create Trip

```
POST https://app-api.8slp.net/v1/users/{userId}/travel/trips
```

Body:
```json
{
  "legs": [
    {
      "legId": "client-generated-uuid",
      "origin": { "name": "PORTLAND", "timezone": "-07:00", "airportCode": "PDX" },
      "destination": { "name": "CHICAGO", "timezone": "-05:00", "airportCode": "ORD" },
      "departureTime": "2026-04-20T14:00:00.000000Z",
      "arrivalTime": "2026-04-20T18:09:00.000000Z"
    }
  ]
}
```

Response:
```json
{
  "tripId": "uuid",
  "name": "PORTLAND to ASHEVILLE/HENDERSONV.",
  "status": "Planning",
  "timezoneShift": { "offset": 3, "direction": "Eastbound" },
  "totalFlightHours": 7,
  "totalFlightTime": "7h 13m",
  "legs": [{ "...leg with server-computed layoverDuration and flightTime..." }]
}
```

### Generate Plan

```
POST https://app-api.8slp.net/v1/users/{userId}/travel/trips/{tripId}/plans
```

Body:
```json
{
  "supplementsEnabled": false
}
```

Response:
```json
{
  "planId": "uuid",
  "direction": "Eastbound",
  "status": "Ready",
  "startDate": "2026-04-18",
  "endDate": "2026-04-25",
  "supplementsEnabled": false,
  "stayingLongerThanThreeDays": false,
  "timezoneShift": { "offset": 3, "direction": "Eastbound" },
  "tasks": [
    {
      "taskId": "uuid",
      "name": "Wake up",
      "type": "WakeUp",
      "scheduledAt": "2026-04-18T14:30:00Z",
      "timezoneId": "-07:00",
      "instructions": "7:00-8:00 AM",
      "status": "Pending",
      "phase": "PreFlight",
      "metadata": {}
    }
  ],
  "groupedTasks": [
    {
      "phase": "PreFlight",
      "date": "2026-04-18",
      "timezoneId": "-07:00",
      "tasks": ["...same task objects..."]
    }
  ],
  "summary": {
    "totalDays": 5,
    "completedTasks": 0,
    "totalTasks": 13,
    "nextTaskDate": "2026-04-18",
    "isActive": false,
    "progress": 0
  }
}
```

Notes:
- Task types: `WakeUp`, `Sleep`, `Exercise`, `Nap`
- Phases: `PreFlight` (origin timezone), `PostFlight` (destination timezone)
- Plan starts 2 days before flight, continues ~2 days after arrival
- `supplementsEnabled` toggles supplement recommendations (melatonin, etc.)
- `stayingLongerThanThreeDays` — unclear if this affects plan generation (was `false` in test)

### List Trips

```
GET https://app-api.8slp.net/v1/users/{userId}/travel/trips
```

Returns array of trip objects with embedded plan summaries (no task details).

### Get Plan Details

```
GET https://app-api.8slp.net/v1/users/{userId}/travel/trips/{tripId}/plans
```

Returns array of full plan objects with all tasks.

### Delete Trip (Soft Delete)

```
PUT https://app-api.8slp.net/v1/users/{userId}/travel/trips/{tripId}
```

Body:
```json
{
  "status": "Completed",
  "name": "PORTLAND to ASHEVILLE/HENDERSONV."
}
```

Sets trip status to `"Completed"` rather than hard-deleting. Response returns the full trip object with updated status.

---

## Autopilot

Autopilot automatically adjusts temperature throughout the night based on sleep stage, ambient temperature, and learned preferences.

### Get Autopilot Config

```
GET https://app-api.8slp.net/v1/users/{userId}/autopilotDetails
```

Response:
```json
{
  "snoringMitigation": {
    "enabled": true,
    "sleepStyle": "back",
    "mitigationLevel": "low",
    "mitigationCount": 4,
    "daysWithMitigation": 291,
    "smartElevation": {
      "bedtimePreset": "sleep",
      "offPreset": "flat"
    }
  },
  "canUseMitigationLevels": true,
  "daysUntilCanUseLevels": 0,
  "userMode": {
    "autopilotMode": "automatic",
    "autopilotToggledOn": true,
    "autopilotOptions": {
      "ambientTempEnabled": true
    }
  },
  "calibrationStatus": {
    "isCalibrated": true,
    "isFirstSessionAfterCalibration": false,
    "calibrationDaysCompleted": 8,
    "daysRequiredForCalibration": 7
  },
  "hasActiveSubscription": true,
  "isAutopilotActive": true
}
```

Includes snoring mitigation config (see Snore Mitigation section), autopilot mode/options, and calibration status. Fetched on every app page load.

### Get Nightly Recap

```
GET https://app-api.8slp.net/v1/users/{userId}/autopilotDetails/autopilotRecap?day=2026-03-14&tz=America/Los_Angeles
```

Response:
```json
{
  "timestamp": "2026-03-14T17:27:30Z",
  "isProcessingComplete": true,
  "temperatureAdjustmentCount": 21,
  "pillowTemperatureAdjustmentCount": 0,
  "elevationAdjustmentCount": 0,
  "temperatureAdjustments": [
    {
      "fromLevel": 17,
      "toLevel": 2,
      "timestamp": "2026-03-14T12:58:06Z",
      "type": "smart",
      "phase": "early",
      "stage": "light"
    },
    {
      "fromLevel": 2,
      "toLevel": 5,
      "reason": "autopilot-ambient-temp:initial",
      "metadata": {
        "previousBedTime": 5,
        "previousInitialSleep": 2,
        "previousFinalSleep": 17,
        "currentBedTime": 5,
        "currentInitialSleep": 5,
        "currentFinalSleep": 17
      },
      "autopilot": {
        "description": "Autopilot increased your temperature by 0.3 when it detected that your bedroom temperature dropped",
        "template": "Autopilot increased your temperature by {delta} when it detected that your bedroom temperature dropped",
        "type": "autopilot-ambient-temp",
        "data": { "delta": ["dial-level", 0.3] }
      },
      "timestamp": "2026-03-14T12:58:12Z",
      "type": "autopilot",
      "phase": "early",
      "stage": "light"
    }
  ],
  "pillowTemperatureAdjustments": [],
  "elevationAdjustments": [],
  "temperatureSettingsUpdate": {
    "fromSettings": {
      "bedTimeLevel": 5,
      "initialSleepLevel": 2,
      "finalSleepLevel": 17
    },
    "toSettings": {
      "bedTimeLevel": 5,
      "initialSleepLevel": 5,
      "finalSleepLevel": 13
    }
  }
}
```

Notes:
- `type`: `"smart"` = schedule-based transitions (bed time → initial sleep → final sleep), `"autopilot"` = reactive adjustments
- `phase`: `"early"` or `"late"` in the sleep session
- `stage`: `"light"`, `"deep"`, `"rem"`, `"awake"` — the detected sleep stage when the adjustment was made
- `reason`: present on autopilot adjustments, e.g. `"autopilot-ambient-temp:initial"`, `"autopilot-ambient-temp:final"`
- `autopilot.description`: human-readable explanation of the adjustment
- `temperatureSettingsUpdate`: how autopilot modified the baseline temperature schedule for future nights
- Fetched on initial app load, provides the data for the nightly adjustment chart

### Get Aggregate History

```
GET https://app-api.8slp.net/v1/users/{userId}/autopilot-history
```

Response:
```json
{
  "userAutopilotHistory": {
    "totalInterventions": 9304,
    "totalNights": 977
  }
}
```

Lifetime totals only. Fetched when the user opens the autopilot detail view (not on initial app load).

---

## User Profile & Autopilot Profile

Profile data is split across two APIs: core user profile on `client-api`, and health survey data on `app-api`.

### Get/Update User Profile

```
PUT https://client-api.8slp.net/v1/users/me?enableValidation=false
```

Body (partial update — only fields being changed):
```json
{
  "tempPreference": "warm",
  "devices": []
}
```

Response returns full user object:
```json
{
  "user": {
    "userId": "...",
    "email": "...",
    "firstName": "...",
    "lastName": "...",
    "gender": "male",
    "tempPreference": "warm",
    "dob": "1977-09-06T07:00:00.000Z",
    "chronotype": "late",
    "isChronotypeCalibrating": false,
    "notifications": {
      "weeklyReportEmail": true,
      "sessionProcessed": true,
      "temperatureRecommendation": false,
      "bedtimeReminder": false,
      "alarmWakeupPush": false
    },
    "displaySettings": {
      "useRealTemperatures": false,
      "locale": "en-US",
      "clockSystem": "12-hour",
      "measurementSystem": "imperial"
    },
    "features": ["warming", "cooling", "vibration", "tapControls", "elevation", "alarms"],
    "currentDevice": {
      "id": "...",
      "side": "solo",
      "timeZone": "America/Los_Angeles",
      "specialization": "pod"
    },
    "experimentalFeatures": true,
    "autoPodTemperatureOff": false,
    "createdAt": "2016-09-22T06:24:46.964Z"
  }
}
```

Notes:
- `tempPreference`: `"warm"`, `"neutral"`, `"cool"` (affects autopilot baseline)
- `devices: []` is always sent alongside other fields (appears required)
- `chronotype`: `"late"`, presumably also `"early"` and `"average"`
- `features` array reflects device capabilities

### Update Health Survey (Weight, Sleep Disorders, etc.)

```
PATCH https://app-api.8slp.net/v1/health-survey/test-drive?enableValidation=true
```

Body — each field updated independently:
```json
{
  "testDrive": {
    "version": "v1",
    "results": {
      "weight": { "value": 140, "unit": "pounds" }
    }
  }
}
```

```json
{
  "testDrive": {
    "version": "v1",
    "results": {
      "sleepDisorders": ["insomnia"]
    }
  }
}
```

Response: `{}` (empty on success).

### Read Full Health Survey

```
GET https://app-api.8slp.net/v1/health-survey/test-drive
```

Response:
```json
{
  "testDrive": {
    "version": "v1",
    "results": {
      "height": { "value": 67, "unit": "inches" },
      "weight": { "value": 140, "unit": "pounds" },
      "sleepDisorders": ["no-conditions"],
      "preExistingConditions": ["no-conditions"]
    }
  }
}
```

Notes:
- First update in a session uses `enableValidation=true`, subsequent ones use `false`
- `sleepDisorders` values: `"insomnia"`, `"no-conditions"`, likely others. Use `"no-conditions"` (not `[]`) to indicate none.
- `preExistingConditions`: same pattern as sleepDisorders
- The "test-drive" naming suggests this originated from an onboarding flow
- Weight, height, sleep disorders, and pre-existing conditions all use the same PATCH endpoint with different keys in `results`

---

## Legacy Routines Endpoint (Deprecated)

```
GET https://app-api.8slp.net/v2/users/{userId}/routines
```

Returns `settings.routines` (empty for newer alarm configs) and `settings.oneOffAlarms`. Recurring alarms have moved to the dedicated `/alarms` endpoint above. One-off alarms still appear here but with less detail than the alarms endpoint. This endpoint should not be used for new development.

---

## Device Settings

### Side Assignment

Reuses the same `current-set` endpoint as away mode.

```
PUT https://app-api.8slp.net/v2/users/{userId}/household/users/{userId}/current-set
```

Body:
```json
{
  "side": "left",
  "setId": "<setId>"
}
```

Known `side` values: `"solo"`, `"left"`, `"right"`.

The `setId` comes from `GET .../household/users/{userId}/current-set` and identifies the household device set.

### Tap Gesture Settings

```
GET https://app-api.8slp.net/v1/users/{userId}/devices/all/tap-settings
PUT https://app-api.8slp.net/v1/users/{userId}/devices/{deviceId}/tap-settings
```

The PUT body contains a single gesture key with its configuration:

**Alarm tap action** (double-tap on bed):
```json
{
  "alarm": {
    "action": "snooze",
    "tapType": "double-tap"
  }
}
```

Known alarm actions: `"snooze"`, `"stop"`.

**Quad-tap action**:
```json
{
  "quadTap": {
    "action": "hot-flash-mode",
    "tapType": "quadruple-tap"
  }
}
```

Known quad-tap actions: `"hot-flash-mode"`, `"thermal-alarm"`, `"nap"`.

Each PUT sends only the gesture being changed — you don't need to send the full settings object.

### LED Brightness

Uses the `client-api` device endpoint:

```
PUT https://client-api.8slp.net/v1/devices/{deviceId}
```

Body:
```json
{
  "deviceId": "<deviceId>",
  "ledBrightnessLevel": 50
}
```

`ledBrightnessLevel` range: `0` (off/lowest) to `100`. The app may rate-limit rapid successive changes.

### Manual Priming

```
POST https://client-api.8slp.net/v1/devices/{deviceId}/priming/tasks
```

Body:
```json
{
  "notifications": {
    "users": ["{userId}"],
    "meta": "fill_pod"
  }
}
```

Response:
```json
{
  "task": {
    "reason": "requested",
    "created": "2026-03-15T00:04:19Z",
    "status": "starting",
    "notifications": {
      "users": ["{userId}"],
      "meta": "fill_pod"
    }
  }
}
```

The app polls `GET /v1/devices/{deviceId}/priming/tasks` to track progress (12-minute countdown).

### Priming Schedule (Daily Maintenance)

```
PUT https://client-api.8slp.net/v1/household/households/{householdId}/sets/{setId}/settings
```

**Disable daily maintenance:**
```json
{
  "primingSchedule": {
    "times": []
  }
}
```

**Enable daily maintenance (with schedule):**
```json
{
  "primingSchedule": {
    "times": [
      {"day": 1, "time": "14:00:00"},
      {"day": 2, "time": "14:00:00"},
      {"day": 3, "time": "14:00:00"},
      {"day": 4, "time": "14:00:00"},
      {"day": 5, "time": "14:00:00"},
      {"day": 6, "time": "14:00:00"},
      {"day": 7, "time": "14:00:00"}
    ]
  }
}
```

Days 1–7, each with an independent `time` (24h format, local time). The app defaults to the same time for all days but per-day customization is supported by the schema.

The `householdId` and `setId` come from `GET .../household/users/{userId}/current-set`.

---

## App Launch Sequence

On cold start, the app fires ~70 requests in ~2 seconds. Key categories:

- **Polling**: `GET .../base` every ~15s (bed position/movement), `.../alarms` + `.../temperature/all` + `.../hot-flash-mode` + `.../priming/tasks` + `.../devices/{id}` every ~60s
- **User/Auth**: `GET /v1/users/me` (×2), `GET /v1/users/{userId}`, `PUT /v1/users/{userId}` (timezone/last-seen update)
- **Sleep data**: `.../intervals` (paginated), `.../trends` (×2 date ranges), `.../metrics/aggregate?metrics=sleep_debt`, `.../tags`, `.../truth-tags`
- **AI/Insights**: `.../llm-insights` (×3, one per day: today, yesterday, day before), `.../llm-insights/settings`, `.../bedtime/recommendation`
- **Content**: `.../audio/tracks?category=soundscapes`, `...=alarms`, `...=nsdr`, `.../audio/categories`
- **Apple Health**: `.../health-integrations/.../checkpoints`, then ~10 sequential POSTs syncing data
- **Security**: `POST .../devices/{id}/security/key` (×4)
- **WebSocket**: `GET .../events` (status 101) for real-time push

---

## Other Endpoints Observed

Seen in app traffic but not yet documented in detail:

- `GET /v1/users/{userId}/temperature/all` — full temperature config (3 phases: bedTime, initialSleep, finalSleep)
- `GET /v1/users/{userId}/level-suggestions` — temperature level suggestions
- `GET/PUT /v1/users/{userId}/level-suggestions-mode` — suggestion mode config
- `GET /v1/audio/categories` — audio category list (Pod 5 Ultra only — requires built-in Base speakers)
- `GET /v1/users/{userId}/audio/tracks?category=soundscapes|alarms|nsdr` — audio library (Pod 5 Ultra only)
- `GET /v1/users/{userId}/audio/player` — speaker player state (Pod 5 Ultra only)
- `GET /v1/users/{userId}/llm-insights?from=...&to=...` — AI sleep insights (per day)
- `GET /v1/users/{userId}/llm-insights/settings` — insight notification settings
- `GET /v1/users/{userId}/metrics/aggregate?metrics=sleep_debt&periods=week&to=...&tz=...` — aggregated sleep metrics
- `GET /v1/users/{userId}/intervals` — sleep intervals (paginated via `?next=` cursor)
- `GET /v1/users/{userId}/trends?from=...&to=...&tz=...&model-version=v3` (client-api) — sleep trend data
- `GET /v1/users/{userId}/tags?from=...&to=...` (client-api) — sleep session tags
- `GET /v1/users/{userId}/truth-tags` — sleep session truth tags
- `GET /v1/users/{userId}/challenges` — gamification/challenges
- `GET /v1/users/{userId}/bedtime/recommendation` — recommended bedtime
- `GET /v1/users/{userId}/release-features` — feature flags
- `GET /v1/users/{userId}/health-integrations/metadata` — connected health apps
- `GET /v1/users/{userId}/health-integrations/sources/apple-health-{id}/checkpoints` — Apple Health sync checkpoints
- `POST /v1/users/{userId}/health-integrations/sources/apple-health-{id}` — Apple Health data sync (bulk, sequential)
- `GET /v1/users/{userId}/app-state/onboard` — onboarding state
- `GET /v1/devices/{deviceId}/priming/tasks` — priming task status
- `POST /v1/devices/{deviceId}/security/key` — device security key exchange (×4 on launch)
- `GET /v1/user/{userId}/device_maintenance/maintenance_insert?v=2` — maintenance status (note: `/user/` not `/users/`)
- `GET /v1/sms/users/{userId}` — SMS settings (returns 404)
- `GET /v1/purchase-tracker?email=...` — purchase/subscription tracking
- `GET /v2/users/{userId}/referral/campaigns` — referral program
- `GET /v1/household/users/{userId}/invitations` — household invitations
- `GET /v1/users/{userId}/events` — WebSocket (status 101) for real-time events

---

## Deprecated vs Current Endpoints

Several legacy endpoints still functioned as of March 2026 but are no longer used by the iOS app. They could be removed at any time.

| Feature | Legacy Endpoint | Current Endpoint | Notes |
|---------|----------------|-----------------|-------|
| **Alarms** | `GET/PUT v2/.../routines` | `GET/POST/PUT/DELETE v2/.../alarms` | Legacy returns `[]` for alarms created in current app versions |
| **Away mode** | `PUT v1/.../away-mode` | `DELETE/PUT v1/household/.../current-set` | Legacy still accepts writes |
| **Temperature on/off** | `PUT v1/.../temperature` | `PUT v1/.../temperature/pod` | Same concept, different path |
| **Temperature override** | `PUT v1/.../temperature` with `currentLevel` | `PUT v1/.../temperature/pod` with `overrideLevels` | Legacy lacks "tonight only" vs "permanent" distinction |
| **Side assignment** | `PUT client-api/.../current-device` | `PUT app-api/.../household/users/{userId}/current-set` | Both appear functional |
| **Priming** | `POST .../priming/tasks` with `"meta": "rePriming"` | Same endpoint with `"meta": "fill_pod"` | Likely cosmetic difference |
