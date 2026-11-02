"""The primary async module in funiculi."""

import os
from collections.abc import Awaitable, Callable

from .connection import Connection
from .errors import CliError
from .settings import DEFAULT_AVR_CTRL_PORT, DEFAULT_CTRL_TIMEOUT_MS


class AsyncSourceApi:
    """Selects or queries the audio source."""

    def __init__(
        self, send: Callable[[str], Awaitable[str | None]]
    ) -> None:
        self._send = send

    async def get(self) -> str:
        """Queries the current audio source.

        :return:
            The source name, or an empty string if the AVR did not
            respond.
        """
        return (await self._send('SI?') or '')[2:]

    async def set(self, name: str) -> str | None:
        """Selects an audio source.

        :param name:
            Source name according to Denon’s protocol.
            This parameter is case-insensitive.
            Acceptable values vary by model. To find out the values
            for a specific model, omit this parameter while your
            device is set to a known source. Repeat for each source.
        """
        return await self._send(f'SI{name.upper()}')


class AsyncApi:
    """Asynchronously controls a Denon AVR over its telnet protocol.

    :param host:
        The AVR host to connect to.

        Mandatory if no `AVR_HOST` environment variable is defined.
        This parameter takes precedence over the environment variable.

    :param ctrlport:
        The AVR control port to connect to.

    :param timeout:
        The timeout for commands in milliseconds.
    """

    source: AsyncSourceApi
    """Selects or queries the audio source."""

    def __init__(
        self,
        host: str | None = None,
        ctrlport: int = DEFAULT_AVR_CTRL_PORT,
        timeout: float = DEFAULT_CTRL_TIMEOUT_MS,
    ) -> None:
        if (
            merged_host := host or os.environ.get('AVR_HOST', None)
        ) is None:
            raise CliError(
                'The `--host` switch must be given if '
                + 'no `AVR_HOST` environment variable is defined.'
            )
        self._avr_host = merged_host
        self._avr_ctrl_port = ctrlport
        self._timeout_s = timeout / 1000
        self.source = AsyncSourceApi(self._send)

    @property
    def host(self) -> str:
        """The AVR host this API connects to."""
        return self._avr_host

    async def off(self) -> None:
        """Turns the device off."""
        await self._send('PWSTANDBY')

    async def on(self) -> None:
        """Turns the device on."""
        await self._send('PWON')

    async def status(self) -> str:
        """Queries whether the device is on standby.

        :return:
            `PWSTANDBY` if it is on standby, `PWON` if it is turned
            on, or an empty string if the AVR did not respond.
        """
        return await self._send('PW?') or ''

    async def down(self) -> None:
        """Turns the volume down one step."""
        await self._send('MVDOWN')

    async def up(self) -> None:
        """Turns the volume up one step."""
        await self._send('MVUP')

    async def _send(self, payload: str) -> str | None:
        async with Connection(
            self._avr_host, self._avr_ctrl_port, self._timeout_s
        ) as connection:
            return await connection.send(payload)
