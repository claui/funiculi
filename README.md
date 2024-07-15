# Funiculi

Funiculi is a tiny command-line utility which lets you interact with
Denon AVR amplifiers over your local network.

It currently supports turning the unit on and off, querying its
power status, changing its volume, and streaming music to it over
[DLNA](https://en.wikipedia.org/wiki/DLNA).

## Prerequisites

You need the following software installed on your system:

- [`ncat`](https://github.com/nmap/nmap/tree/master/ncat#readme)

- [`pulseaudio-dlna`](https://github.com/Cygn/pulseaudio-dlna)

## Installation

### Installing from PyPI

To install Funiculi from PyPI, open a shell and run:

```shell
pip install funiculi
```

If that doesn’t work, try:

```shell
python3 -m pip install funiculi
```

### Installing from the AUR

Direct your favorite
[AUR helper](https://wiki.archlinux.org/title/AUR_helpers) to the
`funiculi` package.

## Usage

```shell
funiculi [FLAGS] COMMAND
```

`COMMAND` is one of the following:

- `off`  
  Turns the device off.

- `on`  
  Turns the device on.

- `down`  
  Turns the volume down one step.

- `up`  
  Turns the volume up one step.

- `source [get | set NAME]`  
  Selects or queries the audio source.

- `status`  
  Queries whether the device is on standby.

- `dlna`  
  Sets up a local virtual output device that relays all audio to the
  receiver via DLNA.

See [`USAGE.md`](https://github.com/claui/funiculi/blob/main/USAGE.md) or `man 1 funiculi` for details.

## Contributing to Funiculi

See [`CONTRIBUTING.md`](https://github.com/claui/funiculi/blob/main/CONTRIBUTING.md).

## License

Copyright (c) 2024 Claudia Pellegrino

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
For a copy of the License, see [LICENSE](LICENSE).
