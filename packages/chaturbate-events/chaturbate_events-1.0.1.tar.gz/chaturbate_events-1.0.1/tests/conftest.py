"""Shared test fixtures and utilities."""

from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest

from chaturbate_events import ChaturbateEventsClient


@pytest.fixture
def client() -> ChaturbateEventsClient:
    """Create a test client."""
    return ChaturbateEventsClient("test_broadcaster", "test_token", testbed=True)


@pytest.fixture
def sample_user() -> dict[str, Any]:
    """Sample user data."""
    return {
        "username": "test_user",
        "gender": "m",
        "hasTokens": True,
        "inFanclub": False,
        "isMod": False,
        "recentTips": "none",
    }


@pytest.fixture
def sample_user_female() -> dict[str, Any]:
    """Sample female user data."""
    return {
        "username": "test_user_f",
        "gender": "f",
        "hasTokens": True,
        "inFanclub": False,
        "isMod": False,
        "recentTips": "some",
    }


@pytest.fixture
def sample_message() -> dict[str, Any]:
    """Sample message data."""
    return {
        "message": "Hello everyone!",
        "color": "#ffffff",
        "font": "default",
    }


@pytest.fixture
def sample_private_message() -> dict[str, Any]:
    """Sample private message data."""
    return {
        "message": "Private message",
        "fromUser": "sender",
        "toUser": "recipient",
    }


@pytest.fixture
def sample_tip() -> dict[str, Any]:
    """Sample tip data."""
    return {
        "tokens": 100,
        "isAnon": False,
        "message": "Great show!",
    }


@pytest.fixture
def sample_media() -> dict[str, Any]:
    """Sample media data."""
    return {
        "id": 123,
        "name": "Test Video",
        "type": "video",
        "tokens": 50,
    }


@pytest.fixture
def event_base_data() -> dict[str, Any]:
    """Return base data for events."""
    return {
        "id": "test-event-id",
        "object": {
            "broadcaster": "test_broadcaster",
        },
    }


@pytest.fixture
def sample_response() -> dict[str, Any]:
    """Sample API response."""
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
                "id": "test-event-id",
            }
        ],
        "nextUrl": "https://events.testbed.cb.dev/events/test_broadcaster/test_token/?i=test-event-id&timeout=10",
    }


@pytest.fixture
def mock_http_response(sample_response: dict[str, Any]) -> AsyncMock:
    """Create a mock HTTP response."""
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = Mock(return_value=sample_response)
    return mock_response


@pytest.fixture
def fast_retry_client() -> ChaturbateEventsClient:
    """Create a client with fast retry settings for testing."""
    client = ChaturbateEventsClient("test_broadcaster", "test_token", testbed=True)
    client.retry_delay = 0.01
    client.max_retries = 2
    return client
