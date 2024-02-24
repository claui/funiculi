"""
.. include:: ../README.md

## API Documentation
"""

# Re-export these symbols
# (This promotes them from funiculi.api to funiculi)
from funiculi.api import Api as Api

from funiculi.version import version


__all__ = [
    # Tell pdoc to pick up all re-exported symbols
    'Api',

    # Modules that every subpackage should see
    # (This also exposes them to pdoc)
    'api',
    'settings',
]

__version__ = version()
