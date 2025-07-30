"""Tests for the ChaturbateEventsClient."""

import asyncio
from typing import Any
from unittest.mock import Mock, patch

import httpx
import pytest

from chaturbate_events import (
    APIError,
    AuthenticationError,
    ChaturbateEventsClient,
    ChaturbateEventsError,
)
from chaturbate_events.models import EventMethod, EventResponse


class TestClientInitialization:
    """Test client initialization scenarios."""

    @pytest.mark.parametrize(
        ("testbed", "expected_url"),
        [
            (True, ChaturbateEventsClient.TESTBED_URL),
            (False, ChaturbateEventsClient.BASE_URL),
        ],
    )
    def test_initialization(self, *, testbed: bool, expected_url: str) -> None:
        """Test client initialization with different parameters."""
        client = ChaturbateEventsClient(
            "broadcaster",
            "test_token",
            testbed=testbed,
            timeout=60.0,
            max_retries=5,
            retry_delay=2.0,
        )

        assert client.broadcaster == "broadcaster"
        assert client.api_token == "test_token"  # noqa: S105
        assert client.base_url == expected_url
        assert client.timeout == 60.0
        assert client.max_retries == 5
        assert client.retry_delay == 2.0


class TestURLBuilding:
    """Test URL building functionality."""

    def test_url_building_with_timeout(self, client: ChaturbateEventsClient) -> None:
        """Test URL building with timeout parameter."""
        url = client._build_initial_url(timeout=30)
        assert "timeout=30" in url
        assert client.broadcaster in url
        assert client.api_token in url

    def test_url_building_without_timeout(self, client: ChaturbateEventsClient) -> None:
        """Test URL building without timeout parameter."""
        url = client._build_initial_url()
        assert "timeout" not in url
        assert client.broadcaster in url
        assert client.api_token in url


class TestErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.parametrize(
        ("status_code", "exception_type", "error_message"),
        [
            (404, AuthenticationError, "Invalid API token or broadcaster"),
            (401, AuthenticationError, "Broadcaster or endpoint not found"),
            (500, APIError, "HTTP 500:"),
        ],
    )
    @patch("httpx.AsyncClient.get")
    async def test_http_errors(
        self,
        mock_get: Mock,
        client: ChaturbateEventsClient,
        status_code: int,
        exception_type: type[Exception],
        error_message: str,
    ) -> None:
        """Test various HTTP error scenarios."""
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.text = "Server Error"
        mock_get.return_value = mock_response

        async with client:
            with pytest.raises(exception_type, match=error_message):
                await client.get_events()

    @patch("httpx.AsyncClient.get")
    async def test_network_error_with_retry(
        self, mock_get: Mock, fast_retry_client: ChaturbateEventsClient
    ) -> None:
        """Test network error handling with retry logic."""
        mock_get.side_effect = httpx.ConnectError("Connection failed")

        async with fast_retry_client:
            with pytest.raises(ChaturbateEventsError, match="Request failed after 3 attempts"):
                await fast_retry_client.get_events()

        # Verify retries happened (initial + 2 retries = 3 total)
        assert mock_get.call_count == 3

    @patch("httpx.AsyncClient.get")
    async def test_network_error_recovery(
        self,
        mock_get: Mock,
        fast_retry_client: ChaturbateEventsClient,
        mock_http_response: Mock,
    ) -> None:
        """Test network error recovery after retry."""
        # First call fails, second succeeds
        mock_get.side_effect = [
            httpx.ConnectError("Connection failed"),
            mock_http_response,
        ]

        async with fast_retry_client:
            response = await fast_retry_client.get_events()

        assert isinstance(response, EventResponse)
        assert mock_get.call_count == 2


