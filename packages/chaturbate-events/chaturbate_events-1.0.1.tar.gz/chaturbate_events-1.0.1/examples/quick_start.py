"""Basic usage example."""

import asyncio

from chaturbate_events import ChaturbateEventsClient, TipEvent


async def main() -> None:
    """Connect and stream events."""
    username = "your_broadcaster_username"
    token = "your_api_token"  # noqa: S105

    async with ChaturbateEventsClient(username, token, testbed=True) as client:
        async for event in client.stream_events():
            print(f"Event: {event.method}")

            if isinstance(event, TipEvent):
                print(f"  Tip: {event.tip.tokens} tokens")


if __name__ == "__main__":
    asyncio.run(main())
