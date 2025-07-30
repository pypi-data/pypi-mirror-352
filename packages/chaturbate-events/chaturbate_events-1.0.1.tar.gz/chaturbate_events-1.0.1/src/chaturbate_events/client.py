"""Main client for the Chaturbate Events API."""

import asyncio
import logging
from collections.abc import AsyncIterator
from types import TracebackType
from urllib.parse import parse_qs, urljoin, urlparse

import httpx

from .exceptions import APIError, AuthenticationError, ChaturbateEventsError
from .models import BaseEvent, EventMethod, EventResponse

logger = logging.getLogger(__name__)
"""logging.Logger: Logger for the Chaturbate Events API client."""

MAX_API_TIMEOUT = 90
"""str: Maximum allowed API timeout in seconds."""


class ChaturbateEventsClient:
    """Async client for the Chaturbate Events API."""

    BASE_URL = "https://eventsapi.chaturbate.com/"
    TESTBED_URL = "https://events.testbed.cb.dev/"

    def __init__(  # noqa: PLR0913
        self,
        broadcaster: str,
        api_token: str,
        *,
        testbed: bool = False,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> None:
        """Initialize the client.

        Args:
            broadcaster: The broadcaster username
            api_token: The API token for authentication
            testbed: Whether to use the testbed environment (default: False)
            timeout: HTTP request timeout in seconds (default: 30.0)
            max_retries: Maximum number of retries for failed requests (default: 3)
            retry_delay: Delay between retries in seconds (default: 1.0)

        """
        self.broadcaster = broadcaster
        self.api_token = api_token
        self.base_url = self.TESTBED_URL if testbed else self.BASE_URL
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        self._client: httpx.AsyncClient | None = None
        self._next_url: str | None = None

    async def __aenter__(self) -> "ChaturbateEventsClient":
        """Async context manager entry."""
        await self._ensure_client()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Async context manager exit."""
        await self.close()

    async def _ensure_client(self) -> None:
        """Ensure the HTTP client is initialized."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout + 10),
                follow_redirects=True,
            )

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def _build_initial_url(self, timeout: int | None = None) -> str:
        """Build the initial events URL."""
        url = urljoin(self.base_url, f"events/{self.broadcaster}/{self.api_token}/")
        if timeout is not None:
            url += f"?timeout={timeout}"
        return url

    async def _make_request(self, url: str) -> dict[str, object]:
        """Make an HTTP request with retry logic."""
        await self._ensure_client()

        if not self._client:
            msg = "HTTP client is not initialized"
            raise ChaturbateEventsError(msg)

        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                response = await self._client.get(url)

                if response.status_code == httpx.codes.NOT_FOUND:
                    msg = "Invalid API token or broadcaster"
                    raise AuthenticationError(msg)
                if response.status_code == httpx.codes.UNAUTHORIZED:
                    msg = "Broadcaster or endpoint not found"
                    raise AuthenticationError(msg)
                if response.status_code >= httpx.codes.BAD_REQUEST:
                    msg = f"HTTP {response.status_code}: {response.text}"
                    raise APIError(msg)

                return dict(response.json())

            except httpx.HTTPError as e:
                last_exception = e
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay * (2**attempt))
                    continue
                break

        msg = f"Request failed after {self.max_retries + 1} attempts"
        raise ChaturbateEventsError(msg) from last_exception

    async def get_events(
        self, api_timeout: int | None = None, *, use_next_url: bool = True
    ) -> EventResponse:
        """Get the next batch of events.

        Args:
            api_timeout: Server timeout in seconds (0-90, default: 10)
            use_next_url: Whether to use the stored next_url from previous requests
                         (default: True)

        Returns:
            EventResponse containing events and next URL

        Raises:
            ChaturbateEventsError: For API errors
            AuthenticationError: For authentication issues
            APIError: For HTTP errors

        """
        if api_timeout is not None and not 0 <= api_timeout <= MAX_API_TIMEOUT:
            msg = "Timeout must be between 0 and 90 seconds"
            raise ValueError(msg)

        if use_next_url and self._next_url:
            url = self._next_url
            # Override timeout in existing URL if provided
            if api_timeout is not None:
                parsed = urlparse(url)
                query_params = parse_qs(parsed.query)
                query_params["timeout"] = [str(api_timeout)]
                # Rebuild query string
                query_string = "&".join(f"{k}={v[0]}" for k, v in query_params.items())
                url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{query_string}"
        else:
            url = self._build_initial_url(api_timeout)

        data = await self._make_request(url)
        response = EventResponse.model_validate(data)

        # Store the next URL for subsequent requests
        self._next_url = response.next_url

        return response

    async def stream_events(
        self,
        api_timeout: int | None = None,
        event_filter: set[EventMethod] | None = None,
        max_consecutive_failures: int = 10,
    ) -> AsyncIterator[BaseEvent]:
        """Stream events continuously.

        Args:
            api_timeout: Server timeout for each request (0-90, default: 10)
            event_filter: Set of event methods to filter for (default: None for all)
            max_consecutive_failures: Max consecutive failures before giving up (default: 10)

        Yields:
            Individual Event objects as they arrive

        Raises:
            ChaturbateEventsError: For API errors
            AuthenticationError: For authentication issues
            APIError: For HTTP errors

        """
        consecutive_failures = 0

        while True:
            try:
                response = await self.get_events(api_timeout=api_timeout)
                consecutive_failures = 0  # Reset on successful request

                for event in response.events:
                    if event_filter is None or event.method in event_filter:
                        yield event

            except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as e:
                # Retry network-related errors that might be temporary
                consecutive_failures += 1
                if consecutive_failures >= max_consecutive_failures:
                    msg = f"Too many consecutive network failures ({consecutive_failures})"
                    raise ChaturbateEventsError(msg) from e

                logger.exception("Network error while streaming events, retrying...")
                await asyncio.sleep(self.retry_delay * min(consecutive_failures, 5))
                continue

    def reset_stream(self) -> None:
        """Reset the stream to start from the beginning."""
        self._next_url = None
