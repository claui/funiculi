"""The asyncio transport for Denon’s telnet control protocol."""

import asyncio

from .errors import ConnectionFailed
from .logging import get_logger
from .settings import DEFAULT_AVR_CTRL_PORT, DEFAULT_CTRL_TIMEOUT_MS

logger = get_logger(__name__)


class Connection:
    """A short-lived telnet connection to a Denon AVR.

    :param host: The AVR host to connect to.

    :param port: The AVR control port to connect to.

    :param timeout:
        The timeout for the connection attempt and for each
        command’s response, in seconds.
    """

    def __init__(
        self,
        host: str,
        port: int = DEFAULT_AVR_CTRL_PORT,
        timeout: float = DEFAULT_CTRL_TIMEOUT_MS / 1000,
    ) -> None:
        self._host = host
        self._port = port
        self._timeout = timeout
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None

    async def __aenter__(self) -> 'Connection':
        await self.open()
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.close()

    async def open(self) -> None:
        """Opens the connection to the AVR.

        :raises ConnectionFailed:
            if the connection cannot be established within the
            timeout.
        """
        try:
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port),
                self._timeout,
            )
        except OSError as error:
            raise ConnectionFailed(
                f'Cannot connect to {self._host}:{self._port} ({error})'
            ) from error

    async def close(self) -> None:
        """Closes the connection, ignoring teardown failures."""
        writer = self._writer
        self._reader = None
        self._writer = None
        if writer is None:
            return
        writer.close()
        try:
            await writer.wait_closed()
        except OSError:
            pass

    async def send(self, payload: str) -> str | None:
        """Sends one command and awaits a single response line.

        Response lines are terminated by a bare carriage return,
        per Denon’s protocol.

        :param payload:
            The protocol command, without a line terminator.

        :return:
            The first response line, stripped of its terminator, or
            `None` if the AVR sent nothing within the timeout (the
            normal case for commands that merely act rather than
            answer).

        :raises ConnectionFailed: if the connection breaks.
        """
        if self._reader is None or self._writer is None:
            raise ConnectionFailed('Not connected.')
        logger.debug('Sending command: %s', payload)
        self._writer.write((payload + '\r').encode('ascii'))
        await self._writer.drain()
        try:
            line = await asyncio.wait_for(
                self._reader.readuntil(b'\r'), self._timeout
            )
        except asyncio.TimeoutError:
            return None
        except asyncio.IncompleteReadError as error:
            # A clean EOF without any response is the AVR’s usual
            # silence after commands that act rather than answer;
            # a truncated line, however, means a broken connection.
            if error.partial:
                raise ConnectionFailed(
                    f'Connection to {self._host}:{self._port} broke'
                    f' ({error})'
                ) from error
            return None
        except OSError as error:
            raise ConnectionFailed(
                f'Connection to {self._host}:{self._port} broke'
                f' ({error})'
            ) from error
        response = line.decode('ascii', errors='replace').strip()
        logger.debug('Received response: %s', response)
        return response
