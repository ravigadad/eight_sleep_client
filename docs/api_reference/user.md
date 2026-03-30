# User

All user endpoints live on `client-api` except the health survey, which is on `app-api`.

## Contents

- [User ID and the `me` Alias](#user-id-and-the-me-alias)
- [Create Account](#create-account)
- [Get User](#get-user)
- [Update User](#update-user)
- [Health Survey](#health-survey)
  - [Read Full Health Survey](#read-full-health-survey)
  - [Update Health Survey](#update-health-survey)

## User ID and the `me` Alias

Most endpoints accept a literal user ID (a hex string). The `client-api` also accepts `me` as an alias for the authenticated user's ID — e.g. `GET /v1/users/me` is equivalent to `GET /v1/users/{userId}`.

The app fetches other users' profiles by their literal ID (e.g. a partner from `sharingMetricsTo`), using the same endpoint: `GET /v1/users/{otherUserId}`.

## Create Account

```
POST https://client-api.8slp.net/v1/users
```

Body:
```json
{
  "email": "user@example.com",
  "password": "password",
  "firstName": "First",
  "lastName": "Last",
  "gender": "other",
  "timezone": "America/Los_Angeles",
  "zip": 11111,
  "devices": [],
  "notifications": {
    "sessionProcessed": true,
    "marketingUpdates": true,
    "healthInsight": true,
    "alarmWakeupPush": true,
    "bedtimeReminder": true,
    "weeklyReportEmail": true,
    "sleepInsight": true,
    "temperatureRecommendation": true
  }
}
```

Response:
```json
{
  "session": {
    "expirationDate": "2026-04-13T05:50:26Z",
    "userId": "newUserId",
    "token": "legacy-session-token"
  },
  "user": { "...full user object..." }
}
```

Notes:
- Creates a new Eight Sleep account.
- The response includes a legacy `session` object with a non-JWT token. The app immediately follows up with a `POST /v1/tokens` password login to get a proper JWT access token.
- `gender`: observed values `"male"`, `"female"`, `"other"`, `"na"`.
- `devices: []` is always sent.
- The new user starts in a `"default"` household with no devices.

## Get User

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
- `sharingMetricsTo` / `sharingMetricsFrom` — linked user IDs (e.g. partner on shared pod). The app fetches linked users' profiles via `GET /v1/users/{linkedUserId}`.

## Update User

```
PUT https://client-api.8slp.net/v1/users/me?enableValidation=false
```

Partial update — send only the fields being changed. Response returns the full user object (same shape as GET).

Confirmed writable fields:

**`tempPreference`** — `"warm"`, `"neutral"`, `"cool"`. Affects autopilot baseline temperature recommendations.
```json
{ "tempPreference": "cool" }
```

**`displaySettings`** — any subset of display settings can be sent:
```json
{
  "displaySettings": {
    "useRealTemperatures": true,
    "locale": "en-US",
    "clockSystem": "24-hour",
    "measurementSystem": "metric"
  }
}
```
- `clockSystem`: `"12-hour"` or `"24-hour"`
- `measurementSystem`: `"imperial"` or `"metric"`
- `useRealTemperatures`: boolean
- `locale`: locale string (e.g. `"en-US"`)
- The app sends `clockSystem` and `locale` on every launch to sync with the device's settings.

**`notifications`** — any subset of notification preferences:
```json
{
  "notifications": {
    "bedtimeReminder": true,
    "weeklyReportEmail": false
  }
}
```

**`firstName`**, **`lastName`** — name fields are writable:
```json
{ "firstName": "New Name" }
```

**Multiple fields at once** — different top-level keys can be combined in a single PUT:
```json
{
  "tempPreference": "cool",
  "displaySettings": { "measurementSystem": "metric" },
  "notifications": { "bedtimeReminder": true }
}
```

Notes:
- `enableValidation=false` query param is observed in app traffic but is not required — the endpoint works without it.
- `devices: []` is sent by the app alongside other fields but is not required — updates work without it.
- `chronotype`: read-only — set by the pod's sleep analysis, not user-editable.

## Health Survey

Profile data that lives on `app-api` rather than `client-api`. The "test-drive" naming suggests this originated from the onboarding flow.

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

### Update Health Survey

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

Notes:
- First update in a session uses `enableValidation=true`, subsequent ones use `false`
- `sleepDisorders` values: `"insomnia"`, `"no-conditions"`, likely others. Use `"no-conditions"` (not `[]`) to indicate none.
- `preExistingConditions`: same pattern as sleepDisorders
- Weight, height, sleep disorders, and pre-existing conditions all use the same PATCH endpoint with different keys in `results`
