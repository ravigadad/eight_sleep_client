# Appendix

## Contents

- [Legacy Routines Endpoint (Deprecated)](#legacy-routines-endpoint-deprecated)
- [WebSocket Events](#websocket-events)
- [Deprecated vs Current Endpoints](#deprecated-vs-current-endpoints)

## Legacy Routines Endpoint (Deprecated)

```
GET https://app-api.8slp.net/v2/users/{userId}/routines
```

Returns `settings.routines` (empty for newer alarm configs) and `settings.oneOffAlarms`. Recurring alarms have moved to the dedicated `/alarms` endpoint above. One-off alarms still appear here but with less detail than the alarms endpoint. This endpoint should not be used for new development.

## WebSocket Events

```
wss://app-api.8slp.net/v1/users/{userId}/events
```

Real-time push channel. Standard WebSocket upgrade (`Sec-WebSocket-Version: 13`) with the same Bearer token in the `Authorization` header. Opened on every app launch; reconnected when the app resumes from background.

The only event type observed is `temp-dial` — temperature state changes. Alarm mutations, base position changes, priming triggers, and other actions do **not** produce events on this channel (confirmed by testing all of these while listening). The app relies on polling (~60s) for everything except temperature.

Message format (JSON text frames):
```json
{
  "userId": "userId",
  "eventType": "temp-dial",
  "timestamp": "2026-03-30T00:52:36Z",
  "event": {
    "currentLevel": 22,
    "currentState": "smart:bedtime",
    "deviceId": "deviceId",
    "specialization": "pod"
  }
}
```

Notes:
- `currentState`: observed values `"off"`, `"smart:bedtime"` (same values as the temperature REST API).
- `currentLevel`: the raw level (same scale as `currentLevel` in the temperature endpoints). `null` when off.
- Each temperature action fires 2+ events — appears to be a "before" and "after" pair.
- Temperature overrides (tonight-only level changes) produce events showing the new `currentLevel`.
- Server-push only — no client-to-server messages observed.
- Connection is idle (no heartbeat/ping) when nothing is happening. No messages received during 30+ seconds of inactivity.

## Deprecated vs Current Endpoints

Several legacy endpoints still functioned as of March 2026 but are no longer used by the iOS app. They could be removed at any time.

| Feature | Legacy Endpoint | Current Endpoint | Notes |
|---------|----------------|-----------------|-------|
| **Alarms** | `GET/PUT v2/.../routines` | `GET v2/.../alarms`, `POST/PUT/DELETE v1/.../alarms` | Legacy returns `[]` for alarms created in current app versions |
| **Away mode** | `PUT v1/.../away-mode` | `DELETE/PUT v1/household/.../current-set` | Legacy still accepts writes |
| **Temperature on/off** | `PUT v1/.../temperature` | `PUT v1/.../temperature/pod` | Same concept, different path |
| **Temperature override** | `PUT v1/.../temperature` with `currentLevel` | `PUT v1/.../temperature/pod` with `overrideLevels` | Legacy lacks "tonight only" vs "permanent" distinction |
| **Side assignment** | `PUT client-api/.../current-device` | `PUT app-api/.../household/users/{userId}/current-set` | Both appear functional |
| **Priming** | `POST .../priming/tasks` with `"meta": "rePriming"` | Same endpoint with `"meta": "fill_pod_maintenance"` | Likely cosmetic difference |
