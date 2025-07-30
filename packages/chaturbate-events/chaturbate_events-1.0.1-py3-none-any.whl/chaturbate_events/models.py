"""Data models for the Chaturbate Events API."""

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, computed_field, model_validator


class EventMethod(str, Enum):
    """Available event methods."""

    BROADCAST_START = "broadcastStart"
    BROADCAST_STOP = "broadcastStop"
    CHAT_MESSAGE = "chatMessage"
    FANCLUB_JOIN = "fanclubJoin"
    FOLLOW = "follow"
    MEDIA_PURCHASE = "mediaPurchase"
    PRIVATE_MESSAGE = "privateMessage"
    ROOM_SUBJECT_CHANGE = "roomSubjectChange"
    TIP = "tip"
    UNFOLLOW = "unfollow"
    USER_ENTER = "userEnter"
    USER_LEAVE = "userLeave"


class ColorGroup(str, Enum):
    """User color groups."""

    GREY = "a"  # No tokens
    DARK_BLUE = "c"  # Has tokens, tipped recently
    LIGHT_BLUE = "f"  # Has tokens, moderate tipper
    PURPLE = "m"  # Has tokens, big tipper


class Gender(str, Enum):
    """User gender options."""

    MALE = "m"
    FEMALE = "f"
    TRANS = "t"
    COUPLE = "c"


class SubGender(str, Enum):
    """User subgender options."""

    NON_TRANS = ""
    TRANSFEMME = "tf"
    TRANSMASC = "tm"
    NON_BINARY = "tn"


class RecentTips(str, Enum):
    """Recent tipping activity levels."""

    NONE = "none"  # Grey
    SOME = "some"  # Dark blue
    LOTS = "lots"  # Light purple
    TONS = "tons"  # Dark purple


class User(BaseModel):
    """User object from the API."""

    username: str = Field(..., description="Username of the user")
    color_group: ColorGroup | None = Field(
        None, alias="colorGroup", description="User color group based on token status"
    )
    fc_auto_renew: bool | None = Field(
        None, alias="fcAutoRenew", description="Whether fanclub auto-renew is enabled"
    )
    gender: Gender = Field(..., description="User gender")
    has_darkmode: bool | None = Field(
        None, alias="hasDarkmode", description="Whether user has dark mode enabled"
    )
    has_tokens: bool = Field(..., alias="hasTokens", description="Whether user has tokens")
    in_fanclub: bool = Field(..., alias="inFanclub", description="Whether user is in fanclub")
    in_private_show: bool | None = Field(
        None, alias="inPrivateShow", description="Whether user is in private show"
    )
    is_broadcasting: bool | None = Field(
        None, alias="isBroadcasting", description="Whether user is broadcasting"
    )
    is_follower: bool | None = Field(
        None, alias="isFollower", description="Whether user is a follower"
    )
    is_mod: bool = Field(..., alias="isMod", description="Whether user is a moderator")
    is_owner: bool | None = Field(
        None, alias="isOwner", description="Whether user is the room owner"
    )
    is_silenced: bool | None = Field(
        None, alias="isSilenced", description="Whether user is silenced"
    )
    is_spying: bool | None = Field(None, alias="isSpying", description="Whether user is spying")
    language: str | None = Field(None, description="User language preference")
    recent_tips: RecentTips = Field(
        ..., alias="recentTips", description="Recent tipping activity level"
    )
    subgender: SubGender = Field(default=SubGender.NON_TRANS, description="User subgender")


class Message(BaseModel):
    """Message object from the API."""

    message: str = Field(..., description="Message content")
    color: str | None = Field(None, description="Message text color")
    bg_color: str | None = Field(None, alias="bgColor", description="Message background color")
    font: str = Field(default="default", description="Message font")
    from_user: str | None = Field(None, alias="fromUser", description="Sender username")
    to_user: str | None = Field(None, alias="toUser", description="Recipient username")
    orig: str | None = Field(None, description="Original message content")

    @computed_field
    @property
    def is_private(self) -> bool:
        """Check if this is a private message."""
        return self.from_user is not None and self.to_user is not None


class Tip(BaseModel):
    """Tip object from the API."""

    tokens: int = Field(..., gt=0, description="Number of tokens tipped")
    is_anon: bool = Field(..., alias="isAnon", description="Whether tip is anonymous")
    message: str = Field(default="", description="Tip message")

    @computed_field
    @property
    def tip_value_usd(self) -> float:
        """Get approximate USD value (1 token ≈ $0.05)."""
        return self.tokens * 0.05


