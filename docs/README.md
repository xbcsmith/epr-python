# EPR Python

## Overview

EPR Python is an async python client for the Event Provenance Registry server. The client uses `httpx` for HTTP requests and requires Python 3.8+ with async/await support.

**Note:** All client operations are async and must be used with `await`. The client should be used as an async context manager to ensure proper resource cleanup.

## Model Example

A model example using the models in the `epr` package.

```python
from epr.models import EventReceiver

event_receiver_foo = EventReceiver()
event_receiver_foo.name = "foo-receiver"
event_receiver_foo.type = "dev.events.foo"
event_receiver_foo.version = "1.0.0"
event_receiver_foo.description = "The Event Receiver for the Foo of Brixton"
event_receiver_foo.schema = "{}"

print(f"Name: {event_receiver_foo.name}")
print(f"Type: {event_receiver_foo.type}")
print(f"Fingerprint: {event_receiver_foo.compute_fingerprint()}")
```

A model example a dictionary and the models in the `epr` package.

```python
from epr.models import EventReceiver

erf = dict(
    name="foo-receiver-2",
    type="dev.events.foo",
    version="1.0.0",
    description="The Event Receiver for the Foo of Brixton",
    schema="{}",
)

erf_obj = EventReceiver(**erf)

print(f"Name: {erf_obj.name}")
print(f"Type: {erf_obj.type}")
print(f"Fingerprint: {erf_obj.compute_fingerprint()}")
```

## Client Create Example

An async Client create example using the models in the `epr` package.

```python
import asyncio
import time

from epr.client import Client
from epr.models import Event, EventReceiver, EventReceiverGroup

async def main():
    url = "http://localhost:8042"
    headers = {}
    
    async with Client(url, headers=headers) as client:

        # Create an event receiver

        event_receiver_foo = EventReceiver()
        event_receiver_foo.name = "foo-receiver-2"
        event_receiver_foo.type = "dev.events.foo"
        event_receiver_foo.version = "1.0.0"
        event_receiver_foo.description = "The Event Receiver for the Foo of Brixton"
        event_receiver_foo.schema = "{}"

        event_receiver_foo_res = await client.create_event_receiver(params=event_receiver_foo)
        event_receiver_foo_id = event_receiver_foo_res["data"]["create_event_receiver"]


        event_receiver_bar = EventReceiver()
        event_receiver_bar.name = "bar-receiver-1"
        event_receiver_bar.type = "dev.events.bar"
        event_receiver_bar.version = "1.0.0"
        event_receiver_bar.description = "The Event Receiver for the Bar of Brixton"
        event_receiver_bar.schema = "{}"

        event_receiver_bar_res = await client.create_event_receiver(params=event_receiver_bar)
        event_receiver_bar_id = event_receiver_bar_res["data"]["create_event_receiver"]

        # Create an event receiver group

        event_receiver_group_foo = EventReceiverGroup()
        event_receiver_group_foo.name = "foo-bar-receiver-group-1"
        event_receiver_group_foo.type = "dev.events.foo.bar.complete"
        event_receiver_group_foo.version = "1.0.0"
        event_receiver_group_foo.description = "The Event Receiver Group for the Foo and Bar of Brixton"
        event_receiver_group_foo.event_receiver_ids = [event_receiver_foo_id, event_receiver_bar_id]
        event_receiver_group_foo.enabled = True

        event_receiver_group_foo_res = await client.create_event_receiver_group(params=event_receiver_group_foo)
        event_receiver_group_foo_id = event_receiver_group_foo_res["data"]["create_event_receiver_group"]

        # Create an event

        event_foo = Event()
        event_foo.name = "foo"
        event_foo.version = "1.0.0"
        event_foo.release = str(time.time())
        event_foo.platform_id = "x86_64-gnu-linux-9"
        event_foo.package = "rpm"
        event_foo.description = "The Foo of Brixton"
        event_foo.payload = '{"name": "foo"}'
        event_foo.success = True
        event_foo.event_receiver_id = event_receiver_foo_id

        event_foo_res = await client.create_event(params=event_foo)
        event_foo_id = event_foo_res["data"]["create_event"]

        event_bar = Event()
        event_bar.name = "bar"
        event_bar.version = "1.0.0"
        event_bar.release = str(time.time())
        event_bar.platform_id = "x86_64-gnu-linux-9"
        event_bar.package = "rpm"
        event_bar.description = "The Bar of Brixton"
        event_bar.payload = '{"name": "bar"}'
        event_bar.success = True
        event_bar.event_receiver_id = event_receiver_bar_id

        event_bar_res = await client.create_event(params=event_bar)
        event_bar_id = event_bar_res["data"]["create_event"]

        results = {
            "events": [event_foo_id, event_bar_id],
            "event_receivers": [event_receiver_foo_id, event_receiver_bar_id],
            "event_receiver_groups": [event_receiver_group_foo_id],
        }

        print(f"{results}")
        return results

# Run the async function
if __name__ == "__main__":
    asyncio.run(main())
```

### TL;DR Async Client Example

Create an event receiver and event receiver group. Then send events.

