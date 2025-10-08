#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2024 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""
Example demonstrating how to use the async EPR client.
This is especially useful for MCP servers and other async contexts.
"""

import asyncio
import json
from typing import Optional

from epr.client import Client


async def search_events_example():
    """Example of searching for events using the async client."""

    # Use the async context manager - this ensures proper cleanup
    async with Client("http://localhost:8042") as client:
        # Search for events with specific parameters
        search_params = {"name": "test-event", "version": "1.0.0"}

        # Specify which fields to return
        fields = ["id", "name", "version", "release", "description", "success"]

        try:
            result = await client.search_events(params=search_params, fields=fields)
            print("Search Results:")
            print(json.dumps(result, indent=2))
            return result

        except Exception as e:
            print(f"Error searching for events: {e}")
            return None


async def create_event_example():
    """Example of creating an event using the async client."""

    async with Client("http://localhost:8042") as client:
        # Event data to create
        event_data = {
            "name": "example-event",
            "version": "1.0.1",
            "release": "stable",
            "platform_id": "linux-x64",
            "package": "my-package",
            "description": "An example event created via async client",
            "payload": {"key": "value", "number": 42},
            "success": True,
        }

        try:
            result = await client.create_event(params=event_data)
            print("Create Result:")
            print(json.dumps(result, indent=2))
            return result

        except Exception as e:
            print(f"Error creating event: {e}")
            return None


async def batch_operations_example():
    """Example of performing multiple operations efficiently."""

    async with Client("http://localhost:8042") as client:
        # Perform multiple operations concurrently
        search_task = client.search_events(fields=["id", "name", "version"])

        receiver_search_task = client.search_event_receivers(fields=["id", "name", "type", "version"])

        group_search_task = client.search_event_receiver_groups(fields=["id", "name", "type", "enabled"])

        try:
            # Wait for all operations to complete
            search_result, receiver_result, group_result = await asyncio.gather(
                search_task, receiver_search_task, group_search_task, return_exceptions=True
            )

            results = {
                "events": search_result,
                "event_receivers": receiver_result,
                "event_receiver_groups": group_result,
            }

            print("Batch Results:")
            print(json.dumps(results, indent=2))
            return results

        except Exception as e:
            print(f"Error in batch operations: {e}")
            return None


class EPRAsyncService:
    """
    Example service class showing how to use the async client in a class.
    This pattern is useful for MCP servers and other service applications.
    """

    def __init__(self, url: str = "http://localhost:8042", headers: Optional[dict] = None):
        self.url = url
        self.headers = headers or {}
        self._client: Optional[Client] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self._client = Client(self.url, headers=self.headers)
        await self._client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.__aexit__(exc_type, exc_val, exc_tb)

    async def get_event_by_name(self, name: str):
        """Get an event by name."""
        if not self._client:
            raise RuntimeError("Service not initialized. Use 'async with EPRAsyncService()' context manager.")

        search_params = {"name": name}
        fields = ["id", "name", "version", "release", "description", "success"]

        result = await self._client.search_events(params=search_params, fields=fields)
        events = result.get("data", {}).get("events", [])
        return events[0] if events else None

    async def create_event(self, event_data: dict):
        """Create a new event."""
        if not self._client:
            raise RuntimeError("Service not initialized. Use 'async with EPRAsyncService()' context manager.")

        return await self._client.create_event(params=event_data)

    async def health_check(self):
        """Simple health check by attempting to search for events."""
        if not self._client:
            raise RuntimeError("Service not initialized. Use 'async with EPRAsyncService()' context manager.")

        try:
            await self._client.search_events(fields=["id"])
            return {"status": "healthy", "service": "epr"}
        except Exception as e:
            return {"status": "unhealthy", "service": "epr", "error": str(e)}


async def service_example():
    """Example using the service class."""

    async with EPRAsyncService() as service:
        # Health check
        health = await service.health_check()
        print("Health Check:")
        print(json.dumps(health, indent=2))

        # Get event by name
        event = await service.get_event_by_name("test-event")
        if event:
            print("Found Event:")
            print(json.dumps(event, indent=2))
        else:
            print("Event not found")


async def main():
    """Main example function."""
    print("EPR Async Client Examples")
    print("=" * 50)

    # Note: These examples assume an EPR server is running at localhost:8042
    # In a real scenario, you would handle connection errors appropriately

    print("\n1. Search Events Example:")
    await search_events_example()

    print("\n2. Create Event Example:")
    await create_event_example()

    print("\n3. Batch Operations Example:")
    await batch_operations_example()

    print("\n4. Service Class Example:")
    await service_example()


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())
