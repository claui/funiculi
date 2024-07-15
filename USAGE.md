<!-- markdownlint-configure-file { "MD041": { "level": 1 } } -->

# Synopsis

```shell
funiculi [FLAGS] COMMAND
```

# Commands

`COMMAND` is one of the following:

`off`
: Turns the device off.

`on`
: Turns the device on.

`down`
: Turns the volume down one step.

`up`
: Turns the volume up one step.

`source [get | set NAME]`
: Selects or queries the audio source.
The `get` subcommand returns the current source.
The `set` subcommand accepts a source name according to Denon’s
protocol; the name is case-insensitive.
Acceptable values vary by model. To find out the values for a
specific model, omit this parameter while your device is set to a
known source. Repeat for each source.

`status`
: Queries whether the device is on standby.

`dlna`
: Sets up a local virtual output device that relays all audio to the
: receiver via DLNA.

# Flags

The following flags are supported:

## `-h`, `--host=HOST`

The AVR host to connect to.

Mandatory if no `AVR_HOST` environment variable is defined.

The parameter takes precedence over the environment variable.

## `-c`, `--ctrlport=CTRLPORT`

The AVR control port to connect to.

The default is 23.

## `-w`, `--webport=WEBPORT`

The AVR web port from which to obtain DLNA metadata.

The default is 60006.

## `-t, --timeout=TIMEOUT`

The timeout for commands in milliseconds.

The default timeout is 100 ms.

## `-p`, `--path=PATH`

The remote path to the UPnP XML descriptor.

The default value is: `/upnp/desc/aios_device/aios_device.xml`
