"""Version number management."""

from contextlib import suppress
import importlib.metadata
from typing import Union

from .settings import PROJECT_ROOT


def version() -> Union[str, None]:
    """Attempts to return a version number for this project.

    Checks both `pyproject.toml` in the development tree and the
    `importlib.metadata` facility for an installed package, with the
    `pyproject.toml` file taking precedence if it exists.

    :return:
        a version string if one is found, None otherwise.

        The version string may be trailed by an explanation such as
        ` (in development at path/to/project)` if the package is
        invoked from a development tree.
    """
    with suppress(FileNotFoundError, StopIteration):
        with open(
            PROJECT_ROOT / 'pyproject.toml', encoding='utf-8',
        ) as pyproject_toml:
            # Parse manually due to Debian 11 missing a `tomli` package
            version_lines = (
                line for line in pyproject_toml
                if line.startswith('version '))
            return next(version_lines).split('=')[1].strip("'\"\n ") \
                + f' (in development at {PROJECT_ROOT})'
        return importlib.metadata.version(
            __package__ or __name__.split('.', maxsplit=1)[0])
    return None