class TestEventRetrieval:
    """Test event retrieval functionality."""

    @pytest.mark.parametrize("api_timeout", [-1, 91])
    def test_timeout_validation(self, client: ChaturbateEventsClient, api_timeout: int) -> None:
        """Test timeout validation edge cases."""
        with pytest.raises(ValueError, match="Timeout must be between 0 and 90"):
            asyncio.run(client.get_events(api_timeout=api_timeout))

    @patch("httpx.AsyncClient.get")
    async def test_get_events_with_next_url(
        self,
        mock_get: Mock,
        client: ChaturbateEventsClient,
        mock_http_response: Mock,
    ) -> None:
        """Test get_events using stored next_url."""
        mock_get.return_value = mock_http_response

        # Set a next_url
        next_url = (
            "https://events.testbed.cb.dev/events/test_broadcaster/test_token/?i=123&timeout=10"
        )
        client._next_url = next_url

        async with client:
            await client.get_events(use_next_url=True)

        # Verify it used the stored next_url
        called_url = mock_get.call_args[0][0]
        assert "i=123" in called_url

    @patch("httpx.AsyncClient.get")
    async def test_get_events_ignore_next_url(
        self,
        mock_get: Mock,
        client: ChaturbateEventsClient,
        mock_http_response: Mock,
    ) -> None:
        """Test ignoring stored next_url when use_next_url=False."""
        mock_get.return_value = mock_http_response

        # Set a next_url
        client._next_url = "https://example.com/next?i=123"

        async with client:
            await client.get_events(use_next_url=False)

        # Verify it built a new URL instead of using next_url
        called_url = mock_get.call_args[0][0]
        assert "i=123" not in called_url

    @patch("httpx.AsyncClient.get")
    async def test_timeout_override_in_next_url(
        self,
        mock_get: Mock,
        client: ChaturbateEventsClient,
        mock_http_response: Mock,
    ) -> None:
        """Test overriding timeout in existing next_url."""
        mock_get.return_value = mock_http_response

        # Set a next_url with existing timeout
        client._next_url = (
            "https://events.testbed.cb.dev/events/test_broadcaster/test_token/?i=123&timeout=10"
        )

        async with client:
            await client.get_events(api_timeout=60, use_next_url=True)

        # Verify timeout was overridden
        called_url = mock_get.call_args[0][0]
        assert "timeout=60" in called_url
        assert "i=123" in called_url


