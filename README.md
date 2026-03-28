# eight-sleep-client

Async Python client library for the Eight Sleep Pod API.

Built from a reverse-engineered API reference (captured via MITM proxy from the iOS app, March 2026).

## Why

The Eight Sleep Pod has no official public API. Existing third-party clients are tightly coupled to Home Assistant or out of date with current API endpoints. This library is a standalone, framework-free Python client that any consumer can use — Home Assistant integrations, CLI tools, scripts, or other automation platforms.

## Tested hardware

- Pod 4 Ultra

Other Pod models may work but haven't been tested.

## Design

- **Layered architecture** — Model → Repository → Session → Client
- **Pure async Python** — built on httpx, no framework dependencies
- **Dependency injection** — caller provides the `httpx.AsyncClient`
- **Session as entry point** — `Session.create()` is the public API
- **Rich domain models** — mutable objects with behavior, delegating to repositories
- **TDD** — pytest + mockito, strict mocking at boundaries

## Usage

```python
import httpx
from eight_sleep_client import Session

async with httpx.AsyncClient() as http:
    session = await Session.create(http, email="you@example.com", password="secret")
    print(session.user_id)
    print(session.device_ids)
```

## Roadmap

1. **Auth + User Discovery** (complete) — authenticate, fetch user/device info
2. **Alarms** — full CRUD for the alarms API
3. **Temperature Control** — on/off, smart schedules, autopilot
4. **Away Mode** — start/end away with return date
5. **Additional Features** — nap mode, LED brightness, bed base control, snore mitigation, and more

See [docs/plan.md](docs/plan.md) for details.

## Development

```bash
pip install -e ".[test]"
pytest
```

## API Reference

Full reverse-engineered API documentation is in [docs/api_reference.md](docs/api_reference.md).
