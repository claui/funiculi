"""Funiculi’s primary package."""

# Re-export these symbols
# (This promotes them from funiculi.api to funiculi)
from funiculi.api import Api as Api

from funiculi.version import version


__all__ = [
    # Modules that every subpackage should see
    'settings',
]

__version__ = version()