class Media(BaseModel):
    """Media object from the API."""

    id: int = Field(..., description="Media ID")
    name: str = Field(..., description="Media name")
    type: Literal["photos", "video"] = Field(..., description="Media type")
    tokens: int = Field(..., ge=0, description="Media price in tokens")

    @computed_field
    @property
    def price_usd(self) -> float:
        """Get approximate USD price."""
        return self.tokens * 0.05


class BaseEvent(BaseModel):
    """Base event structure with flattened API data."""

    method: EventMethod = Field(..., description="Event method type")
    id: str = Field(..., description="Event ID")
    broadcaster: str = Field(..., description="Broadcaster username")

    model_config = {
        "use_enum_values": True,
        "extra": "allow",  # Changed from "forbid" to "allow"
        "str_strip_whitespace": True,
    }

    @model_validator(mode="before")
    @classmethod
    def flatten_object_data(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Flatten the nested 'object' field into the main event."""
        if isinstance(data, dict) and "object" in data:
            # Extract the nested object data
            object_data = data["object"]

            # Create flattened data with the object fields merged
            flattened = {
                "method": data.get("method"),
                "id": data.get("id"),
                "raw_object": object_data,  # Use raw_object instead of object
            }

            # Add broadcaster from the object data
            if "broadcaster" in object_data:
                flattened["broadcaster"] = object_data["broadcaster"]

            # Add any additional fields from the object that aren't already present
            for key, value in object_data.items():
                if key not in flattened and key != "broadcaster":
                    flattened[key] = value

            return flattened
        return data

    @computed_field
    @property
    def event_type(self) -> str:
        """Get a human-readable event type."""
        # Convert camelCase to title case with spaces
        import re

        return re.sub(r"([a-z])([A-Z])", r"\1 \2", self.method).title()


# Discriminated Union Events
class BroadcastStartEvent(BaseEvent):
    """Broadcast start event."""

    user: User = Field(..., description="User who started broadcasting")


class BroadcastStopEvent(BaseEvent):
    """Broadcast stop event."""

    user: User = Field(..., description="User who stopped broadcasting")


class ChatMessageEvent(BaseEvent):
    """Chat message event."""

    user: User = Field(..., description="User who sent the message")
    message: Message = Field(..., description="Message content")


class FanclubJoinEvent(BaseEvent):
    """Fanclub join event."""

    user: User = Field(..., description="User who joined the fanclub")


class FollowEvent(BaseEvent):
    """Follow event."""

    user: User = Field(..., description="User who followed")


class MediaPurchaseEvent(BaseEvent):
    """Media purchase event."""

    user: User = Field(..., description="User who purchased media")
    media: Media = Field(..., description="Purchased media")


class PrivateMessageEvent(BaseEvent):
    """Private message event."""

    user: User = Field(..., description="User who sent the private message")
    message: Message = Field(..., description="Private message content")


class RoomSubjectChangeEvent(BaseEvent):
    """Room subject change event."""

    subject: str = Field(..., description="New room subject")


class TipEvent(BaseEvent):
    """Tip event."""

    user: User = Field(..., description="User who tipped")
    tip: Tip = Field(..., description="Tip details")


class UnfollowEvent(BaseEvent):
    """Unfollow event."""

    user: User = Field(..., description="User who unfollowed")


class UserEnterEvent(BaseEvent):
    """User enter event."""

    user: User = Field(..., description="User who entered the room")


class UserLeaveEvent(BaseEvent):
    """User leave event."""

    user: User = Field(..., description="User who left the room")


Event = (
    BroadcastStartEvent
    | BroadcastStopEvent
    | ChatMessageEvent
    | FanclubJoinEvent
    | FollowEvent
    | MediaPurchaseEvent
    | PrivateMessageEvent
    | RoomSubjectChangeEvent
    | TipEvent
    | UnfollowEvent
    | UserEnterEvent
    | UserLeaveEvent
)
"""Event type that can be any of the defined event classes."""


class EventResponse(BaseModel):
    """Response from the events API."""

    events: list[Event] = Field(..., description="List of events")
    next_url: str = Field(..., alias="nextUrl", description="URL for next page of events")

    model_config = {
        "arbitrary_types_allowed": True,
        "extra": "allow",  # Changed from "forbid" to allow extra fields
    }

    @computed_field
    @property
    def event_count(self) -> int:
        """Get the number of events in this response."""
        return len(self.events)