class TestEventStreaming:
    """Test event streaming functionality."""

    def create_multi_event_response(self) -> dict[str, Any]:
        """Create a response with multiple event types."""
        return {
            "events": [
                {
                    "method": "userEnter",
                    "object": {
                        "broadcaster": "test_broadcaster",
                        "user": {
                            "username": "test_user",
                            "gender": "m",
                            "hasTokens": True,
                            "inFanclub": False,
                            "isMod": False,
                            "recentTips": "none",
                        },
                    },
                    "id": "test-event-id-1",
                },
                {
                    "method": "tip",
                    "object": {
                        "broadcaster": "test_broadcaster",
                        "user": {
                            "username": "tipper",
                            "gender": "f",
                            "hasTokens": True,
                            "inFanclub": False,
                            "isMod": False,
                            "recentTips": "tons",
                        },
                        "tip": {
                            "tokens": 100,
                            "isAnon": False,
                            "message": "Great show!",
                        },
                    },
                    "id": "test-event-id-2",
                },
            ],
            "nextUrl": "https://events.testbed.cb.dev/events/test_broadcaster/test_token/?i=test-event-id-2&timeout=10",
        }

    @patch("httpx.AsyncClient.get")
    async def test_stream_events_with_filter(
        self, mock_get: Mock, client: ChaturbateEventsClient
    ) -> None:
        """Test event streaming with method filter."""
        multi_event_response = self.create_multi_event_response()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json = Mock(return_value=multi_event_response)
        mock_get.return_value = mock_response

        async with client:
            tip_events = 0

            async def stream_with_filter() -> None:
                nonlocal tip_events
                # Filter for only tip events
                async for event in client.stream_events(event_filter={EventMethod.TIP}):
                    if event.method == EventMethod.TIP:
                        tip_events += 1  # ty: ignore[unresolved-reference]
                    if tip_events >= 1:  # Stop after getting 1 tip event
                        break

            await asyncio.wait_for(stream_with_filter(), timeout=5.0)
            assert tip_events == 1

    @patch("httpx.AsyncClient.get")
    async def test_stream_events_exception_recovery(
        self, mock_get: Mock, fast_retry_client: ChaturbateEventsClient
    ) -> None:
        """Test stream_events exception handling and recovery."""
        # First call raises exception, second succeeds
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json = Mock(
            return_value={
                "events": [
                    {
                        "method": "userEnter",
                        "object": {
                            "broadcaster": "test_broadcaster",
                            "user": {
                                "username": "test_user",
                                "gender": "m",
                                "hasTokens": True,
                                "inFanclub": False,
                                "isMod": False,
                                "recentTips": "none",
                            },
                        },
                        "id": "test-event-id",
                    }
                ],
                "nextUrl": "https://events.testbed.cb.dev/next",
            }
        )

        mock_get.side_effect = [
            httpx.ConnectError("Network error"),  # First call fails
            mock_response_success,  # Second call succeeds
        ]

        async with fast_retry_client:
            count = 0

            async def stream_with_exception_recovery() -> None:
                nonlocal count
                async for _event in fast_retry_client.stream_events():
                    count += 1  # ty: ignore[unresolved-reference]
                    if count >= 1:  # Stop after 1 successful event
                        break

            await asyncio.wait_for(stream_with_exception_recovery(), timeout=5.0)
            assert count == 1

    @patch("chaturbate_events.client.ChaturbateEventsClient.get_events")
    async def test_stream_events_max_consecutive_failures(
        self, mock_get_events: Mock, client: ChaturbateEventsClient
    ) -> None:
        """Test stream_events raises exception after max consecutive failures."""
        client.retry_delay = 0.01

        mock_get_events.side_effect = httpx.ConnectError("Network error")

        async with client:
            with pytest.raises(
                ChaturbateEventsError, match="Too many consecutive network failures \\(10\\)"
            ):
                async for _event in client.stream_events(max_consecutive_failures=10):
                    pass  # This should never execute due to failures

        # Should have made exactly 10 attempts (the max_consecutive_failures limit)
        assert mock_get_events.call_count == 10

    @patch("asyncio.sleep")
    @patch("chaturbate_events.client.ChaturbateEventsClient.get_events")
    async def test_stream_events_retry_delay_logic(
        self, mock_get_events: Mock, mock_sleep: Mock, client: ChaturbateEventsClient
    ) -> None:
        """Test stream_events retry delay logic with consecutive failures."""
        client.retry_delay = 2.0

        # Create a mock response for success case
        mock_event = Mock()
        mock_event.method = EventMethod.USER_ENTER
        mock_event.id = "test-event-id"

        mock_response_success = Mock()
        mock_response_success.events = [mock_event]

        # First two calls fail, third succeeds
        mock_get_events.side_effect = [
            httpx.ConnectError("Connection failed"),
            httpx.TimeoutException("Request timeout"),
            mock_response_success,
        ]

        async with client:
            count = 0

            async def stream_with_retry_delay() -> None:
                nonlocal count
                async for _event in client.stream_events():
                    count += 1  # ty: ignore[unresolved-reference]
                    if count >= 1:
                        break

            await asyncio.wait_for(stream_with_retry_delay(), timeout=10.0)
            assert count == 1

        # Verify sleep was called with proper delay calculation
        # First failure: min(1, 5) * 2.0 = 2.0
        # Second failure: min(2, 5) * 2.0 = 4.0
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(2.0)  # First retry delay
        mock_sleep.assert_any_call(4.0)  # Second retry delay


class TestClientLifecycle:
    """Test client lifecycle management."""

    def test_reset_stream(self, client: ChaturbateEventsClient) -> None:
        """Test reset_stream method."""
        client._next_url = "https://example.com/next"
        client.reset_stream()
        assert client._next_url is None

    async def test_close_without_client(self, client: ChaturbateEventsClient) -> None:
        """Test calling close when client is not initialized."""
        await client.close()
        assert client._client is None

    @patch.object(ChaturbateEventsClient, "_ensure_client")
    async def test_make_request_client_not_initialized(
        self, mock_ensure_client: Mock, client: ChaturbateEventsClient
    ) -> None:
        """Test _make_request when HTTP client is not initialized."""
        mock_ensure_client.return_value = None
        client._client = None

        with pytest.raises(ChaturbateEventsError, match="HTTP client is not initialized"):
            await client._make_request("https://example.com")
