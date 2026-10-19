class VintedError(Exception):
    """Base exception for all errors raised by the Vinted client."""


class InvalidValue(VintedError):
    """Raised when a provided value is invalid or improperly formatted."""


class RequestError(VintedError):
    """Raised when an HTTP request fails, with a non-success status code or at the transport level."""


class RequestTimeout(RequestError):
    """Raised when a request times out."""


class AccessDeniedError(RequestError):
    """Raised when access is blocked by anti-bot protection."""


class NotFoundError(VintedError):
    """Raised when a user or item is not found (HTTP 404/410)."""


class ParseError(VintedError):
    """Raised when a response was fetched but its data could not be decoded."""
