"""The primary async module in funiculi."""

import os
from collections.abc import Awaitable, Callable

from .connection import Connection
from .errors import CliError, NoResponse
from .settings import DEFAULT_AVR_CTRL_PORT, DEFAULT_CTRL_TIMEOUT_MS

VOLUME_MIN = 0.0
VOLUME_MAX = 98.0
VOLUME_MAX_PAYLOAD = 'MAX'


def parse_volume(payload: str) -> float:
    """Parses a master volume payload per Denon’s protocol.

    :param payload:
        The response payload without the `MV` prefix, e.g. `40` or
        `40.5` or `MAX`.

    :return: The volume level between 0 and 98.

    :raises ValueError: if the payload is not a volume level.
    """
    if payload == VOLUME_MAX_PAYLOAD:
        return VOLUME_MAX
    try:
        return float(payload)
    except ValueError as error:
        raise ValueError(f'Not a volume level: {payload}') from error


def format_volume(level: float) -> str:
    """Formats a master volume level per Denon’s protocol.

    :param level: The volume level between 0 and 98.

    :return: The payload without the `MV` prefix, e.g. `40` or `40.5`.

    :raises ValueError: if `level` is out of range.
    """
    if not VOLUME_MIN <= level <= VOLUME_MAX:
        raise ValueError(
            f'Volume level out of range: {level}'
            f' ({VOLUME_MIN:g}–{VOLUME_MAX:g})'
        )
    return f'{level:g}'


class AsyncVolumeApi:
    """Queries or sets the master volume."""

    def __init__(
        self, send: Callable[[str], Awaitable[str | None]]
    ) -> None:
        self._send = send

    async def get(self) -> float | None:
        """Queries the master volume level.

        :return:
            The volume level between 0 and 98, or `None` if the AVR
            did not respond.
        """
        response = await self._send('MV?')
        if response is None or not response.startswith('MV'):
            return None
        return parse_volume(response[2:])

    async def set(self, level: float) -> None:
        """Sets the master volume level.

        :param level: The volume level between 0 and 98.

        :raises ValueError: if `level` is out of range.

        :raises NoResponse:
            if the AVR sent no acknowledgment, e.g. because it is
            on standby.
        """
        payload = f'MV{format_volume(level)}'
        if await self._send(payload) is None:
            raise NoResponse(f'The AVR did not acknowledge {payload}.')

    async def down(self) -> None:
        """Turns the volume down one step."""
        await self._send('MVDOWN')

    async def up(self) -> None:
        """Turns the volume up one step."""
        await self._send('MVUP')


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

    async def set(self, name: str) -> None:
        """Selects an audio source.

        :param name:
            Source name according to Denon’s protocol.
            This parameter is case-insensitive.
            Acceptable values vary by model. To find out the values
            for a specific model, omit this parameter while your
            device is set to a known source. Repeat for each source.

        :raises NoResponse:
            if the AVR sent no acknowledgment, e.g. because it is
            on standby.
        """
        if await self._send(f'SI{name.upper()}') is None:
            raise NoResponse(
                f'The AVR did not acknowledge source {name.upper()}.'
            )


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

    volume: AsyncVolumeApi
    """Queries or sets the master volume."""

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
        self.volume = AsyncVolumeApi(self._send)

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

    async def _send(self, payload: str) -> str | None:
        async with Connection(
            self._avr_host, self._avr_ctrl_port, self._timeout_s
        ) as connection:
            return await connection.send(payload)
