"""A place for shared paths and settings."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.absolute()
PACKAGE_ROOT = Path(__file__).parent.absolute()
PYPROJECT_TOML = PROJECT_ROOT / 'pyproject.toml'

DEFAULT_AVR_CTRL_PORT = 23
DEFAULT_AVR_WEB_PORT = 60006
DEFAULT_CTRL_TIMEOUT_MS = 100
DEFAULT_UPNP_DESCRIPTOR_REMOTE_PATH = '/upnp/desc/aios_device/aios_device.xml'
