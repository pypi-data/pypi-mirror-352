"""Chaturbate Events API Python wrapper."""

import importlib.metadata

from .client import ChaturbateEventsClient
from .exceptions import APIError, AuthenticationError, ChaturbateEventsError
from .models import (
    BaseEvent,
    BroadcastStartEvent,
    BroadcastStopEvent,
    ChatMessageEvent,
    Event,
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

__version__ = importlib.metadata.version(distribution_name="chaturbate_events")
__author__ = "MountainGod2"
__author_email__ = "admin@reid.ca"
__maintainer__ = "MountainGod2"
__maintainer_email__ = "admin@reid.ca"
__license__ = "MIT"
__url__ = "https://github.com/MountainGod2/chaturbate_events"
__description__ = "Chaturbate Events API Python wrapper."

__all__ = [
    "APIError",
    "AuthenticationError",
    "BaseEvent",
    "BroadcastStartEvent",
    "BroadcastStopEvent",
    "ChatMessageEvent",
    "ChaturbateEventsClient",
    "ChaturbateEventsError",
    "Event",
    "EventMethod",
    "EventResponse",
    "FanclubJoinEvent",
    "FollowEvent",
    "Media",
    "MediaPurchaseEvent",
    "Message",
    "PrivateMessageEvent",
    "RoomSubjectChangeEvent",
    "Tip",
    "TipEvent",
    "UnfollowEvent",
    "User",
    "UserEnterEvent",
    "UserLeaveEvent",
]
