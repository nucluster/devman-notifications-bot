class NoTokenError(Exception):
    """No API token exception."""


class NotCorrectAPIResponse(Exception):
    """Not corrext API response."""


class NotOkStatusCode(Exception):
    """Not OK http status."""


class NotCorrectKey(KeyError):
    """Not correct key."""


class NotCorrectResponseType(TypeError):
    """Not correct response type."""
