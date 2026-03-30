# Audio (Pod 5 Ultra only)

Audio playback through the Pod 5 Ultra's built-in Base speakers. The content catalog endpoints return data for all accounts, but actual playback requires a paired Base with speakers (`audio/player` returns `{"message": "No Associated Speaker", "errorType": "BaseNotPaired"}` on Pod 4).

## Contents

- [Categories](#categories)
- [Tracks](#tracks)
- [Player](#player)

## Categories

```
GET https://app-api.8slp.net/v1/audio/categories
```

Response:
```json
{
  "categories": [
    {
      "id": "soundscapes",
      "name": "soundscapes",
      "description": "Immersive audio for uninterrupted sleep",
      "detailedDescription": "Soundscapes, like nature sounds or ambient noise, can enhance sleep by masking disruptions, promoting relaxation, and potentially improving Deep and REM sleep quality",
      "accentedTitle": "sound",
      "tags": [],
      "appData": {
        "assetUrl": "https://eight-eightsleep-react.s3.us-east-2.amazonaws.com/audio/cover/soundscapes-cover.jpg",
        "thumbnailUrl": "https://eight-eightsleep-react.s3.us-east-2.amazonaws.com/audio/cover/soundscapes-cover.jpg",
        "backgroundStyle": "Gradient",
        "backgroundColors": ["#161F2C", "#000102"]
      }
    },
    {
      "id": "alarms",
      "name": "alarms",
      "description": "Alarms",
      "detailedDescription": "",
      "accentedTitle": "alarms",
      "tags": [{ "tagId": "alarms", "name": "Alarms" }],
      "appData": { "..." }
    },
    {
      "id": "nsdr",
      "name": "non-sleep deep rest",
      "description": "Guided by Andrew Huberman",
      "detailedDescription": "Non-Sleep Deep Rest (NSDR) is a relaxation technique coined by Dr. Andrew Huberman that promotes deep rest without sleep, using meditation, breathwork, or Yoga Nidra to recharge the brain and body",
      "accentedTitle": "non-sleep",
      "tags": [{ "tagId": "meditation", "name": "Meditation" }],
      "appData": { "..." }
    }
  ]
}
```

Three categories observed: `soundscapes`, `alarms`, `nsdr`.

## Tracks

```
GET https://app-api.8slp.net/v1/users/{userId}/audio/tracks?category=soundscapes
```

Response (showing one of 13 soundscape tracks):
```json
{
  "tracks": [
    {
      "id": "pink-noise",
      "name": "Pink noise",
      "description": "Soft, balanced hum with deep tones",
      "categoryId": "soundscapes",
      "duration": "0:00:30",
      "tags": [],
      "appData": {
        "assetUrl": "https://eight-eightsleep-react.s3.us-east-2.amazonaws.com/audio/soundscapes/Backgrounds/pink-noise-background.png",
        "thumbnailUrl": "https://eight-eightsleep-react.s3.us-east-2.amazonaws.com/audio/soundscapes/Thumbnails/pink-noise-thumbnail.png",
        "backgroundStyle": "Gradient",
        "backgroundColors": ["#FABED5", "#B03866"]
      }
    },
    "..."
  ]
}
```

Track counts per category:
- `soundscapes` — 13 tracks: Pink noise, Brown noise, White noise, Calm river, Island beach life, Mountain rain, Nighttime campfire, Nocturnal beach waves, Rain and thunder, Rainforest nightlife, Summer night, Tropical rain, Underwater movement
- `alarms` — 8 tracks: Surge, Jumpstart, Ignition, Daybreak, Pulse, Lucid, Drift, Flow
- `nsdr` — 2 tracks: Protocol 01 (10:05), Protocol 02

Notes:
- Track metadata only — no audio stream URLs. Actual audio is presumably delivered through the player.
- `duration` format varies: `"0:00:30"` for soundscapes (loops?), `"0:00:06"` for alarm tones, `"0:10:05"` for NSDR sessions.
- `appData` contains UI assets (background images, thumbnails, color gradients). Some NSDR tracks include `backgroundUrl` pointing to a video.

## Player

```
GET https://app-api.8slp.net/v1/users/{userId}/audio/player
```

Response on Pod 4 (no Base speakers):
```json
{
  "message": "No Associated Speaker",
  "errorType": "BaseNotPaired"
}
```

Status 404. Player state and controls are only available with a paired Pod 5 Ultra Base. We have not observed a successful response — the request/response shape for active playback is unknown.
