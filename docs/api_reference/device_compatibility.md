# Device Compatibility

How the API represents different Pod hardware generations, and where the API's responses don't match actual device capabilities.

## Contents

- [Known Pod Generations](#known-pod-generations)
- [Cover vs Hub vs Subscription](#cover-vs-hub-vs-subscription)
  - [`features` array — Hardware capabilities](#features-array-on-user-and-device-endpoints--hardware-capabilities)
  - [`capabilities` array — Subscription entitlements](#capabilities-array-on-subscription-endpoint--subscription-entitlements)
  - [Individual config endpoints](#individual-config-endpoints--unreliable-as-capability-indicators)
  - [Recommended approach](#recommended-approach-for-determining-capabilities)
- [Device Response Differences](#device-response-differences)
- [Heating Level When Off](#heating-level-when-off)
- [Tap Settings](#tap-settings)
- [Priming Differences](#priming-differences)
- [Nap Vibration Config](#nap-vibration-config)
- [Vibration Patterns](#vibration-patterns)
- [Trends Response](#trends-response)
- [Recommended Alarm](#recommended-alarm)

## Known Pod Generations

| Model | `sensorInfo.model` | `sensorInfo.version` | `modelString` | `features` |
|-------|--------------------|-----------------------|---------------|------------|
| Pod 2 Pro | `Pod3` (with Pod 3 cover) | `3` | `Pod 2 Pro` | `warming`, `cooling`, `vibration`, `alarms` |
| Pod 4 | `Pod4` | `4` | `Pod 4` | `warming`, `cooling`, `vibration`, `tapControls`, `elevation`, `alarms` |

Notes:
- `sensorInfo.model` reflects the **cover** hardware, not the hub. A Pod 2 Pro hub with a Pod 3 cover reports `model: "Pod3"`.
- `modelString` reflects the **hub** hardware.
- Covers and hubs from adjacent generations can be mixed (Pod 3 cover on Pod 2 Pro hub is a supported configuration). The cover brings improved sensors and durability; the hub determines what actions are possible (heating, cooling, vibration, base control).
- Pod 5 Ultra has not been tested. Based on feature flags and API responses, it likely adds `"audio"` to the features list and supports the `audio/player` endpoint.

## Cover vs Hub vs Subscription

The API reports capabilities from three independent sources, and they don't always agree:

### `features` array (on user and device endpoints) — Hardware capabilities

**Trust this.** Reflects what the physical hardware can do. Determined by the hub, not the cover.

- Present on both `GET /v1/users/me` and `GET /v1/devices/{deviceId}`
- Pod 2 Pro: `["warming", "cooling", "vibration", "alarms"]`
- Pod 4: `["warming", "cooling", "vibration", "tapControls", "elevation", "alarms"]`
- If a feature is missing from this list, the device cannot perform it regardless of what other endpoints say.

### `capabilities` array (on subscription endpoint) — Subscription entitlements

**Overly permissive.** Reflects what the subscription *allows*, not what the hardware *supports*. Both a Pod 2 Pro and a Pod 4 with the same premium subscription return identical capabilities, including `"smart_elevation"`, `"snoring_mitigation"`, and `"snoring_detection"` — even when the device has no base.

### Individual config endpoints — Unreliable as capability indicators

**Don't trust the existence of a response as proof that a feature works.** Many endpoints return configuration for hardware that doesn't exist on the device:

| Endpoint | Pod 2 Pro (no base, no tap) | Pod 4 (base + tap) |
|----------|----------------------------|---------------------|
| `GET .../devices/all/tap-settings` | 200 — returns full tap config with options | 200 — returns config |
| `GET .../base/presets` | 200 — returns full preset catalog | 200 — returns catalog |
| `GET .../base` | 404 `PodOffline` | 200 — returns angles |
| `GET .../autopilotDetails` (snoring) | 200 — `snoringMitigation.enabled: true` | 200 — returns config |
| `GET .../audio/player` | 404 `PodOffline` | 404 `BaseNotPaired` |

- **Tap settings** return a full menu of actions (alarm dismiss/snooze, temperature control, quad-tap options) even for pods with no tap sensor. Tap hardware was introduced with Pod 4.
- **Base presets** are a server-side catalog returned for all devices, regardless of whether a base is connected.
- **Base state** correctly returns 404 for baseless pods.
- **Snore mitigation** reports `enabled: true` on pods with no base. The cover can *detect* snoring (via chest vibration sensors), but *mitigation* requires base elevation — impossible without the hardware. The API does not distinguish between detection and mitigation capability.
- **Audio player** correctly returns 404 on both, but with different error types depending on whether the server recognizes the device as speaker-capable (`BaseNotPaired`) or not (`PodOffline`).

### Recommended approach for determining capabilities

Use the `features` array as the source of truth for what a device can physically do:

```
"tapControls" in features  →  tap sensor is available
"elevation" in features    →  adjustable base is connected
"alarms" in features       →  vibration/thermal alarms work
"warming" in features      →  heating works
"cooling" in features      →  cooling works
```

For subscription-gated features, check `capabilities` on the subscription endpoint — but cross-reference with `features` before assuming the device can act on them.

## Device Response Differences

Fields that differ between Pod generations in the device endpoint (`GET /v1/devices/{deviceId}`):

### Pod 2 Pro only
- `location` — GPS coordinates `[-122.70, 45.44]`. Not present on Pod 4.
- `encasementType` — `"pod-pro-cover"`. Not present on Pod 4.
- `leftSchedule`/`rightSchedule` include legacy fields: `startUTCHour`, `startUTCMinute`, `durationSeconds`. Pod 4 does not have these.
- `hubInfo` — formatted as `"20500-0001-B02-00004F6E"`. Pod 4 does not have this field in the same format.
- `wifiInfo.ssid` and `wifiInfo.ipAddr` — always empty string on Pod 2 Pro, populated on Pod 4.

### Pod 4 only
- `wifiInfo` with populated `ssid`, `ipAddr`, `signalStrength`.
- `modelString: "Pod 4"` — Pod 2 Pro reports `"Pod 2 Pro"`.

### Both
- `sensorInfo`, `sensors`, `leftKelvin`/`rightKelvin`, `firmwareVersion`, `online`, `lastHeard`, `priming`, `needsPriming`, `hasWater`, `ledBrightnessLevel`, `features` — present on both with the same structure.

## Heating Level When Off

- Pod 2 Pro reports `leftHeatingLevel: -100`, `rightHeatingLevel: -100` when off
- Pod 4 reports `leftHeatingLevel: -42` when off
- Similarly, `currentDeviceLevel` in the temperature endpoint: `-100` for Pod 2 Pro, `-42` for Pod 4
- These differences may reflect different hardware baselines or calibration

## Tap Settings

The `GET /devices/all/tap-settings` endpoint returns identical configuration for all devices regardless of hardware capability — confirmed by comparing Pod 4 (has tap sensor) and Pod 2 Pro (no tap sensor). The full GET and PUT formats are documented in [Device > Tap Gesture Settings](device.md#tap-gesture-settings).

## Priming Differences

- Pod 2 Pro priming takes much longer (~1.5 hours observed) vs Pod 4 (~11 minutes). This reflects the Pod 4's hardware improvement ("fill with water in less than 10 minutes" per Eight Sleep's marketing).
- Pod 2 Pro has no scheduled priming (`priming/schedule` returns empty array). Only manual priming via POST.
- Pod 4 supports daily scheduled maintenance priming.
- Pod 2 Pro `supportsMaintenanceInserts: false` — no replaceable water filter.
- Pod 4 `supportsMaintenanceInserts: true`.

## Nap Vibration Config

Pod 2 Pro response omits the `audioLevel` field:
```json
{ "vibrationEnabled": true, "vibrationLevel": 100, "vibrationPattern": "intense", "audioEnabled": false }
```

Pod 4 includes it:
```json
{ "vibrationEnabled": true, "vibrationLevel": 100, "vibrationPattern": "intense", "audioEnabled": false, "audioLevel": 30 }
```

## Vibration Patterns

The release features endpoint reports different supported patterns per device:
- Pod 2 Pro: `supportedPatterns: ["intense"]`, `allowPatternSelection: false`
- Pod 4: `supportedPatterns: ["intense", "rise"]`, `allowPatternSelection: true`

However, these are **UI hints only**. The server accepts both `"RISE"` and `"INTENSE"` for all devices — confirmed by creating a RISE alarm on a Pod 2 Pro (accepted, stored, and displayed in the app). The app also shows both patterns in the alarm editor UI regardless of `allowPatternSelection`. Whether the Pod 2 Pro hardware actually executes the RISE pattern differently from INTENSE has not been tested.

## Trends Response

When the trends endpoint returns an empty `days` array (no sleep data), additional top-level aggregate fields appear that are not present when days are populated:

```json
{
  "days": [],
  "avgScore": 0,
  "avgPresenceDuration": 0,
  "avgSleepDuration": 0,
  "avgDeepPercent": 0,
  "avgTnt": 0,
  "modelVersion": "v3",
  "sfsCalculator": "v3.2"
}
```

These fields (`avgScore`, `modelVersion`, `sfsCalculator`, etc.) were not observed on accounts with populated trends data — they may only appear when the response is empty, or they may have been present but not noticed due to response truncation.

## Recommended Alarm

The alarms endpoint returns a `recommendedAlarm` alongside the `alarms` array — see [Alarms > List Alarms](alarms.md#list-alarms) for details. When no alarms exist, this is a template with `id: ""` suggesting a daily 7am alarm. When alarms exist, it's a copy of the next upcoming alarm.
