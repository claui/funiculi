"""Entry point for the command line interface."""

import sys
from typing import NoReturn

import fire  # type: ignore

from . import __version__, api, fire_workarounds
from .errors import CliError
from .logging import get_logger


logger = get_logger(__name__)


def run(*args: str) -> NoReturn:
    # pylint: disable=magic-value-comparison
    """Runs the command line interface."""

    if sys.argv[1:] and sys.argv[1:][0] in {'-V', '--version'}:
        if __version__ is None:
            print('Funiculi (unknown version)')
        else:
            print(f'Funiculi v{__version__}')
        sys.exit(0)

    fire_workarounds.apply()
    try:
        fire.Fire(api.Api, command=list(args) + sys.argv[1:])
    except CliError as e:
        logger.error(e)
        sys.exit(1)
    sys.exit(0)
