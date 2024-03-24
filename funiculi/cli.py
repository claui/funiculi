"""Entry point for the command line interface."""

from contextlib import contextmanager
import os
import sys
from typing import Generator, List, NoReturn

import fire  # type: ignore

from . import __version__, api, fire_workarounds
from .errors import CliError
from .logging import get_logger
from .settings import debugMode, PROJECT_ROOT, PYPROJECT_TOML


logger = get_logger(__name__)


def run(*args: str) -> None:
    """Runs the command line interface."""
    with _cli_context(*args) as combined_args:
        fire.Fire(api.Api, command=combined_args)


@contextmanager
def _cli_context(*args: str) -> Generator[List[str], None, NoReturn]:
    combined_args = list(args) + sys.argv[1:]
    if combined_args and combined_args[0] in {'-V', '--version'}:
        print(_version_text())
        sys.exit(0)

    fire_workarounds.apply()
    try:
        yield combined_args
    except CliError as e:
        if debugMode:
            raise e
        logger.error(e)
        sys.exit(1)
    sys.exit(0)


def _version_text() -> str:
    if __version__ is None:
        return 'Funiculi (unknown version)'
    if os.path.exists(PYPROJECT_TOML):
        return (
            f'Funiculi v{__version__}'
            + f' (in development at {PROJECT_ROOT})'
        )
    return f'Funiculi v{__version__}'
