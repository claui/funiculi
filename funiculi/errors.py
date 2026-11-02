"""Custom error types."""


class FuniculiError(Exception):
    """Base class for all errors raised by funiculi."""


class ConnectionFailed(FuniculiError):
    """The AVR could not be reached, or the connection broke."""


class CliError(FuniculiError):
    """A user-facing error message."""
