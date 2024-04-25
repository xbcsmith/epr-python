# epr-python

## Overview

EPR Python is a python client for the Event Provenance Registry server.

## Development

```bash
python3 -m venv ~/.virtualenvs/epr-python
source ~/.virtualenvs/epr-python/bin/activate

git clone git@github.com:xbcsmith/epr-python.git
cd epr-python

pip install -e .
```

### Development dependencies

```bash
pip install -e .[lint,test,build]
```

## Makefile

```text
install         Installs epr into a virtualenv called epr-python
megalint        Run megalinter
tests           Run tests
release         Run tox
wheel           Create an sdist bdist_wheel
clean           Cleanup everything
```

## Usage

```text
usage: eprcli <command> [<args>]

            eprcli commands are:
                create      create Events, Event Receivers, and Event Receiver Groups
                search      search Events, Event Receivers, and Event Receiver Groups
```

### Create

```text
usage: eprcli [-h] [--token EPR_API_TOKEN] [--url EPR_URL] [--jsonpath JSONPATH_EXPR] [--dry-run] [--debug] {event,event-receiver,event-receiver-group} ...

create Events, Event Receivers, and Event Receiver Groups

positional arguments:
  {event,event-receiver,event-receiver-group}
                        Sub-commands for create
    event               Event related options
    event-receiver      Event Receiver related options
    event-receiver-group
                        Event Receiver Group related options

options:
  -h, --help            show this help message and exit
  --token EPR_API_TOKEN
                        EPR Access Token
  --url EPR_URL         EPR Server URL
  --jsonpath JSONPATH_EXPR
                        Apply jsonpath to the results
  --dry-run             Do not do anything
  --debug               Turn debug on
```

### Search

```text
usage: eprcli [-h] [--token EPR_API_TOKEN] [--url EPR_URL] [--jsonpath JSONPATH_EXPR] [--dry-run] [--debug] {event,event-receiver,event-receiver-group} ...

search Events, Event Receivers, and Event Receiver Groups

positional arguments:
  {event,event-receiver,event-receiver-group}
                        Sub-commands for create
    event               Event related options
    event-receiver      Event Receiver related options
    event-receiver-group
                        Event Receiver Group related options

options:
  -h, --help            show this help message and exit
  --token EPR_API_TOKEN
                        EPR Access Token
  --url EPR_URL         EPR Server URL
  --jsonpath JSONPATH_EXPR
                        Apply jsonpath to the results
  --dry-run             Do not do anything
  --debug               Turn debug on
```

## CLI Examples

Create an event receiver using the provided parameters:

```bash
eprcli create event-receiver --name foo-python-cli --version 1.0.0 --type dev.foo.python.cli --description "foo python cli event receiver" --schema "{}"
```

Search for an event receiver using the provided parameters:

```bash
eprcli search event-receiver --id 01HW3SZ8N3MXA9EWZZY4HSVVNK
```

Create an event using the provided parameters:

```bash
eprcli create event --name foo --version 1.0.1 --release 2023.11.16 --description "The Foo of Brixton" --payload '{"name": "foo"}' --success true --event-receiver-id 01HW3SZ8N3MXA9EWZZY4HSVVNK
```

Search for an event using the provided parameters:

```bash
eprcli search event --id 01HQK4MD17NXY7XAQ4B7V32DRS
```

```bash
eprcli search event --name foo --version 1.0.1 --release 2023.11.16
```

### Client Examples

[Client Examples](./docs/README.md)
