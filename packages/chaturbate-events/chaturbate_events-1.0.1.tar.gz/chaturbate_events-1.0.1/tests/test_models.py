"""Tests for the data models."""

from typing import Any

import pytest
from pydantic import ValidationError

from chaturbate_events.models import (
    BaseEvent,
    BroadcastStartEvent,
    BroadcastStopEvent,
    ChatMessageEvent,
    EventMethod,
    EventResponse,
    FanclubJoinEvent,
    FollowEvent,
    Media,
    MediaPurchaseEvent,
    Message,
    PrivateMessageEvent,
    RoomSubjectChangeEvent,
    Tip,
    TipEvent,
    UnfollowEvent,
    User,
    UserEnterEvent,
    UserLeaveEvent,
)


class TestMessage:
    """Test Message model."""

    def test_message_validation_with_none(self) -> None:
        """Test Message validation with None values."""
        message_data = {
            "message": None,
            "color": None,
            "bgColor": None,
            "font": "default",
            "fromUser": None,
            "toUser": None,
            "orig": None,
        }

        with pytest.raises(ValidationError, match="Input should be a valid string"):
            Message.model_validate(message_data)

    @pytest.mark.parametrize(
        ("from_user", "to_user", "expected"),
        [
            ("sender", "recipient", True),  # Private message
            (None, None, False),  # Public message
            ("sender", None, False),  # Partial private message
            (None, "recipient", False),  # Invalid private message
        ],
    )
    def test_is_private_computed_field(
        self, from_user: str | None, to_user: str | None, *, expected: bool
    ) -> None:
        """Test Message.is_private computed field."""
        message_data = {
            "message": "Hello",
            "fromUser": from_user,
            "toUser": to_user,
        }
        message = Message.model_validate(message_data)
        assert message.is_private is expected

    def test_field_defaults(self) -> None:
        """Test Message model field defaults."""
        message_data = {"message": "Test message"}
        message = Message.model_validate(message_data)

        assert message.message == "Test message"
        assert message.color is None
        assert message.bg_color is None
        assert message.font == "default"
        assert message.from_user is None
        assert message.to_user is None
        assert message.orig is None


class TestTip:
    """Test Tip model."""

    @pytest.mark.parametrize("tokens", [0, -5])
    def test_invalid_tokens_validation(self, tokens: int) -> None:
        """Test Tip validation with invalid token amounts."""
        with pytest.raises(ValidationError, match="Input should be greater than 0"):
            Tip.model_validate({"tokens": tokens, "isAnon": False, "message": ""})

    def test_usd_computed_field(self) -> None:
        """Test Tip.tip_value_usd computed field."""
        tip = Tip.model_validate({"tokens": 100, "isAnon": False})
        assert tip.tip_value_usd == 5.0


class TestMedia:
    """Test Media model."""

    def test_price_usd_computed_field(self) -> None:
        """Test Media.price_usd computed field."""
        media = Media.model_validate(
            {
                "id": 123,
                "name": "Test Video",
                "type": "video",
                "tokens": 200,
            }
        )
        assert media.price_usd == 10.0

    def test_zero_tokens_allowed(self) -> None:
        """Test Media allows zero tokens."""
        media = Media.model_validate(
            {
                "id": 123,
                "name": "Free Content",
                "type": "photos",
                "tokens": 0,
            }
        )
        assert media.tokens == 0
        assert media.price_usd == 0.0

    def test_negative_tokens_validation(self) -> None:
        """Test Media validation with negative tokens."""
        with pytest.raises(ValidationError, match="Input should be greater than or equal to 0"):
            Media.model_validate(
                {
                    "id": 123,
                    "name": "Invalid",
                    "type": "video",
                    "tokens": -1,
                }
            )


class TestUser:
    """Test User model."""

    def test_default_subgender(self) -> None:
        """Test User model default subgender."""
        user = User.model_validate(
            {
                "username": "test_user",
                "gender": "m",
                "hasTokens": True,
                "inFanclub": False,
                "isMod": False,
                "recentTips": "none",
            }
        )
        assert user.subgender == ""


