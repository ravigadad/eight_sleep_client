# Device

## Contents

- [Get Device](#get-device)
- [Tap Gesture Settings](#tap-gesture-settings)
- [LED Brightness](#led-brightness)
- [Priming](#priming)
  - [Get Priming Task History](#get-priming-task-history)
  - [Trigger Manual Priming](#trigger-manual-priming)
  - [Get Priming Schedule](#get-priming-schedule)
  - [Update Priming Schedule](#update-priming-schedule)
- [Maintenance Insert Status](#maintenance-insert-status)
  - [Insert Address Management (Web API)](#insert-address-management-web-api)
- [Set Device Owner](#set-device-owner)

## Get Device

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
    "sensors": [ { "...same fields as sensorInfo..." }, "..." ],
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
        },
        "..."
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

## Tap Gesture Settings

```
GET https://app-api.8slp.net/v1/users/{userId}/devices/all/tap-settings
PUT https://app-api.8slp.net/v1/users/{userId}/devices/{deviceId}/tap-settings
```

**Important:** This endpoint returns data for all devices regardless of whether they have tap hardware. Tap sensors were introduced with Pod 4 — check the `features` array for `"tapControls"` to determine if the device actually supports tapping. See [Device Compatibility](device_compatibility.md) for details.

### GET Response

Returns available options per gesture type with current selections:

```json
{
  "settings": {
    "{deviceId}": {
      "alarm": {
        "options": [
          { "tapType": "double-tap", "action": "dismiss" },
          { "tapType": "double-tap", "action": "snooze" },
          { "tapType": "double-tap", "action": "none" }
        ],
        "currentDoubleTap": { "tapType": "double-tap", "action": "dismiss" }
      },
      "generic": {
        "options": [
          { "tapType": "double-tap", "action": "temperature-control" }
        ],
        "currentDoubleTap": { "tapType": "double-tap", "action": "temperature-control" }
      },
      "quadTap": {
        "options": [
          { "tapType": "quadruple-tap", "action": "adjust-base" },
          { "tapType": "quadruple-tap", "action": "adjust-audio" },
          { "tapType": "quadruple-tap", "action": "hot-flash-mode" }
        ],
        "currentQuadTap": { "tapType": "quadruple-tap", "action": "adjust-base" }
      }
    }
  }
}
```

Notes:
- `alarm` — double-tap action during an active alarm. Actions: `"dismiss"`, `"snooze"`, `"none"`.
- `generic` — double-tap action when no alarm is active. Action: `"temperature-control"`.
- `quadTap` — quadruple-tap action. Actions: `"adjust-base"`, `"adjust-audio"`, `"hot-flash-mode"`.
- Each section includes `options` (available choices) and the `current*` selection.
- Confirmed identical response for Pod 4 (has tap hardware) and Pod 2 Pro (no tap hardware) — the server does not filter by device capability.

### PUT Request

The PUT body contains a single gesture key with its updated configuration:

**Alarm tap action** (double-tap on bed):
```json
{
  "alarm": {
    "action": "snooze",
    "tapType": "double-tap"
  }
}
```

**Quad-tap action**:
```json
{
  "quadTap": {
    "action": "hot-flash-mode",
    "tapType": "quadruple-tap"
  }
}
```

Each PUT sends only the gesture being changed — you don't need to send the full settings object.

## LED Brightness

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

`ledBrightnessLevel` range: `0` (off) to `100`. The app may rate-limit rapid successive changes.

## Priming

All priming endpoints are on `app-api` (not `client-api`), except for the schedule update which uses `client-api`.

### Get Priming Task History

```
GET https://app-api.8slp.net/v1/devices/{deviceId}/priming/tasks
```

Returns the full history of priming tasks (both scheduled daily maintenance and manual). Polled by the app every ~60s.

Response (showing an in-progress task followed by a completed task):
```json
{
  "tasks": [
    {
      "reason": "requested",
      "created": "2026-03-30T00:02:45Z",
      "status": "starting",
      "notifications": {
        "users": ["userId"],
        "meta": "fill_pod_maintenance"
      }
    },
    {
      "reason": "scheduled",
      "created": "2026-03-29T21:09:19Z",
      "started": "2026-03-29T21:10:02Z",
      "finished": "2026-03-29T21:20:51Z",
      "outcome": "succeeded",
      "status": "finished",
      "notifications": {
        "users": ["userId"]
      },
      "coverInfo": {
        "label": "20600-0001-I12-B07001BA"
      }
    },
    "..."
  ]
}
```

Notes:
- `reason`: `"scheduled"` (daily maintenance) or `"requested"` (manual trigger).
- `status` progression: `"starting"` (created, pod not yet pumping) → `"started"` (actively pumping, `started` timestamp and `coverInfo` appear) → `"finished"` (`finished`, `outcome` added).
- Transition from `starting` to `started` takes ~30 seconds. Transition from `started` to `finished` takes ~11 minutes.
- `outcome` (on finished tasks): `"succeeded"`, `"expired"`, or `"out-of-water"`.
- `notifications.meta`: `"fill_pod_maintenance"` observed on both manual and scheduled tasks. Absent on older tasks.
- `coverInfo.label` — the pod cover's serial/part number. Present once status reaches `"started"`.
- History goes back to device setup (354 tasks spanning ~2 years observed). No pagination — the full history is returned.
- The app shows a countdown timer during priming, but the API provides no estimated duration or remaining time — the countdown is computed client-side (priming consistently takes ~11 minutes).

### Trigger Manual Priming

```
POST https://app-api.8slp.net/v1/devices/{deviceId}/priming/tasks
```

Body:
```json
{
  "notifications": {
    "meta": "fill_pod_maintenance",
    "users": ["userId"]
  }
}
```

Response:
```json
{
  "task": {
    "reason": "requested",
    "created": "2026-03-30T00:02:45Z",
    "status": "starting",
    "notifications": {
      "users": ["userId"],
      "meta": "fill_pod_maintenance"
    }
  }
}
```

The app immediately polls `GET .../priming/tasks` after triggering to track progress.

### Get Priming Schedule

```
GET https://app-api.8slp.net/v1/devices/{deviceId}/priming/schedule
```

Response:
```json
{
  "schedule": [
    "Monday 14:00",
    "Tuesday 14:00",
    "Wednesday 14:00",
    "Thursday 14:00",
    "Friday 14:00",
    "Saturday 14:00",
    "Sunday 14:00"
  ]
}
```

Human-readable daily maintenance schedule. This is the read side — the write side uses a different endpoint on `client-api` (see [Update Priming Schedule](#update-priming-schedule) below).

### Update Priming Schedule

Note: this endpoint uses a `/household/` path on `client-api` — the `householdId` and `setId` come from the [Household Summary](household.md#get-household-summary) response.

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

## Maintenance Insert Status

```
GET https://app-api.8slp.net/v1/user/{userId}/device_maintenance/maintenance_insert?v=2
```

Note: this endpoint uses `/user/` (singular), not `/users/` like every other endpoint.

Response (array — one entry per device):
```json
[
  {
    "deviceId": "deviceId",
    "deviceAddress": {
      "deviceId": "deviceId",
      "updateDate": "2026-01-28T02:18:50Z",
      "company": null,
      "firstName": "Jane",
      "lastName": "Doe",
      "address1": "123 Main St",
      "address2": "",
      "city": "Portland",
      "countryCode": "US",
      "province": "OR",
      "postalCode": "97201",
      "createdAt": "2026-01-28T02:18:50Z",
      "updatedAt": "2026-01-28T02:18:50Z",
      "deletedAt": null,
      "confirmedDate": "2026-01-28T02:18:50Z",
      "confirmedByUserId": null
    },
    "previousInsertReplacement": {
      "deviceId": "deviceId",
      "replacementDate": "2026-02-03",
      "maintenanceInsertOrderDate": "2026-02-03T17:12:50Z",
      "invoiceNumber": "2GTIKVOO-0001",
      "invoicePaymentUrl": null,
      "shippingAddress": "Jane Doe, 123 Main St, Portland, OR, 97201, US",
      "createdDate": "2026-01-06T03:43:11Z",
      "updatedDate": "2026-02-03T17:12:50Z",
      "deletedDate": null,
      "reminderEmailSentDate": "2026-01-27T16:55:13Z",
      "paymentReviewedDate": null
    },
    "nextInsertReplacement": {
      "deviceId": "deviceId",
      "replacementDate": "2026-08-03",
      "maintenanceInsertOrderDate": null,
      "invoiceNumber": null,
      "invoicePaymentUrl": null,
      "shippingAddress": null,
      "createdDate": "2026-02-03T17:12:47Z",
      "updatedDate": "2026-02-03T17:12:47Z",
      "deletedDate": null,
      "reminderEmailSentDate": null,
      "paymentReviewedDate": null
    }
  },
  "..."
]
```

Notes:
- Tracks the periodic water filter/insert replacement cycle.
- `deviceAddress` — shipping address on file for replacement inserts.
- `previousInsertReplacement` — the last completed replacement with order date, invoice, and shipping info.
- `nextInsertReplacement` — the upcoming replacement. `replacementDate` is the scheduled date (~6 months after previous). Fields like `maintenanceInsertOrderDate` and `invoiceNumber` are `null` until the replacement is ordered.
- `reminderEmailSentDate` — when Eight Sleep emailed the reminder to order.
- `invoicePaymentUrl` — presumably a link to pay for the replacement insert (null in our observations, possibly populated for accounts that haven't paid yet).
- Fetched on app launch.

### Insert Address Management (Web API)

The insert shipping address is managed through a webview that opens `www.eightsleep.com/insert-management/{deviceId}/`. The webview passes the same Bearer token via query params (`token`, `jwt`, `authToken` — all identical). These endpoints accept the same auth token as the `app-api`/`client-api` endpoints.

The address update flow:

**1. Read current address:**
```
GET https://www.eightsleep.com/api/insert-management/device-address/?deviceId={deviceId}
```

Response:
```json
{
  "success": true,
  "data": {
    "deviceId": "deviceId",
    "firstName": "Jane",
    "lastName": "Doe",
    "address1": "123 Main St",
    "address2": "",
    "city": "Portland",
    "countryCode": "US",
    "province": "OR",
    "postalCode": "97201",
    "company": null,
    "updateDate": "ISO8601",
    "createdAt": "ISO8601",
    "updatedAt": "ISO8601",
    "deletedAt": null,
    "confirmedDate": "ISO8601",
    "confirmedByUserId": null
  }
}
```

**2. Validate new address:**
```
POST https://www.eightsleep.com/api/shipping/address_verification/
```

Body:
```json
{
  "address": {
    "address": {
      "line1": "123 Main St",
      "line2": "",
      "city": "Portland",
      "state": "OR",
      "postal_code": "97201",
      "country": "US"
    }
  }
}
```

Response includes a Google Address Validation verdict with `possibleNextAction: "ACCEPT"` and a `formattedAddress`.

**3. Save address:**
```
PUT https://www.eightsleep.com/api/insert-management/device-address/?deviceId={deviceId}
```

Body:
```json
{
  "firstName": "Jane",
  "lastName": "Doe",
  "address1": "123 Main St",
  "city": "Portland",
  "province": "OR",
  "postalCode": "97201",
  "countryCode": "US"
}
```

Response: same shape as the GET, with updated timestamps.

**4. Confirm address:**
```
POST https://www.eightsleep.com/api/insert-management/device-address/confirm/?deviceId={deviceId}
```

Body: identical to the PUT body. Response: `{"success": true}`.

**5. Re-read to verify** — same GET as step 1.

Notes:
- The PUT saves the address and the confirm POST is an explicit "yes I'm sure" step.
- These are on `www.eightsleep.com` (Vercel/Next.js), not `app-api` or `client-api`.
- The webview also hits `/api/user/devices/` (returns household/device info, subset of what `client-api` provides) and `/api/user/member-shop-eligibility/`.

## Set Device Owner

```
PUT https://client-api.8slp.net/v1/devices/{deviceId}/owner
```

Provisions a device to a user account. Used during initial setup and when transferring a device to a new owner.

Body:
```json
{
  "ownerId": "userId",
  "timezone": "America/Los_Angeles"
}
```

Response:
```json
{
  "message": "Device successfully updated.",
  "device": {
    "deviceId": "deviceId",
    "timeZone": "America/Los_Angeles",
    "specialization": "pod",
    "deviceMetaData": { "awayUsers": [] },
    "timezone": "America/Los_Angeles"
  }
}
```

Notes:
- Sets the `ownerId` field on the device. This is separate from household membership and side assignment.
- After setting the owner, the device still needs to be added to a household (`POST .../households/{householdId}/devices`) and the user needs to be assigned to it (`PUT .../current-set`).
- There is no single "transfer device" API — transferring involves removing the device from the old household, setting the new owner, and adding to the new household as separate steps.
