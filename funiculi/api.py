"""The primary module in funiculi."""

import os
import socket
import subprocess
import tempfile
from typing import Optional

from .errors import CliError

from .settings import \
    DEFAULT_AVR_CTRL_PORT, DEFAULT_AVR_WEB_PORT, \
    DEFAULT_CTRL_TIMEOUT_MS, DEFAULT_UPNP_DESCRIPTOR_REMOTE_PATH


class Api:
    """
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

    def __init__(self,  # pylint: disable=too-many-arguments
        host: Optional[str]=None,
        ctrlport: int=DEFAULT_AVR_CTRL_PORT,
        webport: int=DEFAULT_AVR_WEB_PORT,
        timeout: float=DEFAULT_CTRL_TIMEOUT_MS,
        path: str=DEFAULT_UPNP_DESCRIPTOR_REMOTE_PATH,
    ) -> None:
        if (merged_host := host or os.environ.get('AVR_HOST', None)) is None:
            raise CliError('The `--host` switch must be given if ' +
                'no `AVR_HOST` environment variable is defined.')
        self._avr_host = merged_host
        self._avr_ctrl_port = ctrlport
        self._avr_web_port = webport
        self._timeout_ms = timeout
        self._upnp_descriptor_path = path


    def off(self) -> None:
        """Turns the device off."""
        self._send('PWSTANDBY')


    def on(self) -> None:
        """Turns the device on."""
        self._send('PWON')


    def status(self) -> str:
        """Queries whether the device is on standby.

        :return:
            `PWSTANDBY` if it is on standby, `PWON` if it is turned
            on.
        """
        return self._send('PW?')

    def down(self) -> None:
        """Turns the volume down one step."""
        self._send('MVDOWN')

    def up(self) -> None:
        """Turns the volume up one step."""
        self._send('MVUP')

    def dlna(self) -> None:
        """Sets up a local virtual output device that relays all audio
        to the receiver via DLNA."""
        try:
            avr_host_ipv4_addr = socket.gethostbyname(self._avr_host)
        except OSError as e:
            raise CliError(f'{e.strerror} ({self._avr_host})') from e
        subprocess.run(
            [
                'pulseaudio-dlna',
                '--renderer-urls',
                f'http://{avr_host_ipv4_addr}:{self._avr_web_port}' \
                    + self._upnp_descriptor_path
            ],
            check=True)

    def _send(self, payload: str) -> str:
        f = tempfile.NamedTemporaryFile(  # pylint: disable=consider-using-with
            mode='w', encoding='ascii', suffix='.funiculi.status',
            delete=False)
        f.close()
        process = subprocess.run(
            [
                'timeout', str(self._timeout_ms / 1000), 'ncat',
                '-C', '-o', f.name, '--no-shutdown', self._avr_host,
                str(self._avr_ctrl_port),
            ],
            capture_output=True, check=False, encoding='ascii',
            input=payload, text=True)
        os.remove(f.name)
        if process.returncode not in (0, 124):
            process.check_returncode()
        return os.linesep.join(process.stdout.splitlines())
