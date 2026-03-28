# eight-sleep-client

Async Python client for the Eight Sleep Pod API.

## Usage

```python
import httpx
from eight_sleep_client import EightSleepClient

async with httpx.AsyncClient() as http:
    client = EightSleepClient(http, email="you@example.com", password="secret")
    session = await client.authenticate()
    print(session.user_id)
    print(session.device_ids)
```

## Development

```bash
pip install -e ".[test]"
pytest
```