```python
import asyncio
import time
from epr.client import Client
from epr.models import Event, EventReceiver, EventReceiverGroup

async def main():
    url = "http://localhost:8042"
    headers = {}
    
    async with Client(url, headers=headers) as client:

        erf = dict(
            name="foo-receiver-3",
            type="dev.events.foo",
            version="1.0.0",
            description="The Event Receiver for the Foo of Brixton",
            schema="{}",
        )

        erf_res = await client.create_event_receiver(params=erf)
        erf_id = erf_res["data"]["create_event_receiver"]


        erb = dict(
            name="bar-receiver-4",
            type="dev.events.bar",
            version="1.0.0",
            description="The Event Receiver for the Bar of Brixton",
            schema="{}",
        )

        erb_res = await client.create_event_receiver(params=erb)
        erb_id = erb_res["data"]["create_event_receiver"]

        erg = dict(
            name="foo-bar-receiver-group-2",
            type="dev.events.foo.bar.complete",
            version="1.0.0",
            description="The Event Receiver Group for the Foo and Bar of Brixton",
            enabled=True,
            event_receiver_ids=[erf_id, erb_id],
        )

        erg_res = await client.create_event_receiver_group(params=erg)
        erg_id = erg_res["data"]["create_event_receiver_group"]

        ef = dict(
            name="foo",
            version="1.0.0",
            release=str(time.time()),
            platform_id="x86_64-gnu-linux-9",
            package="rpm",
            description="The Foo of Brixton",
            payload="{}",
            success=True,
            event_receiver_id=erf_id,
        )

        ef_res = await client.create_event(params=ef)
        ef_id = ef_res["data"]["create_event"]

        eb = dict(
            name="bar",
            version="1.0.0",
            release=str(time.time()),
            platform_id="x86_64-gnu-linux-9",
            package="rpm",
            description="The Bar of Brixton",
            payload="{}",
            success=True,
            event_receiver_id=erb_id,
        )

        eb_res = await client.create_event(params=eb)
        eb_id = eb_res["data"]["create_event"]

        results = {"events": [ef_id, eb_id], "event_receivers": [erf_id, erb_id], "event_receiver_groups": [erg_id]}

        print(f"{results}")
        return results

# Run the async function
if __name__ == "__main__":
    asyncio.run(main())
```

## Client Search Example

First we will search for events we created above. Here we will search by name,
version, and release. We will use the release values from the Events we created
above. We will also set the fields we want to return.

```python
import asyncio
from epr.client import Client
from epr.models import Event, EventReceiver, EventReceiverGroup

async def search_example():
    url = "http://localhost:8042"
    headers = {}
    
    async with Client(url, headers=headers) as client:

        e_fields = [
            "id",
            "name",
            "version",
            "release",
            "platform_id",
            "package",
            "description",
            "success",
            "event_receiver_id",
        ]

        efs = Event()
        efs.name = "foo"
        efs.version = "1.0.0"
        efs.release = "1234567890"  # Use your actual release value

        event_results = await client.search_events(params=efs.as_dict_query(), fields=e_fields)
        print(f"{event_results}")

        ebs = Event()
        ebs.name = "bar"
        ebs.version = "1.0.0"
        ebs.release = "1234567891"  # Use your actual release value

        event_results = await client.search_events(params=ebs.as_dict_query(), fields=e_fields)
        print(f"{event_results}")

# Run the async function
if __name__ == "__main__":
    asyncio.run(search_example())
```

We will now search for event receivers using the name, version, and type.

```python
import asyncio
from epr.client import Client
from epr.models import EventReceiver

async def search_event_receivers():
    url = "http://localhost:8042"
    headers = {}
    
    async with Client(url, headers=headers) as client:
        er_fields = ["id", "name", "type", "version", "description", "schema", "fingerprint", "created_at"]

        erfs = EventReceiver()
        erfs.name = "foo-receiver-3"
        erfs.version = "1.0.0"
        erfs.type = "dev.events.foo"

        event_receiver_results = await client.search_event_receivers(params=erfs.as_dict_query(), fields=er_fields)
        print(f"{event_receiver_results}")

        erbs = EventReceiver()
        erbs.name = "bar-receiver-4"
        erbs.version = "1.0.0"
        erbs.type = "dev.events.bar"

        event_receiver_results = await client.search_event_receivers(params=erbs.as_dict_query(), fields=er_fields)
        print(f"{event_receiver_results}")

# Run the async function
if __name__ == "__main__":
    asyncio.run(search_event_receivers())
```

Last we will search for event receiver groups using the name, version, and type.

```python
import asyncio
from epr.client import Client
from epr.models import EventReceiverGroup

async def search_event_receiver_groups():
    url = "http://localhost:8042"
    headers = {}
    
    async with Client(url, headers=headers) as client:
        erg_fields = ["id", "name", "type", "version", "description", "enabled", "created_at", "event_receiver_ids"]
        ergs = EventReceiverGroup()
        ergs.name = "foo-bar-receiver-group-2"
        ergs.version = "1.0.0"
        ergs.type = "dev.events.foo.bar.complete"

        event_receiver_group_results = await client.search_event_receiver_groups(params=ergs.as_dict_query(), fields=erg_fields)
        print(f"{event_receiver_group_results}")

# Run the async function
if __name__ == "__main__":
    asyncio.run(search_event_receiver_groups())
```

## Using with Model Context Protocol (MCP) Servers

The async client is designed to work seamlessly with MCP servers. Here's an example of how to use it in an MCP server context:

```python
import asyncio
from epr.client import Client
from epr.models import Event

class EPRMCPServer:
    def __init__(self, epr_url: str):
        self.epr_url = epr_url
        
    async def create_event_handler(self, event_data: dict) -> dict:
        """MCP tool handler for creating events"""
        async with Client(self.epr_url) as client:
            event = Event(**event_data)
            result = await client.create_event(params=event)
            return result
            
    async def search_events_handler(self, search_params: dict, fields: list = None) -> dict:
        """MCP tool handler for searching events"""
        async with Client(self.epr_url) as client:
            result = await client.search_events(params=search_params, fields=fields)
            return result
```

The async context manager ensures that HTTP connections are properly managed and closed, which is essential for long-running MCP servers.

