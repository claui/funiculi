# Funiculi

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

The following flags are supported:

- `-h`, `--host=HOST`  
  The AVR host to connect to.  
  Mandatory if no `AVR_HOST` environment variable is defined.  
  The parameter takes precedence over the environment variable.

- `-c`, `--ctrlport=CTRLPORT`  
  Default: 23  
  The AVR control port to connect to.

- `-w`, `--webport=WEBPORT`  
  Default: 60006  
  The AVR web port from which to obtain DLNA metadata.

- `-t, --timeout=TIMEOUT`  
  Default: 100  
  The timeout for commands in milliseconds.

- `-p`, `--path=PATH`  
  Default: `/upnp/desc/aios_device/aios_device.xml`  
  The remote path to the UPnP XML descriptor.

`COMMAND` is one of the following:

- `off`  
  Turns the device off.

- `on`  
  Turns the device on.

- `down`  
  Turns the volume down one step.

- `up`  
  Turns the volume up one step.

- `status`  
  Queries whether the device is on standby.

- `dlna`  
  Sets up a local virtual output device that relays all audio to the
  receiver via DLNA.

## Contributing to Funiculi

See [`CONTRIBUTING.md`](https://github.com/claui/funiculi/blob/main/CONTRIBUTING.md).

## License

Copyright (c) 2024 Claudia Pellegrino

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
For a copy of the License, see [LICENSE](LICENSE).
