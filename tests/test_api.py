# pylint: disable=magic-value-comparison, missing-function-docstring, missing-module-docstring, no-self-use, too-few-public-methods, too-many-public-methods

import asyncio
import threading
from collections.abc import Iterator

import pytest

from funiculi import Api, AsyncApi
from funiculi.errors import CliError, ConnectionFailed, NoResponse


class FakeDenon:
    """An asyncio stand-in for a Denon AVR telnet endpoint."""

    def __init__(self) -> None:
        self.power = 'PWSTANDBY'
        self.source = 'TV'
        self.volume: float = 40
        self.port: int | None = None
        self.commands: list[str] = []

    def respond(self, command: str) -> str | None:
        self.commands.append(command)
        if command.startswith('SI'):
            return self._source_command(command)
        if command.startswith('MV'):
            return self._volume_command(command)
        return self._power_command(command)

    def _power_command(self, command: str) -> str | None:
        if command == 'PW?':
            return self.power
        if command in {'PWON', 'PWSTANDBY'}:
            self.power = command
        return None

    def _source_command(self, command: str) -> str | None:
        if command == 'SI?':
            return f'SI{self.source}'
        return self._select_source(command)

    def _volume_command(self, command: str) -> str | None:
        if command == 'MV?':
            return f'MV{self.volume:g}'
        if command == 'MVUP':
            return self._step_volume(1)
        if command == 'MVDOWN':
            return self._step_volume(-1)
        return self._set_volume(command)

    def _select_source(self, command: str) -> str | None:
        if self.power != 'PWON':
            return None
        self.source = command[2:]
        return command

    def _step_volume(self, delta: int) -> str | None:
        if self.power == 'PWON':
            self.volume += delta
        return f'MV{self.volume:g}'

    def _set_volume(self, command: str) -> str | None:
        if self.power != 'PWON':
            return None
        self.volume = float(command[2:])
        return command

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
    api.on()
    api.up()
    assert avr.volume == 41
    api.down()
    api.down()
    assert avr.volume == 39


def test_volume_steps_via_sub_api(avr: FakeDenon) -> None:
    api = make_api(avr)
    api.on()
    api.volume.up()
    assert avr.volume == 41
    api.volume.down()
    assert avr.volume == 40


def test_source_get_and_set(avr: FakeDenon) -> None:
    api = make_api(avr)
    assert api.source.get() == 'TV'
    with pytest.raises(NoResponse):
        api.source.set('aux')
    api.on()
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
        await api.on()
        await api.source.set('phono')
        after = await api.source.get()
        return before, after

    assert asyncio.run(scenario()) == ('TV', 'PHONO')


def test_volume_get_and_set(avr: FakeDenon) -> None:
    api = make_api(avr)
    assert api.volume.get() == 40
    with pytest.raises(NoResponse):
        api.volume.set(40.5)
    api.on()
    api.volume.set(40.5)
    assert avr.volume == 40.5
    assert api.volume.get() == 40.5


def test_volume_set_out_of_range(avr: FakeDenon) -> None:
    api = make_api(avr)
    with pytest.raises(ValueError, match='out of range'):
        api.volume.set(99)


def test_async_volume_get_and_set(avr: FakeDenon) -> None:
    async def scenario() -> tuple[float | None, float | None]:
        api = make_async_api(avr)
        before = await api.volume.get()
        await api.on()
        await api.volume.set(12)
        after = await api.volume.get()
        return before, after

    assert asyncio.run(scenario()) == (40, 12)


def test_async_setters_raise_no_response_in_standby(
    avr: FakeDenon,
) -> None:
    async def scenario() -> None:
        api = make_async_api(avr)
        with pytest.raises(NoResponse):
            await api.volume.set(10)
        with pytest.raises(NoResponse):
            await api.source.set('TV')

    asyncio.run(scenario())


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
