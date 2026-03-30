# Infrastructure

## Contents

- [Authentication](#authentication)
  - [Password Login](#password-login)
  - [Token Refresh](#token-refresh)
- [Multi-Device Households](#multi-device-households)
  - [Endpoint scoping](#endpoint-scoping)
  - [Shared pod (left/right) behavior](#shared-pod-leftright-behavior)
  - [User profile](#user-profile)
  - [App polling behavior](#app-polling-behavior)
- [Base URLs](#base-urls)
- [App Launch Sequence](#app-launch-sequence)

## Authentication

Same endpoint for both password login and token refresh:

```
POST https://auth-api.8slp.net/v1/tokens
```

### Password Login

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

Response:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 72000,
  "refresh_token": "eyJ...",
  "userId": "hex-string"
}
```

### Token Refresh

Body:
```json
{
  "client_id": "0894c7f33bb94800a03f1f4df13a4f38",
  "client_secret": "f0954a3ed5763ba3d06834c73731a32f15f168f47d4f164751275def86db0c76",
  "grant_type": "refresh_token",
  "refresh_token": "<refresh_token from prior auth>"
}
```

Response:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 72000,
  "refresh_token": "eyJ..."
}
```

Notes:
- `userId` is only present in the password login response, not the refresh response.
- Both tokens are JWTs. The `userId` can be extracted from the `sub` claim in the access token JWT payload.
- `expires_in` is 72000 seconds (20 hours). The iOS app uses token refresh on cold start when it has a stored refresh token from a prior session, and password grant on fresh login.
- The refresh response includes a new `refresh_token`, but the old refresh token is **not invalidated** — it can be used again to generate additional tokens. Multiple refresh tokens and access tokens can be valid simultaneously.
- Use `Authorization: Bearer <access_token>` on all subsequent requests.
- There is no logout/token-revocation endpoint. Tokens are stateless JWTs — valid until their `exp` claim regardless of logout or new logins. Multiple tokens can be valid simultaneously. The app discards the token client-side and deregisters push notifications (see [App Client > Push Targets](app_client.md#deregister-push-token-on-logout)). Confirmed by testing: logging out, issuing a new token, and verifying the old token still works.

## Multi-Device Households

A household can contain multiple devices, each in its own **set** (e.g. "Main Bedroom", "Guest Bedroom"). Users are assigned to one set at a time via `PUT .../current-set` (see [Household](household.md)). This assignment determines which device user-scoped endpoints operate on.

### Endpoint scoping

| Scoping | Endpoints | Behavior |
|---------|-----------|----------|
| **User + side** | `temperature/all`, `temperature/pod`, `alarms`, `autopilotDetails`, `hot-flash-mode`, `bedtime`, `tap-settings` (PUT) | Only shows/modifies this user's side of their assigned device. Two users sharing a pod see independent data. |
| **Device (both sides)** | `base`, `devices/{deviceId}` | Shows both left and right sides. Base angles are per-side but visible to both users. The device endpoint shows both `leftKelvin`/`rightKelvin`. |
| **All devices in household** | `tap-settings` (GET), `maintenance_insert`, `release-features` | Returns data for every device in the household. Tap settings GET shows per-user config for each device. |
| **Explicit device ID** | `devices/{deviceId}/priming/tasks`, `devices/{deviceId}/priming/schedule` | Requires the caller to specify which device |
| **Historical (all ever used)** | `temperature/all` → `temperatureSettings[]` | Includes smart level history for devices the user is no longer assigned to |

### Shared pod (left/right) behavior

When two users share a pod (one on left, one on right):
- `currentDevice.side` on each user's profile reflects their side (`"left"` or `"right"`)
- `temperature/all` returns only the user's own side — each user sees their own `currentLevel`, `currentState`, and `smart` levels independently
- `temperature/pod` mutations only affect the user's assigned side — both sides can be active simultaneously at different temperatures
- **Alarms** are fully per-user — each user has their own alarm set, invisible to the other. Alarms follow the user when moving between devices.
- **Autopilot**, **hot flash**, and **tap settings** are per-user — follow the user across devices. Each side of the bed responds to its assigned user's config. Confirmed: changing one user's alarm tap action does not affect the other's.
- **Smart temperature levels** are the exception — they are **per-user-per-device**. Each user has a history of levels for each device they've used (visible in `temperatureSettings[]`). Moving to a different device loads the last levels used on *that specific device*, not the levels from the previous device.
- **Base** state is visible to both users (physical base moves as one unit)
- The device endpoint (`GET /v1/devices/{deviceId}`) is the only place that shows both sides' temperature state (`leftKelvin`/`rightKelvin`)

### User profile

- `currentDevice` reflects the user's `currentSet` assignment — always one device, with `side` indicating `"solo"`, `"left"`, or `"right"`.
- `devices` array does NOT include all owned devices — only the one in `currentSet`.
- A user with no device assignment has `currentDevice: null` and `devices: []`.
- The [Household Summary](household.md#get-household-summary) is the only endpoint that shows all devices and their set assignments.

### App polling behavior

The app polls endpoints for **all users across all sets** in the household simultaneously. In a two-device household with User A on Pod 4 and User B on Pod 2 Pro, the app polls both users' alarms, temperature, and hot flash endpoints, plus both devices' priming tasks and device info.

## Base URLs

- **auth-api**: `https://auth-api.8slp.net/v1` — authentication only
- **client-api**: `https://client-api.8slp.net/v1` — user profiles, device info, sleep data
- **app-api**: `https://app-api.8slp.net` — temperature, alarms, base, features (v1 and v2 paths)

## App Launch Sequence

On cold start, the app fires ~70 requests in ~2 seconds. Key categories:

- **Polling**: `GET .../base` every ~15s at idle (rapid-polls several times/sec during base movement), `.../alarms` + `.../temperature/all` + `.../hot-flash-mode` + `.../priming/tasks` + `.../devices/{id}` every ~60s
- **User/Auth**: `GET /v1/users/me` (×2), `GET /v1/users/{userId}`, `PUT /v1/users/{userId}` (timezone/last-seen update)
- **Sleep data**: `.../intervals` (paginated), `.../trends` (×2 date ranges), `.../metrics/aggregate?metrics=sleep_debt`, `.../tags`, `.../truth-tags`
- **AI/Insights**: `.../llm-insights` (×3, one per day: today, yesterday, day before), `.../llm-insights/settings`, `.../bedtime/recommendation`
- **Content**: `.../audio/tracks?category=soundscapes`, `...=alarms`, `...=nsdr`, `.../audio/categories`
- **Apple Health**: `.../health-integrations/.../checkpoints`, then ~10 sequential POSTs syncing data
- **Security**: `POST .../devices/{id}/security/key` (×4)
- **WebSocket**: `GET .../events` (status 101) for real-time temperature state push (see [appendix](appendix.md#websocket-events))
