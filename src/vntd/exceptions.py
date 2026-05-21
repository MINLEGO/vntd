class VintedError(Exception):
    """Base exception for all errors raised by the Vinted client."""


class InvalidValue(VintedError):
    """Raised when a provided value is invalid or improperly formatted."""


class RequestError(VintedError):
    """Raised when an HTTP request fails with a non-success status code."""


class AccessDeniedError(RequestError):
    """Raised when access is blocked by anti-bot protection."""


class NotFoundError(VintedError):
    """Raised when a user or item is not found."""
