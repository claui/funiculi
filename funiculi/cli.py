"""Entry point for the command line interface."""

import sys
from typing import NoReturn

import fire  # type: ignore

from . import api
from . import fire_workarounds
from .errors import CliError
from .logging import get_logger


logger = get_logger(__name__)


def run(*args: str) -> NoReturn:
    """Runs the command line interface."""
    fire_workarounds.apply()
    try:
        fire.Fire(api.Api, command=list(args) + sys.argv[1:])
    except CliError as e:
        logger.error(e)
        sys.exit(1)
    sys.exit(0)
