# Sleep Features

## Contents

- [Nap Mode](#nap-mode)
  - [Get Nap Settings](#get-nap-settings)
  - [Get Nap Alarm/Vibration Config](#get-nap-alarmvibration-config)
  - [Save Nap Alarm/Vibration Config](#save-nap-alarmvibration-config)
  - [Start Nap](#start-nap)
  - [Check Nap Status](#check-nap-status)
  - [Extend Nap](#extend-nap)
  - [Cancel Nap](#cancel-nap)
- [Hot Flash Mode](#hot-flash-mode)
  - [Get Settings](#get-settings)
  - [Update Settings](#update-settings)
- [Snore Mitigation](#snore-mitigation)
  - [Get/Set Snore Mitigation](#getset-snore-mitigation)

## Nap Mode

Start, monitor, extend, and cancel naps with per-nap temperature and alarm settings.

### Get Nap Settings

```
GET https://app-api.8slp.net/v1/users/{userId}/temperature/nap-mode
```

Response:
```json
{
  "defaultDuration": "00:20:00",
  "defaultLevels": {
    "pod": 15,
    "pillow": 0
  },
  "alarmRequested": true
}
```

### Get Nap Alarm/Vibration Config

```
GET https://app-api.8slp.net/v1/users/{userId}/temporary-mode/nap-mode
```

Response:
```json
{
  "vibrationEnabled": true,
  "vibrationLevel": 100,
  "vibrationPattern": "intense",
  "audioEnabled": false,
  "audioLevel": 30
}
```

### Save Nap Alarm/Vibration Config

```
PUT https://app-api.8slp.net/v1/users/{userId}/temporary-mode/nap-mode
```

Body and response share the same shape:
```json
{
  "vibrationEnabled": true,
  "vibrationLevel": 50,
  "vibrationPattern": "rise",
  "audioEnabled": false,
  "audioLevel": 30
}
```

### Start Nap

```
POST https://app-api.8slp.net/v1/users/{userId}/temperature/nap-mode/activate
```

Body:
```json
{
  "duration": "00:05:00",
  "levels": { "pod": 10 },
  "alarmRequested": true
}
```

Response:
```json
{
  "alarmRequested": true,
  "sessionId": "uuid",
  "active": true,
  "phase": "nap",
  "startTime": "2026-03-30T01:31:37Z",
  "remainingTime": "00:05:00",
  "duration": "00:05:00",
  "endTime": "2026-03-30T01:36:37Z",
  "levels": { "pod": 10 },
  "extensionCount": 0
}
```

All nap responses (status, extend, cancel) share this same structure. The fields that change between states are noted below.

### Check Nap Status

```
GET https://app-api.8slp.net/v1/users/{userId}/temperature/nap-mode/status
```

When a nap is active, returns the same structure as the activate response with a live `remainingTime` countdown:
```json
{
  "alarmRequested": true,
  "sessionId": "uuid",
  "active": true,
  "phase": "nap",
  "startTime": "2026-03-30T01:31:37Z",
  "remainingTime": "00:04:55",
  "duration": "00:05:00",
  "endTime": "2026-03-30T01:36:37Z",
  "levels": { "pod": 10 },
  "extensionCount": 0
}
```

When no nap is active, returns **404** with body: `No active nap session found`.

### Extend Nap

```
POST https://app-api.8slp.net/v1/users/{userId}/temperature/nap-mode/extend
```

Body:
```json
{
  "additionalDuration": "00:05:00"
}
```

Response — same structure, with `duration`, `endTime`, `remainingTime` updated and `extensionCount` incremented:
```json
{
  "alarmRequested": true,
  "sessionId": "uuid",
  "active": true,
  "phase": "nap",
  "startTime": "2026-03-30T01:31:37Z",
  "remainingTime": "00:09:55",
  "duration": "00:10:00",
  "endTime": "2026-03-30T01:41:37Z",
  "levels": { "pod": 10 },
  "extensionCount": 1
}
```

### Cancel Nap

```
PUT https://app-api.8slp.net/v1/users/{userId}/temperature/nap-mode/deactivate
```

No request body. Response — same structure, with `active: false` and `endTime` set to actual cancellation time:
```json
{
  "alarmRequested": true,
  "sessionId": "uuid",
  "active": false,
  "phase": "nap",
  "startTime": "2026-03-30T01:31:37Z",
  "remainingTime": "00:09:52",
  "duration": "00:10:00",
  "endTime": "2026-03-30T01:31:45Z",
  "levels": { "pod": 10 },
  "extensionCount": 1
}
```

Notes:
- `endTime` changes from the projected end to the actual cancellation time.
- `remainingTime` freezes at whatever was left when cancelled.
- After cancellation, `GET .../status` returns 404 — the session is immediately gone.

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

## Snore Mitigation

Controls the autopilot snore response settings. Note: this endpoint lives under the `autopilotDetails` path — the read side of the same data is returned in the [Autopilot Config](autopilot.md#get-autopilot-config) response. Separate from the base `inSnoreMitigation` sensor which indicates whether elevation is currently active.

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
