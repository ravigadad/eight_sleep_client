# Sleep Analytics

Computed/derived/logged data produced by the pod and Eight Sleep's analysis pipeline. All read-only — the user never writes to these endpoints.

## Contents

- [Sleep Intervals](#sleep-intervals)
- [Trends](#trends)
- [Aggregated Metrics](#aggregated-metrics)
- [Metrics Summary](#metrics-summary)
- [Bedtime Recommendation](#bedtime-recommendation)
- [Tags](#tags)
  - [Read Tags](#read-tags)
  - [Update Tags](#update-tags)
- [Truth Tags](#truth-tags)
- [Edit Sleep Interval](#edit-sleep-interval)
- [Feedback](#feedback)
- [Insights](#insights)
- [LLM Insights](#llm-insights)
- [Challenges](#challenges)
- [Days Count](#days-count)

## Sleep Intervals

```
GET https://client-api.8slp.net/v1/users/{userId}/intervals
```

Paginated via `?next=` cursor. Each page returns up to ~10 intervals (sleep sessions).

Response (showing one interval per page — each page returns up to ~10):
```json
{
  "next": "eyJ2IjoiMSIsImxhc3RFdmVudFRzIjoiMjAyNi0wMy0xOVQwNzo1OTowMC4wMDBaIn0=",
  "intervals": [
    {
      "id": "1774679580",
      "deviceTimeAtUpdate": "2026-03-28T18:02:00.000Z",
      "ts": "2026-03-28T07:41:00.000Z",
      "sleepStart": "2026-03-28T07:53:00.000Z",
      "sleepEnd": "2026-03-28T17:59:00.000Z",
      "presenceEnd": "2026-03-28T18:00:00.000Z",
      "duration": 41370,
      "score": 0,
      "timezone": "America/Los_Angeles",
      "device": {
        "id": "deviceId",
        "side": "solo",
        "specialization": "pod"
      },
      "sleepAlgorithmVersion": "0.1.1",
      "presenceAlgorithmVersion": "3.2.1",
      "hrvAlgorithmVersion": "1.1.0",
      "stages": [
        { "stage": "awake", "duration": 720 },
        { "stage": "light", "duration": 330 },
        { "stage": "deep", "duration": 3000 },
        { "stage": "rem", "duration": 1230 },
        "..."
      ],
      "snoring": [
        { "intensity": "none", "duration": 7140 },
        { "intensity": "medium", "duration": 60 },
        { "intensity": "heavy", "duration": 300 },
        { "intensity": "light", "duration": 60 },
        "..."
      ],
      "stageSummary": {
        "totalDuration": 41370,
        "sleepDuration": 34530,
        "outDuration": 4230,
        "awakeDuration": 2610,
        "lightDuration": 19770,
        "deepDuration": 4890,
        "remDuration": 9870,
        "awakeBeforeSleepDuration": 720,
        "awakeBetweenSleepDuration": 1830,
        "awakeAfterSleepDuration": 60,
        "outBetweenSleepDuration": 0,
        "wasoDuration": 1830,
        "deepPercentOfSleep": 0.14,
        "remPercentOfSleep": 0.29,
        "lightPercentOfSleep": 0.57
      },
      "timeseries": {
        "tnt": [["2026-03-28T08:47:00.000Z", 1], "..."],
        "tempRoomC": [["timestamp", value], "..."],
        "tempBedC": [["timestamp", value], "..."],
        "respiratoryRate": [["timestamp", value], "..."],
        "nemeanRespiratoryRate": [["timestamp", value], "..."],
        "nemeanRespiratoryRateNightly": [["timestamp", value], "..."],
        "heartRate": [["timestamp", value], "..."],
        "heating": [["timestamp", value], "..."],
        "hrv": [["timestamp", value], "..."],
        "rmssd": [["timestamp", value], "..."],
        "shortAwakes": [["timestamp", value], "..."]
      }
    },
    "..."
  ]
}
```

Notes:
- `stages` — sequential sleep stage segments. `stage` values: `"awake"`, `"light"`, `"deep"`, `"rem"`. `duration` in seconds.
- `snoring` — sequential snoring segments. `intensity` values: `"none"`, `"light"`, `"medium"`, `"heavy"`. `duration` in seconds.
- `timeseries` — per-metric time series arrays. Each entry is `[timestamp, value]`.
  - `tnt` — toss and turn events
  - `tempRoomC` / `tempBedC` — room and bed temperature in Celsius
  - `heartRate`, `hrv`, `rmssd` — heart rate metrics
  - `respiratoryRate`, `nemeanRespiratoryRate`, `nemeanRespiratoryRateNightly` — breathing rate (multiple algorithm versions)
  - `heating` — pod heating level over time
  - `shortAwakes` — brief awakenings
- `score` — observed as `0`, purpose unclear (possibly deprecated or not computed for all accounts)
- `next` — base64-encoded cursor for pagination. Pass as `?next=` to get the next page. Absent when no more pages.

## Trends

```
GET https://client-api.8slp.net/v1/users/{userId}/trends?from=2026-03-22&to=2026-03-28&tz=America/Los_Angeles&model-version=v3&consistent-read=false
```

Supports multi-day date ranges. Days with no sleep data are omitted from the response.

Query parameters:
- `from` / `to` — date range (inclusive). Multi-day spans work (tested up to 30 days, returned 27 days).
- `tz` — timezone for day boundaries.
- `model-version=v3` — observed value; other versions unknown.
- `include-all-sessions=true` — includes full interval objects (same shape as `/intervals`) in a `sessions` array per day. Without this, sessions are omitted and the response includes scoring and health fields instead.
- `include-main=false` — observed values `true`/`false`. Effect unclear.
- `consistent-read=false` — observed value; likely a database consistency hint.

### Compact response (without `include-all-sessions`)

This is the richer form — includes sleep scores, health metrics, performance windows, and hot flash data (showing one day from a multi-day query):

```json
{
  "days": [
    {
      "day": "2026-03-28",
      "presenceDuration": 41370,
      "sleepDuration": 34530,
      "remDuration": 9870,
      "remPercent": 0.29,
      "lightDuration": 19770,
      "deepDuration": 4890,
      "deepPercent": 0.14,
      "snoreDuration": 600,
      "heavySnoreDuration": 360,
      "snorePercent": 2,
      "heavySnorePercent": 1,
      "mitigationEvents": 0,
      "stoppedSnoringEvents": 0,
      "reducedSnoringEvents": 0,
      "ineffectiveExtendedEvents": 0,
      "cancelledEvents": 0,
      "elevationDuration": 0,
      "theoreticalSnorePercent": 2,
      "snoringReductionPercent": 0,
      "elevationAutopilotAdjustmentCount": 0,
      "presenceStart": "2026-03-28T07:41:00.000Z",
      "presenceEnd": "2026-03-28T18:00:00.000Z",
      "sleepStart": "2026-03-28T07:53:00.000Z",
      "sleepEnd": "2026-03-28T17:59:00.000Z",
      "tnt": 56,
      "mainSessionId": "1774679580",
      "sessionIds": ["1774679580", "..."],
      "incomplete": false,
      "tags": [],
      "score": 91,
      "sleepQualityScore": {
        "total": 94,
        "weight": 0.5,
        "weighted": 47,
        "sleepDurationSeconds": {
          "current": 34530, "average": 21983, "score": 100, "weight": 0.4,
          "lowerRange": 28800, "upperRange": 86400, "inclusive7DayAverage": 21853
        },
        "heartRate": {
          "current": 52, "average": 55.1, "score": 81, "weight": 0.1,
          "lowerRange": 52.9, "upperRange": 57.3, "inclusive7DayAverage": 55.4
        },
        "hrv": {
          "current": 28.6, "average": 22.1, "score": 0, "weight": 0,
          "lowerRange": 19.9, "upperRange": 24.3
        },
        "respiratoryRate": {
          "current": 12, "average": 12.5, "score": 0, "weight": 0,
          "lowerRange": 11, "upperRange": 14
        },
        "deep": { "current": 4890, "average": 4658, "score": 78, "weight": 0.06 },
        "rem": { "current": 9870, "average": 6992, "score": 105, "weight": 0.19 },
        "waso": { "current": 0.05, "average": 0, "score": 95, "weight": 0.15 },
        "sleepDebt": {
          "dailySleepDebtSeconds": -11839,
          "baselineSleepDurationSeconds": 22691,
          "isCalibrating": false
        }
      },
      "sleepRoutineScore": {
        "total": 44,
        "weight": 0.1,
        "weighted": 4,
        "wakeupConsistency": { "current": "10:59:00", "average": "08:29:57", "score": 20 },
        "sleepStartConsistency": { "current": "00:53:00", "average": "02:04:47", "score": 68 },
        "bedtimeConsistency": { "current": "00:41:00", "average": "01:39:27", "score": 75 },
        "latencyAsleepSeconds": { "current": 720, "average": 1399, "score": 0 },
        "latencyOutSeconds": { "current": 60, "average": 1354, "score": 0 }
      },
      "avgSleepFitnessScore": 76.38,
      "avgSleepQualityScore": 82.38,
      "avgSleepRoutineScore": 73.88,
      "health": {
        "breathing": {
          "value": 0.4, "rating": "inRange",
          "timeseries": [["2026-03-28T13:50:00Z", 1], "..."],
          "ranges": { "inRange": { "min": 0, "max": 14 }, "outOfRange": { "min": 14 } }
        },
        "heartbeat": {
          "value": 0, "rating": "inRange",
          "timeseries": [["2026-03-28T08:00:00.000Z", 0], "..."],
          "ranges": { "inRange": { "min": 0, "max": 3 }, "outOfRange": { "min": 3 } }
        },
        "wellbeing": {
          "value": 0, "rating": "inRange",
          "abnormalities": {
            "hr": { "value": 52, "isAbnormal": false, "probability": 0.19, "dayOfWeekAverage": 53.85 },
            "hrv": { "value": 28.58, "isAbnormal": false, "probability": 0.14, "dayOfWeekAverage": 24.21 },
            "rr": { "value": 12.05, "isAbnormal": false, "probability": 0.22, "dayOfWeekAverage": 12.36 }
          },
          "dayCount": 62,
          "daysUntilAvailable": 0,
          "daysUntilCalibrated": 0
        }
      },
      "hotFlash": {
        "summary": { "sessionCount": 0 },
        "sessions": []
      },
      "performanceWindows": {
        "isAvailable": true,
        "performanceWindowStats": {
          "currentSleepStart": "00:53:00",
          "currentSleepMidpoint": "05:56:00",
          "currentSleepEnd": "10:59:00",
          "sleepStartBaseline": "02:07:48",
          "sleepEndBaseline": "08:24:17",
          "totalSleepTimeSecondsBaseline": 21983
        },
        "chronotype": { "source": "pod", "chronoClass": "late", "isCalibrating": false },
        "socialJetlag": {
          "socialJetlagSeconds": 846,
          "avgWeekdaySleepMidpoint": "05:09:15",
          "avgWeekendSleepMidpoint": "05:23:21"
        },
        "exerciseWindow": {
          "exerciseWindowStart": "11:29:00",
          "exerciseWindowMidpoint": "12:29:00",
          "exerciseWindowEnd": "13:29:00"
        },
        "cognitiveWindow": {
          "cognitiveWindowStart": "13:16:30",
          "cognitiveWindowMidpoint": "15:46:30",
          "cognitiveWindowEnd": "18:16:30"
        }
      }
    },
    "..."
  ]
}
```

### With `include-all-sessions=true`

Includes a `sessions` array per day with full interval objects (same shape as the `/intervals` endpoint), but omits the scoring, health, and performance window fields.

Notes:
- Durations in seconds, percentages as decimals (0.29 = 29%).
- `tnt` — toss and turn count for the night.
- `score` — overall sleep fitness score (0–100).
- `sleepQualityScore` — weighted composite of duration, heart rate, HRV, respiratory rate, deep, REM, WASO, snoring. Each sub-metric has `current`, `average`, `score`, `weight`, and range bounds.
- `sleepRoutineScore` — consistency metrics (wake time, sleep start, bedtime). Scored against personal baselines.
- `health` — breathing irregularities, heartbeat irregularities, wellbeing (anomaly detection against day-of-week baselines).
- `performanceWindows` — optimal exercise and cognitive windows based on chronotype and sleep midpoint. Also includes social jetlag calculation.
- `hotFlash` — hot flash events detected during the session.
- Snoring mitigation fields (`mitigationEvents`, `stoppedSnoringEvents`, etc.) relate to autopilot elevation responses.

## Aggregated Metrics

```
GET https://app-api.8slp.net/v1/users/{userId}/metrics/aggregate?metrics=sleep_debt&periods=week&to=2026-03-28&tz=America/Los_Angeles
```

Response:
```json
{
  "periods": [
    {
      "name": "week",
      "date": "2026-03-28",
      "avg": [{ "name": "sleep_debt", "value": "-652.55" }],
      "stdDev": [{ "name": "sleep_debt", "value": "6562.95" }],
      "sum": [{ "name": "sleep_debt", "value": "-3915.31" }],
      "samples": [
        { "date": "2026-03-22", "avg": [{ "name": "sleep_debt", "value": "-6328.13" }] },
        { "date": "2026-03-23", "avg": [{ "name": "sleep_debt", "value": "4597.06" }] },
        "..."
      ]
    }
  ]
}
```

Notes:
- `metrics` query param — observed value: `sleep_debt`. Other possible values unknown.
- `periods` query param — observed value: `week`. Other possible values unknown.
- Values are strings (not numbers). Values appear to be in seconds. The sign convention (whether negative means deficit or surplus) has not been confirmed.
- `samples` gives per-day breakdowns within the period.
- Days with no sleep data are omitted from `samples`.

## Metrics Summary

```
GET https://app-api.8slp.net/v1/users/{userId}/metrics/summary?from=2026-03-27&metrics=sfs&periods=day&to=2026-03-29&tz=America/Los_Angeles
```

Separate from `metrics/aggregate` (which handles `sleep_debt`). Returns daily sleep fitness and quality scores.

Response (showing 3 days with one metric):
```json
{
  "days": [
    {
      "date": "2026-03-27",
      "metrics": [
        { "name": "sfs", "value": "75" }
      ]
    },
    {
      "date": "2026-03-28",
      "metrics": [
        { "name": "sfs", "value": "91" }
      ]
    },
    "..."
  ]
}
```

With multiple metrics (`?metrics=avg_sfs,avg_sqs,sfs`):
```json
{
  "days": [
    {
      "date": "2026-03-28",
      "metrics": [
        { "name": "avg_sfs", "value": "76.38" },
        { "name": "avg_sqs", "value": "82.38" },
        { "name": "sfs", "value": "91" }
      ]
    },
    "..."
  ]
}
```

Query parameters:
- `metrics` — comma-separated. Observed values: `sfs` (sleep fitness score), `avg_sfs` (average sleep fitness score), `avg_sqs` (average sleep quality score).
- `periods` — observed value: `day`.
- `from`/`to` — date range.
- `tz` — timezone.

Notes:
- Values are strings, not numbers.
- `sfs` is the per-night score (same as `score` in the trends response). `avg_sfs` and `avg_sqs` are rolling averages.
- Days with no sleep data are omitted.

## Bedtime Recommendation

```
GET https://app-api.8slp.net/v1/users/{userId}/bedtime/recommendation
```

Response:
```json
{
  "recommendedBedtime": "00:45:00",
  "standardDeviation": "01:10:42",
  "daysAnalyzed": 83,
  "topPerformingDays": 21
}
```

Notes:
- `recommendedBedtime` — time in 24h format. `"00:45:00"` = 12:45 AM.
- Based on analysis of `daysAnalyzed` nights, with `topPerformingDays` being the best-sleep subset.

## Tags

### Read Tags

```
GET https://client-api.8slp.net/v1/users/{userId}/tags?from=2026-03-29&to=2026-03-30
```

Response:
```json
{
  "days": [
    {
      "day": "2026-03-29",
      "tags": [
        {
          "id": "late_meal",
          "name": "Late meal",
          "value": true,
          "source": "user-input"
        },
        {
          "id": "caffeine",
          "name": "Caffeine",
          "value": false,
          "source": "user-input"
        },
        "..."
      ]
    },
    "..."
  ]
}
```

Notes:
- Date-range query. Days with no tags are omitted.
- Tags also appear in the compact trends response (see [Trends](#trends)).
- `source`: observed value `"user-input"`. Other sources may exist (e.g. auto-detected).
- `value: false` means the tag was set then cleared — it's still returned, not deleted.
- Known tag IDs: `"late_meal"`, `"caffeine"` (likely also `"late_caffeine"` — the app sent this ID but the server normalized it to `"caffeine"`). Full list of available tags unknown.
- A per-day path variant also exists: `GET /v1/users/{userId}/days/{date}/tags` — uses a path parameter for the date instead of `from`/`to` query params. Returns the same tag data.

### Update Tags

```
PUT https://client-api.8slp.net/v1/users/{userId}/days/{day}/tags
```

Body — sends the full set of tags for the day (not a partial update):
```json
{
  "tags": [
    { "id": "late_meal", "name": "Late meal", "value": true },
    { "id": "caffeine", "name": "Caffeine", "value": false }
  ]
}
```

Response returns the saved tags with `source` added:
```json
{
  "tags": [
    { "id": "late_meal", "name": "Late meal", "value": true, "source": "user-input" },
    { "id": "caffeine", "name": "Caffeine", "value": false, "source": "user-input" }
  ]
}
```

Notes:
- To clear a tag, set `value: false` — it persists in the response rather than being deleted.
- The server may normalize tag IDs (the app sent `"late_caffeine"` but the response returned `"caffeine"`).

## Truth Tags

```
GET https://app-api.8slp.net/v1/users/{userId}/truth-tags
```

Response:
```json
{
  "tags": []
}
```

No query parameters. We have never observed non-empty results — the shape of a truth tag object is unknown. Possibly ground-truth sleep stage corrections or feedback data for algorithm training.

## Edit Sleep Interval

```
PUT https://client-api.8slp.net/v1/users/{userId}/intervals/{intervalId}
```

Allows manual correction of sleep/wake times for an interval.

Body:
```json
{
  "ts": "2026-03-29T14:55:00.000Z",
  "stages": [
    { "duration": 3780, "stage": "awake" },
    { "duration": 840, "stage": "asleep" },
    { "duration": 3660, "stage": "awake" }
  ]
}
```

Response returns the full updated interval (same shape as GET `/intervals`):
```json
{
  "id": "1774796100",
  "ts": "2026-03-29T14:55:00.000Z",
  "stages": [
    { "stage": "awake", "duration": 3780 },
    { "stage": "light", "duration": 690 },
    { "stage": "awake", "duration": 3810 }
  ],
  "stageSummary": { "sleepDuration": 630, "..." },
  "timeseries": { "..." }
}
```

Notes:
- The PUT body uses coarse stage names (`"asleep"`) but the server refines them in the response (e.g. `"asleep"` → `"light"`). Durations may also be adjusted.
- The server recomputes `stageSummary`, `sleepStart`, `sleepEnd`, and timeseries data based on the edited stages.
- `ts` is the interval start time.
- Used when the pod's automatic sleep detection got the wake time wrong.

## Feedback

```
POST https://client-api.8slp.net/v1/users/{userId}/feedback
```

User confirmation that sleep analytics data looks accurate.

Body:
```json
{
  "properties": {
    "sleepAlgorithmVersion": "0.1.1",
    "presenceAlgorithmVersion": "3.2.1",
    "hrvAlgorithmVersion": "1.2.0",
    "processing": false,
    "complete": true,
    "type": "metrics",
    "answers": {
      "sessionIds": ["1774773060", "1774796100"],
      "sessionDay": "2026-03-29",
      "dataQuality": "high"
    },
    "sleep_heath_version": "v3",
    "showHypnogramDetail": "true",
    "hasHealthCheck": "true",
    "hasSnoreDetection": "true",
    "defaultBranch": "",
    "lagMinutes": 0
  }
}
```

Response: empty 200.

Notes:
- Fire-and-forget — the response has no body.
- `dataQuality`: observed value `"high"`. Presumably other values for when the user says the data looks wrong.
- Includes algorithm versions and session context, likely used to improve sleep detection models.
- Triggered from the "Does this look right?" prompt in the app's daily sleep summary.

## Insights

```
GET https://app-api.8slp.net/v1/users/{userId}/insights?date=2026-03-28
```

Separate from the `llm-insights` endpoint. Returns actionable sleep insights generated from the previous night's data.

Response:
```json
{
  "insights": [
    {
      "id": "userId-2026-03-28T18:02:30Z-performance_windows",
      "title": "Daily performance windows",
      "sentiment": "ALERT",
      "type": "performance_windows",
      "message": "Work out between 11:29AM\u20131:29PM and focus between 1:16PM\u20136:16PM to get the most out of your day.",
      "metric": "performance_windows",
      "summary": "",
      "priority": 58.7,
      "createdAt": "2026-03-28T18:02:30Z",
      "callout": { "title": "INSIGHT", "body": "New sleep insight" }
    },
    {
      "id": "userId-2026-03-28T18:02:30Z-hrv",
      "title": "New HRV alert",
      "sentiment": "GOAL",
      "type": "hrv",
      "message": "Last night your HRV 29ms was above your baseline (19 - 26). Looks like your body is recovering well!",
      "metric": "hrv",
      "summary": "Your body recovered well last night.",
      "priority": 58,
      "createdAt": "2026-03-28T18:02:30Z",
      "callout": { "title": "INSIGHT", "body": "New sleep insight" }
    },
    "..."
  ],
  "topInsight": {
    "...same shape as an insight, the highest-priority one..."
  }
}
```

Notes:
- `type`/`metric` observed values: `"performance_windows"`, `"hrv"`, `"exercise_window_shift"`, `"sleep_debt_insight_1"`, `"autopilot_deep"`.
- `sentiment`: `"ALERT"`, `"GOAL"`, or empty string.
- `priority`: numeric, higher = more important. `1000` observed for exercise window shifts.
- `topInsight`: duplicates the highest-priority insight from the array.
- `message`: human-readable text with specific values from the night's data (HRV numbers, exercise windows, sleep debt).
- `summary`: brief version of the message, empty for some insight types.
- This is different from `llm-insights` (which always returned empty `{}` in our testing). These insights are rule-based/computed, not LLM-generated.

## LLM Insights

```
GET https://app-api.8slp.net/v1/users/{userId}/llm-insights?from=2026-03-28&to=2026-03-28
```

Response (empty — the only state we've observed):
```json
{
  "insights": {}
}
```

Fetched 3 times on app launch (today, yesterday, day before). Per-day date range. We have never observed a non-empty response — the shape of an insight object is unknown. Possibly requires specific account/subscription conditions.

### LLM Insights Settings

```
GET https://app-api.8slp.net/v1/users/{userId}/llm-insights/settings
```

Response:
```json
{}
```

Empty object is the only response observed.

## Challenges

```
GET https://app-api.8slp.net/v1/users/{userId}/challenges
```

Response:
```json
{
  "results": []
}
```

We have never observed non-empty results — the shape of a challenge object is unknown. Likely gamification features (sleep streaks, goals, etc.).

## Days Count

```
GET https://app-api.8slp.net/v1/users/{userId}/days/count
```

Response:
```json
{
  "count": 52
}
```

Total number of tracked sleep days.
