# pylint: disable=magic-value-comparison, missing-function-docstring, missing-module-docstring, no-self-use, too-few-public-methods, too-many-public-methods

import asyncio
import threading
from collections.abc import Iterator

import pytest

from funiculi import Api, AsyncApi
from funiculi.errors import CliError, ConnectionFailed


class FakeDenon:
    """An asyncio stand-in for a Denon AVR telnet endpoint."""

    def __init__(self) -> None:
        self.power = 'PWSTANDBY'
        self.source = 'TV'
        self.volume = 40
        self.port: int | None = None
        self.commands: list[str] = []

    def respond(self, command: str) -> str | None:
        self.commands.append(command)
        if command == 'PW?':
            return self.power
        if command == 'PWON':
            self.power = 'PWON'
        elif command == 'PWSTANDBY':
            self.power = 'PWSTANDBY'
        elif command == 'SI?':
            return f'SI{self.source}'
        elif command.startswith('SI'):
            self.source = command[2:]
        elif command == 'MV?':
            return f'MV{self.volume:02}'
        elif command == 'MVUP':
            self.volume += 1
        elif command == 'MVDOWN':
            self.volume -= 1
        return None

    async def handle(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        try:
            line = await reader.readuntil(b'\r')
        except (asyncio.IncompleteReadError, ConnectionError):
            writer.close()
            return
        command = line.decode('ascii').strip()
        if (response := self.respond(command)) is not None:
            writer.write((response + '\r').encode('ascii'))
            await writer.drain()
        writer.close()


@pytest.fixture(name='avr')
def fixture_avr() -> Iterator[FakeDenon]:
    denon = FakeDenon()
    loop = asyncio.new_event_loop()
    server = loop.run_until_complete(
        asyncio.start_server(denon.handle, '127.0.0.1', 0)
    )
    sockets = server.sockets
    assert sockets is not None
    denon.port = sockets[0].getsockname()[1]
    thread = threading.Thread(target=loop.run_forever, daemon=True)
    thread.start()
    yield denon
    loop.call_soon_threadsafe(server.close)
    loop.call_soon_threadsafe(loop.stop)
    thread.join(timeout=5)
    loop.close()


def make_api(avr: FakeDenon) -> Api:
    assert avr.port is not None
    return Api(host='127.0.0.1', ctrlport=avr.port, timeout=1000)


def make_async_api(avr: FakeDenon) -> AsyncApi:
    assert avr.port is not None
    return AsyncApi(host='127.0.0.1', ctrlport=avr.port, timeout=1000)


def test_sanity(avr: FakeDenon) -> None:
    assert make_api(avr) is not None


def test_status_reports_standby(avr: FakeDenon) -> None:
    assert make_api(avr).status() == 'PWSTANDBY'


def test_on_and_off_round_trip(avr: FakeDenon) -> None:
    api = make_api(avr)
    api.on()
    assert api.status() == 'PWON'
    api.off()
    assert api.status() == 'PWSTANDBY'


def test_volume_steps_reach_the_device(avr: FakeDenon) -> None:
    api = make_api(avr)
    api.up()
    assert avr.volume == 41
    api.down()
    api.down()
    assert avr.volume == 39


def test_source_get_and_set(avr: FakeDenon) -> None:
    api = make_api(avr)
    assert api.source.get() == 'TV'
    api.source.set('aux')
    assert avr.source == 'AUX'
    assert api.source.get() == 'AUX'


def test_async_api_round_trip(avr: FakeDenon) -> None:
    async def scenario() -> tuple[str, str]:
        api = make_async_api(avr)
        before = await api.status()
        await api.on()
        after = await api.status()
        return before, after

    assert asyncio.run(scenario()) == ('PWSTANDBY', 'PWON')


def test_async_source_get_and_set(avr: FakeDenon) -> None:
    async def scenario() -> tuple[str, str]:
        api = make_async_api(avr)
        before = await api.source.get()
        await api.source.set('phono')
        after = await api.source.get()
        return before, after

    assert asyncio.run(scenario()) == ('TV', 'PHONO')


def test_connection_failure_raises() -> None:
    api = Api(host='127.0.0.1', ctrlport=1, timeout=200)
    with pytest.raises(ConnectionFailed):
        api.status()


def test_missing_host_raises_cli_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv('AVR_HOST', raising=False)
    with pytest.raises(CliError):
        Api()
