# Contributing to Funiculi

## Setting up Funiculi for development

To set up Funiculi, you need the Python project
management tool [uv](https://docs.astral.sh/uv).

### Installing uv

To install uv, see its
[installation instructions](https://docs.astral.sh/uv/getting-started/installation/).

To verify uv is working, run:

```shell
uv
```

## Development scripts and tasks

To see a list of available tasks, run: `uv run poe tasks`

### Running Funiculi

To execute Funiculi, run:

```shell
uv run poe cli
```

### Running the tests

To execute the tests, run:

```shell
uv run poe tests
```

To execute a single test, run e. g.:

```shell
uv run poe tests -vv tests/test_api.py::test_hello
```

To execute tests from VS Code, use the test runner built into the Python extension.
You don’t need _Run tasks_ for executing tests.

### Running the linter

To execute the linter, run:

```shell
uv run poe linter
```

### Running the code formatting style check

To check the code base for formatting style violations that are not
covered by the linter, run:

```shell
uv run poe formatcheck
```

### Running the static type check

To execute the static type check, run:

```shell
uv run poe typecheck
```

### Running the entire CI pipeline locally

If you have [act](https://github.com/nektos/act) installed and a
Docker daemon active, run:

```shell
act
```

### Generating project documentation

To generate project documentation (HTML and man page), run:

```shell
uv run poe doc
```

To open the generated HTML documentation in your browser, run:

```shell
uv run poe html
```

To open the generated manual page in your terminal, run:

```shell
uv run poe man
```

## Maintenance

### Refreshing dependencies

If you get errors after a Git pull, refresh your dependencies:

```shell
uv sync
```

### Checking Funiculi’s dependencies for compatible updates

To check Funiculi’s dependencies for compatible updates, run:

```shell
uv lock -U --dry-run
```

### Updating requirements file for Read the Docs

To update the `doc/requirements.txt` file for Read the Docs, run:

```shell
uv export --only-group doc --output-file doc/requirements.txt
```
