"""Custom error types."""


class FuniculiError(Exception):
    """Base class for all errors raised by funiculi."""


class ConnectionFailed(FuniculiError):
    """The AVR could not be reached, or the connection broke."""


class NoResponse(FuniculiError):
    """The AVR ignored a command it normally acknowledges.

    The amp silently drops commands such as `MV<level>` or
    `SI<name>` while it is on standby, so a missing acknowledgment
    usually means the unit is off.
    """


class CliError(FuniculiError):
    """A user-facing error message."""
