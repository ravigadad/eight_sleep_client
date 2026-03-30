# Autopilot & Analytics

Autopilot automatically adjusts temperature throughout the night based on sleep stage, ambient temperature, and learned preferences.

## Contents

- [Autopilot Options](#autopilot-options)
- [Level Suggestions](#level-suggestions)
- [Get Autopilot Config](#get-autopilot-config)
- [Get Nightly Recap](#get-nightly-recap)
- [Get Aggregate History](#get-aggregate-history)

## Autopilot Options

```
GET https://app-api.8slp.net/v1/users/{userId}/level-suggestions-mode
PUT https://app-api.8slp.net/v1/users/{userId}/level-suggestions-mode
```

GET returns the current autopilot configuration. PUT updates it.

PUT body:
```json
{
  "autopilotOptions": { "ambientTempEnabled": false }
}
```

Response (same shape for both GET and PUT):
```json
{
  "autopilotMode": "automatic",
  "autopilotEnabled": true,
  "autopilotOptions": {
    "ambientTempEnabled": true,
    "llmEnabled": false
  }
}
```

Also used to toggle autopilot itself: `{"autopilotEnabled": true/false}`

## Level Suggestions

```
GET https://app-api.8slp.net/v1/users/{userId}/level-suggestions
```

Cohort-based temperature level recommendations. Returns multiple suggestion types based on the user's demographic profile.

Response:
```json
{
  "levelSuggestions": [
    {
      "type": "bedtime-level",
      "createdAt": "2026-03-14T23:26:31Z",
      "data": {
        "cohort": {
          "genderGroup": "male",
          "ageGroup": "40",
          "temperatureGroup": "warm"
        },
        "community": [
          { "level": 10, "percentDifference": 0 }
        ],
        "personal": []
      }
    },
    {
      "type": "cohort",
      "createdAt": "2026-03-14T23:26:31Z",
      "data": {
        "cohort": {
          "genderGroup": "male",
          "ageGroup": "40",
          "temperatureGroup": "warm"
        },
        "levels": {
          "bedTimeLevel": 13,
          "initialSleepLevel": -5,
          "finalSleepLevel": 6
        }
      }
    },
    {
      "type": "cohort-v2",
      "createdAt": "2023-08-10T00:00:00Z",
      "data": {
        "cohort": {
          "age": 48,
          "gender": "male",
          "location": "Oregon",
          "country": "United States"
        },
        "levels": {
          "bedTimeLevel": {
            "distributions": [
              { "level": -10, "percent": 3.06, "aggregate": false },
              { "level": -2, "percent": 11.97, "aggregate": true },
              { "level": -1, "percent": 10.11, "aggregate": true },
              { "level": 0, "percent": 8.17, "aggregate": true },
              { "level": 10, "percent": 0.15, "aggregate": false },
              "..."
            ]
          },
          "initialSleepLevel": { "distributions": ["...same shape..."] },
          "finalSleepLevel": { "distributions": ["...same shape..."] }
        }
      }
    },
    {
      "type": "first-night",
      "createdAt": "2026-03-14T23:26:31Z",
      "data": {
        "cohort": {
          "ageGroup": "40",
          "genderGroup": "male",
          "temperatureGroup": "warm"
        },
        "pod": {
          "bedTimeLevel": 13,
          "initialSleepLevel": -5,
          "finalSleepLevel": 6
        },
        "pillow": {
          "bedTimeLevel": -10,
          "initialSleepLevel": -20,
          "finalSleepLevel": -10
        },
        "blanket": {
          "bedTimeLevel": 13,
          "initialSleepLevel": -1,
          "finalSleepLevel": 2
        }
      }
    },
    "..."
  ]
}
```

Notes:
- `type` values observed: `"bedtime-level"`, `"cohort"`, `"cohort-v2"`, `"first-night"`.
- `cohort` — simple recommended levels for the user's demographic group (gender, age decade, temperature preference).
- `cohort-v2` — full distribution curves per phase. Uses more specific cohort matching (exact age, location). Each level has a `percent` (what % of the cohort uses it) and `aggregate: true` marks the central cluster.
- `first-night` — recommended levels for a new user's first night, with separate suggestions for different products (pod, pillow, blanket).
- `bedtime-level` — community-level bedtime suggestion with a `percentDifference` field (observed as 0).
- Levels in these suggestions use the smart/dial scale (see [Level Scales](temperature.md#level-scales)).

## Get Autopilot Config

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

Includes snoring mitigation config (see [Sleep Features > Snore Mitigation](sleep_features.md#snore-mitigation)), autopilot mode/options, and calibration status. Fetched on every app page load.

## Get Nightly Recap

```
GET https://app-api.8slp.net/v1/users/{userId}/autopilotDetails/autopilotRecap?day=2026-03-14&tz=America/Los_Angeles
```

Response (showing 2 of 21 temperature adjustments):
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
    },
    "..."
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

## Get Aggregate History

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
