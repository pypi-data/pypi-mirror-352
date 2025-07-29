# Python: Go2rtc client

Asynchronous Python client for [go2rtc][go2rtc].

## About

This package allows you to communicate with a [go2rtc][go2rtc] server.

## Installation

```bash
uv pip install go2rtc-client
```

## Changelog & Releases

This repository keeps a change log using [GitHub's releases][releases]
functionality. The format of the log is based on
[Keep a Changelog][keepchangelog].

Releases are based on [Semantic Versioning][semver], and use the format
of `MAJOR.MINOR.PATCH`. In a nutshell, the version will be incremented
based on the following:

- `MAJOR`: Incompatible or major changes.
- `MINOR`: Backwards-compatible new features and enhancements.
- `PATCH`: Backwards-compatible bugfixes and package updates.

## Contributing

This is an active open-source project. We are always open to people who want to
use the code or contribute to it.

We've set up a separate document for our
[contribution guidelines](.github/CONTRIBUTING.md).

Thank you for being involved! :heart_eyes:

## Setting up development environment

This Python project is fully managed using the [uv][uv] dependency manager.

You need at least:

- [uv][uv-install]

To install all packages, including all development requirements:

```bash
uv sync --dev
```

As this repository uses the [pre-commit][pre-commit] framework, all changes
are linted and tested with each commit. You can run all checks and tests
manually, using the following commands:

In the project venv

```bash
pre-commit run -a
```

or with

```bash
uv run pre-commit run -a
```

To run just the Python tests:

```bash
uv run pytest
```

## Authors & contributors

The content is by [Robert Resch][edenhaus].

For a full list of all authors and contributors,
check [the contributor's page][contributors].

[go2rtc]: https://github.com/AlexxIT/go2rtc/
[contributors]: https://github.com/home-assistant-libs/python-go2rtc-client/graphs/contributors
[edenhaus]: https://github.com/edenhaus
[keepchangelog]: http://keepachangelog.com/en/1.0.0/
[uv]: https://docs.astral.sh/uv/
[uv-install]: https://docs.astral.sh/uv/getting-started/installation/
[pre-commit]: https://pre-commit.com/
[releases]: https://github.com/home-assistant-libs/python-go2rtc-client/releases
[semver]: http://semver.org/spec/v2.0.0.html
