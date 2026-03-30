# Jet Lag Protocol (Beta)

Travel-based sleep protocol that adjusts sleep/wake times before and after flights to reduce jet lag. Only triggers when the timezone shift is large enough (a 2-hour shift was rejected as "no protocol needed"; a 3-hour shift triggered a full plan).

## Contents

- [Flight Lookup](#flight-lookup)
- [Create Trip](#create-trip)
- [Generate Plan](#generate-plan)
- [List Trips](#list-trips)
- [Get Plan Details](#get-plan-details)
- [Delete Trip (Soft Delete)](#delete-trip-soft-delete)

## Flight Lookup

```
GET https://app-api.8slp.net/v1/travel/flight-status?date=2026-04-20&flightNumber=ua1496
```

Response:
```json
{
  "legs": [{
    "departureAirport": "PDX",
    "departureAirportName": "PORTLAND INTL",
    "departureCity": "PORTLAND",
    "departureTimezone": "-07:00",
    "scheduledDepartureTime": "2026-04-20T14:00:00Z",
    "arrivalAirport": "ORD",
    "arrivalAirportName": "O HARE INTERNATIONAL",
    "arrivalCity": "CHICAGO",
    "arrivalTimezone": "-05:00",
    "scheduledArrivalTime": "2026-04-20T18:09:00Z",
    "aircraft": "738",
    "duration": "PT4H9M",
    "flightNumber": "1496",
    "carrierCode": "UA"
  }]
}
```

Notes:
- `flightNumber` param is lowercase carrier+number (e.g., `ua1496`)
- Each connecting flight is looked up separately
- No auth required beyond the standard Bearer token

## Create Trip

```
POST https://app-api.8slp.net/v1/users/{userId}/travel/trips
```

Body:
```json
{
  "legs": [
    {
      "legId": "client-generated-uuid",
      "origin": { "name": "PORTLAND", "timezone": "-07:00", "airportCode": "PDX" },
      "destination": { "name": "CHICAGO", "timezone": "-05:00", "airportCode": "ORD" },
      "departureTime": "2026-04-20T14:00:00.000000Z",
      "arrivalTime": "2026-04-20T18:09:00.000000Z"
    },
    "..."
  ]
}
```

Response:
```json
{
  "tripId": "uuid",
  "name": "PORTLAND to ASHEVILLE/HENDERSONV.",
  "status": "Planning",
  "timezoneShift": { "offset": 3, "direction": "Eastbound" },
  "totalFlightHours": 7,
  "totalFlightTime": "7h 13m",
  "legs": [{ "...leg with server-computed layoverDuration and flightTime..." }]
}
```

## Generate Plan

```
POST https://app-api.8slp.net/v1/users/{userId}/travel/trips/{tripId}/plans
```

Body:
```json
{
  "supplementsEnabled": false
}
```

Response:
```json
{
  "planId": "uuid",
  "direction": "Eastbound",
  "status": "Ready",
  "startDate": "2026-04-18",
  "endDate": "2026-04-25",
  "supplementsEnabled": false,
  "stayingLongerThanThreeDays": false,
  "timezoneShift": { "offset": 3, "direction": "Eastbound" },
  "tasks": [
    {
      "taskId": "uuid",
      "name": "Wake up",
      "type": "WakeUp",
      "scheduledAt": "2026-04-18T14:30:00Z",
      "timezoneId": "-07:00",
      "instructions": "7:00-8:00 AM",
      "status": "Pending",
      "phase": "PreFlight",
      "metadata": {}
    },
    "..."
  ],
  "groupedTasks": [
    {
      "phase": "PreFlight",
      "date": "2026-04-18",
      "timezoneId": "-07:00",
      "tasks": ["...same task objects..."]
    },
    "..."
  ],
  "summary": {
    "totalDays": 5,
    "completedTasks": 0,
    "totalTasks": 13,
    "nextTaskDate": "2026-04-18",
    "isActive": false,
    "progress": 0
  }
}
```

Notes:
- Task types: `WakeUp`, `Sleep`, `Exercise`, `Nap`
- Phases: `PreFlight` (origin timezone), `PostFlight` (destination timezone)
- Plan starts 2 days before flight, continues ~2 days after arrival
- `supplementsEnabled` toggles supplement recommendations (melatonin, etc.)
- `stayingLongerThanThreeDays` — unclear if this affects plan generation (was `false` in test)

## List Trips

```
GET https://app-api.8slp.net/v1/users/{userId}/travel/trips
```

Returns array of trip objects with embedded plan summaries (no task details).

## Get Plan Details

```
GET https://app-api.8slp.net/v1/users/{userId}/travel/trips/{tripId}/plans
```

Returns array of full plan objects with all tasks.

## Delete Trip (Soft Delete)

```
PUT https://app-api.8slp.net/v1/users/{userId}/travel/trips/{tripId}
```

Body:
```json
{
  "status": "Completed",
  "name": "PORTLAND to ASHEVILLE/HENDERSONV."
}
```

Sets trip status to `"Completed"` rather than hard-deleting. Response returns the full trip object with updated status.
