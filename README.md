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

## Examples

```bash
eprcli create event-receiver --name foo-python-cli --version 1.0.0 --type dev.foo.python.cli --description "foo python cli event receiver" --schema "{}"
```

```bash
eprcli search event-receiver --id 01HW3SZ8N3MXA9EWZZY4HSVVNK
```

```bash
eprcli create event --name foo --version 1.0.1 --release 2023.11.16 --description "The Foo of Brixton" --payload '{"name": "foo"}' --success true --event-receiver-id 01HW3SZ8N3MXA9EWZZY4HSVVNK
```

```bash
eprcli search event --id 01HQK4MD17NXY7XAQ4B7V32DRS
```

```bash
eprcli search event --name foo --version 1.0.1 --release 2023.11.16
```
