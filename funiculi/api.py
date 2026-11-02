"""The primary module in funiculi."""

import asyncio
import socket
import subprocess

from .async_api import AsyncApi, AsyncSourceApi
from .errors import CliError
from .settings import (
    DEFAULT_AVR_CTRL_PORT,
    DEFAULT_AVR_WEB_PORT,
    DEFAULT_CTRL_TIMEOUT_MS,
    DEFAULT_UPNP_DESCRIPTOR_REMOTE_PATH,
)


class SourceApi:
    """Selects or queries the audio source."""

    def __init__(self, source: AsyncSourceApi) -> None:
        self._source = source

    def get(self) -> str:
        """Queries the current audio source."""
        return asyncio.run(self._source.get())

    def set(self, name: str) -> str | None:
        """Selects an audio source.

        :param name:
            Source name according to Denon’s protocol.
            This parameter is case-insensitive.
            Acceptable values vary by model. To find out the values
            for a specific model, omit this parameter while your
            device is set to a known source. Repeat for each source.
        """
        return asyncio.run(self._source.set(name))


class Api:
    """Controls a Denon AVR over its telnet protocol.

    :param host:
        The AVR host to connect to.

        Mandatory if no `AVR_HOST` environment variable is defined.
        This parameter takes precedence over the environment variable.

    :param ctrlport:
        The AVR control port to connect to.

    :param webport:
        The AVR web port from which to obtain DLNA metadata.

    :param timeout:
        The timeout for commands in milliseconds.

    :param path:
        The remote path to the UPnP XML descriptor.
    """

    source: SourceApi
    """Selects or queries the audio source."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        host: str | None = None,
        ctrlport: int = DEFAULT_AVR_CTRL_PORT,
        webport: int = DEFAULT_AVR_WEB_PORT,
        timeout: float = DEFAULT_CTRL_TIMEOUT_MS,
        path: str = DEFAULT_UPNP_DESCRIPTOR_REMOTE_PATH,
    ) -> None:
        self._async_api = AsyncApi(host, ctrlport, timeout)
        self._avr_host = self._async_api.host
        self._avr_web_port = webport
        self._upnp_descriptor_path = path
        self.source = SourceApi(self._async_api.source)

    def off(self) -> None:
        """Turns the device off."""
        asyncio.run(self._async_api.off())

    def on(self) -> None:
        """Turns the device on."""
        asyncio.run(self._async_api.on())

    def status(self) -> str:
        """Queries whether the device is on standby.

        :return:
            `PWSTANDBY` if it is on standby, `PWON` if it is turned
            on.
        """
        return asyncio.run(self._async_api.status())

    def down(self) -> None:
        """Turns the volume down one step."""
        asyncio.run(self._async_api.down())

    def up(self) -> None:
        """Turns the volume up one step."""
        asyncio.run(self._async_api.up())

    def dlna(self) -> None:
        """Sets up a local virtual output device that relays all audio
        to the receiver via DLNA."""
        try:
            avr_host_ipv4_addr = socket.gethostbyname(self._avr_host)
        except OSError as e:
            raise CliError(f'{e.strerror} ({self._avr_host})') from e
        try:
            subprocess.run(
                [
                    'pulseaudio-dlna',
                    '--renderer-urls',
                    f'http://{avr_host_ipv4_addr}:{self._avr_web_port}'
                    + self._upnp_descriptor_path,
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise CliError(e) from e
