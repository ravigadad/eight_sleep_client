# Eight Sleep API Reference

Reverse-engineered from the Eight Sleep iOS app via MITM proxy (March 2026).

## Table of Contents

| Domain | File | Keywords |
|--------|------|----------|
| **[Infrastructure](api_reference/infrastructure.md)** | `infrastructure.md` | auth, login, tokens, Bearer, client credentials, base URLs, app launch, polling intervals |
| **[User](api_reference/user.md)** | `user.md` | /users/me, `me` alias, partner fetch, temp preference, chronotype, notifications, display settings, health survey, weight, sleep disorders |
| **[Device](api_reference/device.md)** | `device.md` | /devices/{deviceId}, hardware, firmware, wifi, connectivity, pod model, bed size, LED brightness, tap gestures, priming, maintenance schedule, maintenance insert, insert address |
| **[Alarms](api_reference/alarms.md)** | `alarms.md` | wake alarm, vibration, thermal wake, smart wake, snooze, dismiss, stop, skip, enable/disable, one-time override, repeating, schedule |
| **[Temperature](api_reference/temperature.md)** | `temperature.md` | heating, cooling, smart schedule, bedtime level, initial sleep, final sleep, on/off, override tonight, permanent levels, bedtime schedule, level scales, dial values, raw levels |
| **[Bed Base & Elevation](api_reference/bed_base.md)** | `bed_base.md` | bed platform, head angle, foot angle, torso, leg, presets, flat, sleep position, reading, relaxing, anti-snore, zero-g, moving |
| **[Sleep Features](api_reference/sleep_features.md)** | `sleep_features.md` | nap mode, start/stop/extend nap, hot flash, burst cooling, night sweats, snore mitigation, auto-elevation |
| **[Household](api_reference/household.md)** | `household.md` | household summary, device sets, side assignment, pairing vs assignment, guest management, add/remove guests, reclaim device, remove user assignment, away mode, return schedule, invitations, invite user, accept invite, household users list, add/remove device, device owner transfer |
| **[Autopilot & Analytics](api_reference/autopilot.md)** | `autopilot.md` | automatic temperature, ambient response, autopilot toggle, level suggestions, cohort recommendations, nightly recap, sleep stage adjustments, calibration, aggregate history |
| **[Sleep Analytics](api_reference/sleep_analytics.md)** | `sleep_analytics.md` | intervals, sleep stages, trends, snoring, HRV, heart rate, respiratory rate, sleep debt, bedtime recommendation, toss and turn, timeseries, tags, truth tags, feedback, edit intervals, challenges, days count, metrics summary, insights |
| **[Account](api_reference/account.md)** | `account.md` | subscription, billing, premium, basic, capabilities, feature gates, purchase history, referral program |
| **[Jet Lag Protocol](api_reference/jet_lag.md)** | `jet_lag.md` | travel, flight lookup, trip planning, timezone shift, pre-flight/post-flight tasks, supplements |
| **[Audio](api_reference/audio.md)** | `audio.md` | Pod 5 Ultra only, speakers, soundscapes, alarm tones, NSDR, Huberman, player, Base speakers |
| **[App Client](api_reference/app_client.md)** | `app_client.md` | notifications, push targets, APNS, onboarding, feature flags, release features, device security key, SMS, health integrations, Apple Health sync |
| **[Device Compatibility](api_reference/device_compatibility.md)** | `device_compatibility.md` | Pod 2 Pro, Pod 3, Pod 4, Pod 5, hardware vs subscription capabilities, features array, tap settings GET, hybrid cover/hub, priming differences, recommended alarm |
| **[Appendix](api_reference/appendix.md)** | `appendix.md` | legacy routines, deprecated endpoints, WebSocket events, migration table |

## API Base URLs

- **auth-api**: `https://auth-api.8slp.net/v1` — authentication only
- **client-api**: `https://client-api.8slp.net/v1` — device data, user profiles, LED, priming
- **app-api**: `https://app-api.8slp.net` — temperature, alarms, base, features (v1 and v2 paths)
