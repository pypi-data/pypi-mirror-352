"""Exception classes for the Chaturbate Events API."""


class ChaturbateEventsError(Exception):
    """Base exception for all Chaturbate Events API errors."""


class APIError(ChaturbateEventsError):
    """Raised when the API returns an error response."""


class AuthenticationError(APIError):
    """Raised when authentication fails."""
