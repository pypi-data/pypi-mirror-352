"""Errors from borehole.io package."""


class Error(Exception):
    """Top level borehole.io error."""


class UninitializedError(Error):
    """Raised when an object is only partially initialized."""
