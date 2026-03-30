# Household

Household management — device sets, user/device pairing, away mode, side assignment. Most endpoints live under `/household/` on `app-api` (side assignment uses a `/v2/users/` path that includes `/household/` as a segment).

For how multi-device households affect endpoint scoping across the API, see [Infrastructure > Multi-Device Households](infrastructure.md#multi-device-households).

## Contents

- [Get Household Summary](#get-household-summary)
- [Guest Management](#guest-management)
  - [Add Guests](#add-guests)
  - [Reclaim Device ("I'm Back")](#reclaim-device-im-back)
  - [Remove User from Household](#remove-user-from-household)
- [Invite User to Household](#invite-user-to-household)
- [Check Pending Invitations](#check-pending-invitations)
- [Accept Invitation](#accept-invitation)
- [Household Users List](#household-users-list)
- [Side Assignment](#side-assignment)
- [Add Device to Household](#add-device-to-household)
- [Remove Device from Household](#remove-device-from-household)
- [Remove User Assignment from Device](#remove-user-assignment-from-device)
- [Away Mode](#away-mode)
  - [Set Return Schedule](#set-return-schedule)
  - [Set Away](#set-away)
  - [End Away (Come Back)](#end-away-come-back)

## Get Household Summary

```
GET https://app-api.8slp.net/v1/household/users/{userId}/summary
```

The primary endpoint for household state. Returns device sets, user assignments, and away status. Other features depend on the IDs returned here (`householdId`, `setId`).

Response (when home):
```json
{
  "currentSet": "set-uuid-1",
  "households": [{
    "householdId": "...",
    "sets": [{
      "setId": "set-uuid-1",
      "setName": "Main Bedroom",
      "devices": [{
        "deviceId": "...",
        "specialization": "pod",
        "pairing": { "leftUserId": "...", "rightUserId": "..." },
        "assignment": { "leftUserId": "...", "rightUserId": "..." }
      }, "..."]
    }, "..."],
    "users": [{
      "userId": "...",
      "schedules": []
    }, "..."]
  }]
}
```

Response (when away):
```json
{
  "currentSet": "default",
  "previousSet": "set-uuid-1-...",
  "households": [{
    "sets": [{
      "devices": [{
        "pairing": {},
        "assignment": { "leftUserId": "...", "rightUserId": "..." }
      }, "..."]
    }, "..."],
    "users": [{
      "userId": "...",
      "schedules": [{
        "setId": "set-uuid-1-...",
        "dateToReturn": "2026-03-17T07:00:00Z"
      }]
    }, "..."]
  }]
}
```

Key differences when away: `currentSet` becomes `"default"`, `previousSet` appears, device `pairing` empties, user gains a `schedules` entry with the return date.

**`pairing` vs `assignment`:** Both contain `leftUserId`/`rightUserId` but have different semantics:

- **`pairing`** — who is **currently active** on each side. Changes when a user moves via `current-set` or when a guest is added. Matches the device endpoint's `leftUserId`/`rightUserId`.
- **`assignment`** — the **permanent/home base** user for each side. Does NOT change when a user moves to another device via `current-set` — the assignment persists, and the app shows the user as "Away" on that device. Only changes through explicit assignment operations (guest creation, or `DELETE .../assignment/users/{userId}`).
- **`awaySides`** (on the device endpoint) — mirrors `assignment`. Shows the permanent users for each side regardless of whether they're currently active.

Example: If User A is assigned to Pod 4 right side, then moves to Pod 2 via `current-set`:
- Pod 4 `pairing.rightUserId` changes (User A is replaced or the remaining user goes solo)
- Pod 4 `assignment.rightUserId` still shows User A (their "home base")
- The app displays User A as "Away" on Pod 4

## Guest Management

Create and remove ephemeral guest accounts for shared pods.

### Add Guests

```
POST https://app-api.8slp.net/v1/household/households/{householdId}/sets/{setId}/guests
```

Body — one or two guests, each assigned to a side:
```json
{
  "guests": [
    { "name": "Guest Name", "side": "right" }
  ]
}
```

Can also assign both sides at once:
```json
{
  "guests": [
    { "name": "Left Guest", "side": "left" },
    { "name": "Right Guest", "side": "right" }
  ]
}
```

Response:
```json
{
  "set": {
    "setId": "setId",
    "friendlyName": "Guest Bedroom",
    "devices": [
      {
        "deviceId": "deviceId",
        "specialization": "pod",
        "timezone": "America/Los_Angeles",
        "leftUserId": "primaryUserId",
        "rightUserId": "newGuestUserId"
      }
    ]
  }
}
```

Notes:
- Each guest gets a new, server-generated user ID — a real user account with its own alarms, temperature settings, autopilot config, sleep data, and even a WebSocket events connection.
- Adding a new guest on a side that already has one replaces the previous guest.
- Adding guests to both sides bumps the primary user off — the device's `leftUserId` and `rightUserId` both change to the new guest IDs.
- `side` values: `"left"`, `"right"`, `"solo"` (assigns both sides to the guest).
- The `householdId` and `setId` come from the [Household Summary](#get-household-summary).
- While in guest mode, the app maintains dual-user context — polling endpoints for both the owner and the guest, and opening separate WebSocket connections for each.
- All mutations (temperature, alarms, schedules, autopilot) use the guest's user ID. The guest has full control of the pod.

### Reclaim Device ("I'm Back")

To end guest mode and reclaim the device, the primary user reassigns themselves:

```
PUT https://app-api.8slp.net/v1/household/users/{primaryUserId}/current-set
```

Body:
```json
{
  "side": "solo",
  "setId": "setId"
}
```

This implicitly removes the guest — no separate DELETE is needed. The device's `leftUserId`/`rightUserId` revert to the primary user.

### Remove User from Household

```
DELETE https://app-api.8slp.net/v1/household/households/{householdId}/users/{userId}
```

No request body. Removes a user (typically a guest) from the household.

Response — remaining household members:
```json
[
  {
    "householdId": "householdId",
    "userId": "primaryUserId",
    "role": "PRIMARY",
    "invited": false
  }
]
```

Notes:
- After removal, the user ID is no longer valid in the household context.
- Attempting to reassign a removed user via `PUT .../current-set` returns an error: `"Household user {userId} not found in household {householdId}"`.

## Invite User to Household

```
POST https://app-api.8slp.net/v1/household/households/{householdId}/users
```

Body:
```json
{
  "user": {
    "role": "PRIMARY",
    "email": "invitee@email.com"
  }
}
```

Response:
```json
{
  "user": {
    "householdId": "householdId",
    "userId": "newOrExistingUserId",
    "role": "PRIMARY",
    "invited": true,
    "token": "invitation-token-uuid",
    "invitedBy": "Inviter Name (inviter@email.com)",
    "email": "invitee@email.com"
  }
}
```

Notes:
- Works the same whether the email belongs to an existing Eight Sleep account or a new user.
- A user ID is created/returned immediately, before the invitee accepts. **For existing accounts, the `userId` in the response is their real user ID.**
- **Existing account**: the invitation appears in the invitee's `/invitations` endpoint. They remain in their current household until they accept.
- **New account**: a user is created in a `"default"` household with `status: "INVITED"`. The invitee receives an email with a link to create an account and accept.
- Re-inviting a user can return **409** with `"User has already declined invite"`, and accepting can return **409** with `"Invitation already processed"`. Both were observed for a new user who created their account from the invite link but never completed the household join — leaving them in an orphaned state with no way back in. The conditions that trigger this are not fully understood (see also the `invited` field inconsistency noted under [Household Users List](#household-users-list)).

## Check Pending Invitations

```
GET https://app-api.8slp.net/v1/household/users/{userId}/invitations
```

Returns invitations **to** the authenticated user, not invitations **from** them. Only works with the caller's own user ID (403 for other user IDs).

Response (when the user has a pending invitation):
```json
{
  "invitations": [
    {
      "householdId": "invitingHouseholdId",
      "userId": "thisUserId",
      "role": "PRIMARY",
      "invited": true,
      "token": "invitation-token-uuid",
      "invitedBy": "Inviter Name (inviter@email.com)",
      "email": "thisUser@email.com"
    },
    "..."
  ]
}
```

Response (no pending invitations):
```json
{
  "invitations": []
}
```

Notes:
- To see who you've invited, use `GET .../households/{householdId}/users` and filter for `invited: true`.
- The app checks this endpoint on launch/foreground — if an invitation is pending, it shows a modal automatically.

## Accept Invitation

```
POST https://app-api.8slp.net/v1/household/households/{householdId}/users/{userId}
```

Body:
```json
{
  "invitation": {
    "accept": true,
    "token": "invitation-token-uuid"
  }
}
```

Response:
```json
{
  "user": {
    "householdId": "householdId",
    "userId": "userId",
    "role": "PRIMARY",
    "invited": false
  }
}
```

Notes:
- The `householdId` and `token` come from the invitation object in `/invitations`.
- After accepting, the user appears in the household summary's `users[]` with `status: "ACCEPTED"`.
- The user's `currentSet` becomes `"default"` — they are in the household but not assigned to any device. They need to be assigned via `PUT .../current-set`.
- A deviceless household member can see all sets, devices, and other members in the summary, and can read other members' user profiles within the same household.
- User-scoped endpoints (temperature, alarms, etc.) return empty/default data when the user has no device assignment — `temperature/all` returns `devices: []`, alarms returns just the `recommendedAlarm` template, base returns 404.

## Household Users List

```
GET https://app-api.8slp.net/v1/household/households/{householdId}/users
```

Returns ALL members of the household, including pending invitations. More complete than the household summary's `users[]` which only shows accepted members.

Response:
```json
[
  {
    "householdId": "householdId",
    "userId": "acceptedUserId",
    "role": "PRIMARY",
    "invited": false
  },
  {
    "householdId": "householdId",
    "userId": "invitedUserId",
    "role": "PRIMARY",
    "invited": true,
    "token": "invitation-token-uuid",
    "invitedBy": "Inviter Name (inviter@email.com)",
    "email": "invitee@email.com"
  },
  "..."
]
```

Notes:
- `invited: true` with `token`/`invitedBy`/`email` fields indicates a pending invitation for an existing Eight Sleep account.
- `invited: false` does NOT reliably indicate an accepted member. In testing, a newly invited user (with no existing account) showed `invited: false` immediately after the invite, before any action was taken — while their own household summary still showed `status: "INVITED"`. The meaning of this field is inconsistent.
- To reliably determine household membership, use the household summary's `users[]` (only shows accepted members) or the user's own household summary `status` field (`"ACCEPTED"` vs `"INVITED"`).
- `invitedBy` includes the inviter's full name and email.

## Side Assignment

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

The `setId` comes from the household summary response above.

## Add Device to Household

```
POST https://app-api.8slp.net/v1/household/households/{householdId}/devices
```

Body:
```json
{
  "device": {
    "friendlyName": "Guest Bedroom",
    "deviceId": "deviceId"
  }
}
```

Response:
```json
{
  "householdId": "householdId",
  "deviceId": "deviceId",
  "friendlyName": "Guest Bedroom",
  "setId": "new-set-id"
}
```

Notes:
- The device gets its own new **set** within the household. Multi-device households have one set per device.
- After adding, use `PUT .../current-set` to assign a user to the new device's set.
- This is likely also triggered during initial device setup (onboarding) when the user names the device.

## Remove Device from Household

```
DELETE https://app-api.8slp.net/v1/household/devices/{deviceId}
```

No request body. Removes the device from its current household entirely. Response: empty 200.

After removal, the device has no household association. It can be re-added to the same or a different household via `POST .../households/{householdId}/devices`.

## Remove User Assignment from Device

```
DELETE https://app-api.8slp.net/v1/household/devices/{deviceId}/assignment/users/{userId}
```

No request body. Response: empty 200.

Fully severs a user's relationship with a device — removes them from `assignment`, `awaySides`, and `pairing`. This is a "clean break" as opposed to `PUT .../current-set` which only changes the active location while leaving the assignment behind.

Effects:
- Removes the user from the device's `assignment` (permanent record)
- Removes them from `awaySides`
- If they were actively paired, removes them from `pairing` and device `leftUserId`/`rightUserId`
- If the remaining user was sharing the device, they become solo on both sides
- The removed user becomes deviceless (`currentDevice: null`, `devices: []`)
- **If the user has no remaining assignment on any device in the household, they are removed from the household entirely** — ejected to the `"default"` household with `status: "INVITED"` and no way to rejoin (no pending invitation). This is a destructive, potentially unintended side effect.
- Can cascade: removing a user's assignment may also bump other users who were actively paired on that side via `current-set` but whose permanent assignment was elsewhere

## Away Mode

The app no longer uses the legacy `PUT /v1/users/{userId}/away-mode` endpoint. Instead, away mode works by detaching the user from their household "set" (device group).

### Set Return Schedule

```
POST https://app-api.8slp.net/v1/household/users/{userId}/schedule
```

Body:
```json
{
  "schedule": {
    "setId": "setId",
    "dateToReturn": "2026-03-30T07:00:00Z"
  },
  "includePartner": false
}
```

Response: empty 200.

Notes:
- Creates the return-date schedule entry that appears in the household summary when a user is away.
- `includePartner`: whether to also set the partner as away. Observed value `false`.

### Set Away

```
DELETE https://app-api.8slp.net/v1/household/users/{userId}/current-set
```

- No request body (`Content-Length: 0`)
- Return date can be set via the [Set Return Schedule](#set-return-schedule) endpoint above, or via custom headers on this request: `X-8S-Return-Date: 2026-03-17T07:00:00Z` and `X-8S-Include-Partner: false`.
- Response: `{}`

### End Away (Come Back)

Two simultaneous requests:

```
PUT https://app-api.8slp.net/v1/household/users/{userId}/current-set
```

Body:
```json
{
  "setId": "set-uuid-1",
  "side": "solo"
}
```

Response:
```json
{
  "setId": "set-uuid-1-...",
  "devices": [{
    "deviceId": "...",
    "specialization": "pod",
    "side": "solo",
    "timezone": "America/Los_Angeles"
  }, "..."]
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
