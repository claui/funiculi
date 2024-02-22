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

See [`USAGE.md`](https://github.com/claui/funiculi/blob/main/USAGE.md) or `man 1 funiculi` for details.

## Contributing to Funiculi

See [`CONTRIBUTING.md`](https://github.com/claui/funiculi/blob/main/CONTRIBUTING.md).

## License

Copyright (c) 2024 Claudia Pellegrino

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
For a copy of the License, see [LICENSE](LICENSE).
