# App Client

Endpoints specific to the iOS app client — push notifications, feature flags, onboarding state, device security. These are not sleep-domain endpoints and are unlikely to be needed by a third-party client library, but are documented for completeness.

## Contents

- [Notifications](#notifications)
- [Push Targets](#push-targets)
  - [Register Push Token (on login)](#register-push-token-on-login)
  - [Deregister Push Token (on logout)](#deregister-push-token-on-logout)
- [Onboarding State](#onboarding-state)
- [Release Features (Feature Flags)](#release-features-feature-flags)
- [Device Security Key](#device-security-key)
- [Health Integrations (Apple Health Sync)](#health-integrations-apple-health-sync)
  - [Get Connected Sources](#get-connected-sources)
  - [Get Sync Checkpoints](#get-sync-checkpoints)
  - [Push Health Data](#push-health-data)
- [Support Chat Auth](#support-chat-auth)
- [SMS Settings](#sms-settings)

## Notifications

```
GET https://app-api.8slp.net/v1/users/{userId}/notifications?active=true&limit=10
```

Response:
```json
{
  "notifications": [],
  "pagination": {
    "limit": 10,
    "cursor": "",
    "hasMore": false
  }
}
```

Polled frequently by the app (every ~60s alongside other polling endpoints). Supports cursor-based pagination. We have never observed a non-empty `notifications` array, so the shape of a notification object is unknown.

## Push Targets

### Register Push Token (on login)

```
PUT https://client-api.8slp.net/v1/users/me/push-targets/{deviceUUID}
```

Body:
```json
{
  "deviceToken": "apns-push-token-hex-string",
  "platform": "ios"
}
```

Response: empty 200.

The `{deviceUUID}` in the URL is the iOS device identifier (from `X-Client-Device-Id` header), not the Eight Sleep pod ID. The `deviceToken` is the APNS push token.

### Deregister Push Token (on logout)

```
DELETE https://client-api.8slp.net/v1/users/me/push-targets/token/{apnsToken}
```

No request body. Response: empty 200.

## Onboarding State

```
GET https://app-api.8slp.net/v1/users/{userId}/app-state/onboard
```

A `PATCH` to this endpoint was also observed (during device onboarding) but the request body and response were not captured.

Response:
```json
{
  "value": {
    "testDriveCompletedTimestamp": "2026-03-15T00:04:41Z",
    "lastOnboardTime": "2026-03-15T00:04:41Z"
  }
}
```

Fetched once on app launch.

## Release Features (Feature Flags)

```
GET https://app-api.8slp.net/v1/users/{userId}/release-features
```

Response (abbreviated — full response is ~2.8KB):
```json
{
  "hrvReleaseDate": "2022-06-21T10:00:00Z",
  "routinesMinimumAppVersion": "6.0.0",
  "showHypnogramDetail": true,
  "hrvAlgo": "hrv-algo:1.2.0",
  "sleepAlgo": "full-nemean:0.1",
  "adjustableBase": false,
  "showAdjustableBaseTab": false,
  "snoreReport": true,
  "primingCancellation": true,
  "autopilotRecap": true,
  "enableAmbientTemperature": true,
  "enableHotFlashMode": true,
  "enableJetLag": true,
  "enableNapModeIOS": true,
  "enableMultipodV3": true,
  "enableSleepDebtIOS": true,
  "enableOfflineModeIOS": true,
  "supportedPatterns": ["intense", "rise"],
  "supportedPatternsByDevice": {
    "intense": [{ "deviceId": "...", "deviceName": "Main Bedroom" }, "..."],
    "rise": [{ "deviceId": "...", "deviceName": "Main Bedroom" }, "..."]
  },
  "patternsSupportedOnAllDevices": true,
  "deviceAlarmSupport": {
    "someSupport": true,
    "allSupport": true,
    "supportedDevices": [{ "deviceId": "...", "deviceName": "Main Bedroom" }, "..."]
  },
  "deviceVibrationSupport": {
    "someSupport": true,
    "allSupport": true,
    "supportedDevices": [{ "deviceId": "...", "deviceName": "Main Bedroom" }, "..."]
  }
}
```

A mix of feature flags, algorithm versions, UI toggles, and per-device capability declarations. Fetched once on app launch.

## Device Security Key

```
POST https://app-api.8slp.net/v1/devices/{deviceId}/security/key
```

Body:
```json
{
  "deviceToken": "AeMUyhslqWN7poWynFNNO7m/Tyg/OPFzekwHdQrq/hwGisYAAA=="
}
```

Response:
```json
{
  "expiresIn": 50826,
  "key": "HGt/AhscAHezjrtJL8kzarQbIGbcs6Qkf8pJMXvc0pY="
}
```

Called 4 times on app launch (possibly once per security context). The `deviceToken` here is base64-encoded and different from the APNS push token — likely a device attestation or encryption key. Purpose unclear; possibly for end-to-end encryption of sensitive device commands.

## Health Integrations (Apple Health Sync)

The app acts as a bridge between Apple HealthKit and Eight Sleep's servers, pushing daytime health data (exercise, steps, heart rate, etc.) that the pod can't measure. This likely feeds into autopilot algorithms and sleep analytics (e.g. the exercise/cognitive performance windows in trends data).

### Get Connected Sources

```
GET https://app-api.8slp.net/v1/users/{userId}/health-integrations/metadata
```

Response:
```json
{
  "from": "2026-03-22T23:47:23Z",
  "to": "2026-03-29T23:47:23Z",
  "totalDataPoints": 3231,
  "lastSyncedAt": "2026-03-29T22:49:54Z",
  "healthSourceCount": 3,
  "healthSources": [
    {
      "name": "Apple Watch",
      "identifier": "com.apple.health.0CC40EF5-B24A-4353-B9CD-784CB2CE37A3",
      "iconUrl": "https://app-media.8slp.net/mobile-health-platforms/3p-health-icons/apple_watch.png"
    },
    {
      "name": "iPhone",
      "identifier": "com.apple.health.F21AB78E-8CA1-40BE-BC94-2EFA47E97D1B",
      "iconUrl": "https://app-media.8slp.net/mobile-health-platforms/3p-health-icons/apple_health.png"
    },
    {
      "name": "apple-health",
      "identifier": "apple-health",
      "iconUrl": "https://app-media.8slp.net/mobile-health-platforms/3p-health-icons/unknown.png"
    },
    "..."
  ]
}
```

### Get Sync Checkpoints

```
GET https://app-api.8slp.net/v1/users/{userId}/health-integrations/sources/apple-health-{deviceUUID}/checkpoints
```

Response — per-HealthKit-type timestamps showing when each metric was last synced:
```json
{
  "HKQuantityTypeIdentifierHeartRate": "2026-03-28T07:47:08Z",
  "HKQuantityTypeIdentifierHeartRateVariabilitySDNN": "2026-03-28T07:47:08Z",
  "HKQuantityTypeIdentifierStepCount": "2026-03-28T07:47:08Z",
  "HKQuantityTypeIdentifierActiveEnergyBurned": "2026-03-28T07:47:08Z",
  "HKQuantityTypeIdentifierDistanceWalkingRunning": "2026-03-28T07:47:08Z",
  "HKQuantityTypeIdentifierBodyMass": "2026-03-28T07:47:08Z",
  "HKQuantityTypeIdentifierBloodGlucose": "2026-03-28T07:47:08Z",
  "HKCategoryTypeIdentifierSleepAnalysis": "2026-03-28T07:47:08Z",
  "..."
}
```

The `{deviceUUID}` is the iOS device identifier (same as `X-Client-Device-Id` header). The full list includes ~40 HealthKit types covering exercise, vitals, body measurements, cycling, swimming, and sleep.

### Push Health Data

```
POST https://app-api.8slp.net/v1/users/{userId}/health-integrations/sources/apple-health-{deviceUUID}
```

Body — batched HealthKit data points keyed by type:
```json
{
  "metrics": {
    "HKQuantityTypeIdentifierHeartRateVariabilitySDNN": {
      "value": [
        {
          "value": 42.94,
          "source": {
            "version": "26.3",
            "bundleIdentifier": "com.apple.health.0CC40EF5-...",
            "systemVersion": "26.3.0",
            "sourceName": "Apple Watch"
          },
          "unit": "ms",
          "startDate": "2026-03-28T18:59:49Z",
          "endDate": "2026-03-28T19:00:48Z"
        },
        "..."
      ],
      "checkpoint": "2026-03-29T02:54:10Z"
    },
    "HKQuantityTypeIdentifierSwimmingStrokeCount": {
      "value": [],
      "checkpoint": "2026-03-29T02:54:10Z"
    }
  }
}
```

Response: `{}` (empty on success).

Notes:
- The app sends ~10 sequential POSTs on each launch, batching metrics by type.
- Each metric includes a `checkpoint` timestamp that advances the sync cursor.
- Empty `value` arrays are sent for metric types with no new data (to advance the checkpoint).
- This is a one-way push — the app reads HealthKit locally and pushes to Eight Sleep. There is no pull/read endpoint for this data.
- In addition to HK type identifiers, the app also sends Apple Health profile data as standalone metric keys: `dateOfBirth` (ISO8601 string value), `biologicalSex` (`"male"`, `"female"`, etc.), `HKQuantityTypeIdentifierHeight`, `HKQuantityTypeIdentifierBodyMass`, `HKQuantityTypeIdentifierBodyFatPercentage`, `HKQuantityTypeIdentifierBodyMassIndex`. These are single-value metrics (not time series arrays).
- Android equivalent would use Health Connect (`enableHealthConnect` appears in release feature flags).

## Support Chat Auth

```
GET https://app-api.8slp.net/v1/users/{userId}/decagon-auth
```

Returns auth credentials for the in-app support chat (Decagon). Response not captured in detail — observed returning 200 during app launch.

## SMS Settings

```
GET https://app-api.8slp.net/v1/sms/users/{userId}
```

Returns 404 with empty string body (`""`). Possibly only populated if the user has enrolled in SMS notifications (the `smsEnrollment` release feature flag is `"show"`).
