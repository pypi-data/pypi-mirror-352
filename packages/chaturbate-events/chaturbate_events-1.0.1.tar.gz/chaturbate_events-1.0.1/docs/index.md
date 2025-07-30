# Chaturbate Events

Python wrapper for the Chaturbate Events API. Stream tips, messages, and user events.

```python
import asyncio
from chaturbate_events import ChaturbateEventsClient, TipEvent

async def main():
    async with ChaturbateEventsClient("username", "api_token") as client:
        async for event in client.stream_events():
            if isinstance(event, TipEvent):
                print(f"{event.user.username} tipped {event.tip.tokens} tokens")

asyncio.run(main())
```

```{toctree}
:maxdepth: 2
:caption: Documentation

example.ipynb
api/index
CHANGELOG.md
LICENSE.md
```