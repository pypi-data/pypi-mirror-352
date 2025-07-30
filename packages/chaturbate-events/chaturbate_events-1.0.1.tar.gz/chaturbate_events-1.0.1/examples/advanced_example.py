"""Event filtering and custom handlers example."""

import asyncio
import logging

from chaturbate_events import (
    ChatMessageEvent,
    ChaturbateEventsClient,
    EventMethod,
    TipEvent,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Stream and handle specific event types."""
    username = "your_broadcaster_username"
    token = "your_api_token"  # noqa: S105

    # Filter for specific events
    event_filter: set[EventMethod] = {
        EventMethod.TIP,
        EventMethod.CHAT_MESSAGE,
    }

    async with ChaturbateEventsClient(
        broadcaster=username,
        api_token=token,
        testbed=True,
        max_retries=3,
    ) as client:
        logger.info("Connected. Listening for tips and chat...")

        async for event in client.stream_events(event_filter=event_filter):
            if isinstance(event, TipEvent):
                logger.info(
                    "Tip: %d tokens from %s",
                    event.tip.tokens,
                    event.user.username,
                )

            elif isinstance(event, ChatMessageEvent):
                logger.info(
                    "Chat: %s says '%s'",
                    event.user.username,
                    event.message.message,
                )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stopped")
    except Exception:
        logger.exception("Error occurred")
