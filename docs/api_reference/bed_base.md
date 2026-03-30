# Bed Base & Elevation

## Contents

- [Get Base State](#get-base-state)
- [Get Presets](#get-presets)
- [Set Preset](#set-preset)
- [Set Manual Angles](#set-manual-angles)

## Get Base State

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
    "macAddress": "AA:BB:CC:DD:EE:FF"
  }
}
```

Notes:
- `preset` key only appears when a preset is active. Absent when flat or custom angles.
- While moving: includes `startingAngle`, `targetAngle`, and `moving: true`.
- `modified: false` means angles still match the preset definition.

## Get Presets

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

## Set Preset

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

`snoreMitigation` — observed as `false` in all captures. Purpose not confirmed; possibly indicates whether the preset change is being triggered by the snore mitigation autopilot rather than manual user action.

## Set Manual Angles

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
- After setting, app rapid-polls `GET .../base` (several times per second) until `moving: false`, using the `currentAngle`/`targetAngle` to animate the position change in the UI. Base position changes do not push events over the WebSocket — polling is the only way to track movement.