class TestBaseEvent:
    """Test BaseEvent model."""

    def test_event_type_computed_field(self) -> None:
        """Test BaseEvent.event_type computed field."""
        event = UserEnterEvent.model_validate(
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
                "id": "test-id",
            }
        )
        assert event.event_type == "User Enter"

    def test_flatten_object_data_without_object(self) -> None:
        """Test BaseEvent flattening when no object field is present."""
        event = BaseEvent.model_validate(
            {
                "method": "userEnter",
                "id": "test-id",
                "broadcaster": "test_broadcaster",
            }
        )
        assert event.method == "userEnter"
        assert event.id == "test-id"
        assert event.broadcaster == "test_broadcaster"


class TestEvents:
    """Test event models using parametrization."""

    @pytest.mark.parametrize(
        ("event_class", "method", "additional_fields"),
        [
            (BroadcastStartEvent, EventMethod.BROADCAST_START, {"user": "sample_user"}),
            (BroadcastStopEvent, EventMethod.BROADCAST_STOP, {"user": "sample_user"}),
            (
                ChatMessageEvent,
                EventMethod.CHAT_MESSAGE,
                {"user": "sample_user", "message": "sample_message"},
            ),
            (FanclubJoinEvent, EventMethod.FANCLUB_JOIN, {"user": "sample_user"}),
            (FollowEvent, EventMethod.FOLLOW, {"user": "sample_user"}),
            (
                MediaPurchaseEvent,
                EventMethod.MEDIA_PURCHASE,
                {"user": "sample_user", "media": "sample_media"},
            ),
            (
                PrivateMessageEvent,
                EventMethod.PRIVATE_MESSAGE,
                {"user": "sample_user", "message": "sample_private_message"},
            ),
            (
                RoomSubjectChangeEvent,
                EventMethod.ROOM_SUBJECT_CHANGE,
                {"subject": "New room topic!"},
            ),
            (TipEvent, EventMethod.TIP, {"user": "sample_user", "tip": "sample_tip"}),
            (UnfollowEvent, EventMethod.UNFOLLOW, {"user": "sample_user"}),
            (UserEnterEvent, EventMethod.USER_ENTER, {"user": "sample_user"}),
            (UserLeaveEvent, EventMethod.USER_LEAVE, {"user": "sample_user"}),
        ],
    )
    def test_event_validation(  # noqa: PLR0913
        self,
        event_class: type[BaseEvent],
        method: EventMethod,
        additional_fields: dict[str, str],
        event_base_data: dict[str, Any],
        sample_user: dict[str, Any],
        sample_message: dict[str, Any],
        sample_private_message: dict[str, Any],
        sample_tip: dict[str, Any],
        sample_media: dict[str, Any],
    ) -> None:
        """Test event model validation."""
        # Build the event data
        event_data = {
            "method": method.value,
            **event_base_data,
        }

        # Add fields to the object
        object_data = event_data["object"]

        # Map fixture names to actual data
        fixture_map = {
            "sample_user": sample_user,
            "sample_message": sample_message,
            "sample_private_message": sample_private_message,
            "sample_tip": sample_tip,
            "sample_media": sample_media,
        }

        for field_name, fixture_name in additional_fields.items():
            object_data[field_name] = fixture_map.get(fixture_name, fixture_name)

        # Validate the event
        event = event_class.model_validate(event_data)
        assert event.method == method
        assert event.broadcaster == "test_broadcaster"


class TestEventResponse:
    """Test EventResponse model."""

    def test_event_count_computed_field(self, sample_response: dict[str, Any]) -> None:
        """Test EventResponse.event_count computed field."""
        response = EventResponse.model_validate(sample_response)
        assert response.event_count == 1

    def test_empty_events_list(self) -> None:
        """Test EventResponse with empty events list."""
        response_data = {
            "events": [],
            "nextUrl": "https://example.com/next",
        }
        response = EventResponse.model_validate(response_data)
        assert response.events == []
        assert response.event_count == 0

    def test_multiple_events(self) -> None:
        """Test EventResponse with multiple events."""
        response_data = {
            "events": [
                {
                    "method": "userEnter",
                    "object": {
                        "broadcaster": "test_broadcaster",
                        "user": {
                            "username": "user1",
                            "gender": "m",
                            "hasTokens": True,
                            "inFanclub": False,
                            "isMod": False,
                            "recentTips": "none",
                        },
                    },
                    "id": "enter1",
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
                        "tip": {"tokens": 100, "isAnon": False, "message": "Nice!"},
                    },
                    "id": "tip1",
                },
            ],
            "nextUrl": "https://example.com/next",
        }
        response = EventResponse.model_validate(response_data)
        assert response.event_count == 2
