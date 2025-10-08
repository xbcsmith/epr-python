# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2024 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from epr import create, search
from epr.config import Config
from epr.models import Event, EventReceiver, EventReceiverGroup
from tests import base


class AsyncSearchCreateTestCase(base.BaseTestCase):
    """Test cases for the async search and create functions."""

    def setUp(self):
        super().setUp()
        self.test_url = "http://test-server:8042"

        # Create test config
        self.config = Config(url=self.test_url, token="test-token")

        # Create test data
        self.test_event = Event(
            name="test-event",
            version="1.0.0",
            release="stable",
            platform_id="linux-x64",
            package="test-package",
            description="Test event",
        )

        self.test_receiver = EventReceiver(
            name="test-receiver",
            type="webhook",
            version="1.0.0",
            description="Test receiver",
            schema={"type": "object"},
        )

        self.test_group = EventReceiverGroup(
            name="test-group",
            type="group",
            version="1.0.0",
            description="Test group",
            event_receiver_ids=["receiver-1", "receiver-2"],
            enabled=True,
        )

    @patch("epr.search.Client")
    async def test_search_function(self, mock_client_class):
        """Test the async search function."""
        # Setup mock client and responses
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Mock search responses
        mock_client.search_events.return_value = {"data": {"events": [{"id": "event-1", "name": "test-event"}]}}
        mock_client.search_event_receivers.return_value = {
            "data": {"event_receivers": [{"id": "receiver-1", "name": "test-receiver"}]}
        }
        mock_client.search_event_receiver_groups.return_value = {
            "data": {"event_receiver_groups": [{"id": "group-1", "name": "test-group"}]}
        }

        # Add test data to config
        self.config.events = [self.test_event]
        self.config.event_receivers = [self.test_receiver]
        self.config.event_receiver_groups = [self.test_group]

        # Run search function
        result = await search.search(self.config)

        # Verify results
        self.assertIn("events", result)
        self.assertIn("event_receivers", result)
        self.assertIn("event_receiver_groups", result)

        # Verify client was used correctly
        mock_client.search_events.assert_called_once()
        mock_client.search_event_receivers.assert_called_once()
        mock_client.search_event_receiver_groups.assert_called_once()

        # Verify client context manager was used
        mock_client_class.return_value.__aenter__.assert_called_once()
        mock_client_class.return_value.__aexit__.assert_called_once()

    @patch("epr.create.Client")
    async def test_create_function(self, mock_client_class):
        """Test the async create function."""
        # Setup mock client and responses
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Mock create responses
        mock_client.create_event.return_value = {"data": {"create_event": "new-event-id"}}
        mock_client.create_event_receiver.return_value = {"data": {"create_event_receiver": "new-receiver-id"}}
        mock_client.create_event_receiver_group.return_value = {"data": {"create_event_receiver_group": "new-group-id"}}

        # Add test data to config
        self.config.events = [self.test_event]
        self.config.event_receivers = [self.test_receiver]
        self.config.event_receiver_groups = [self.test_group]

        # Run create function
        result = await create.create(self.config)

        # Verify results
        self.assertIn("events", result)
        self.assertIn("event_receivers", result)
        self.assertIn("event_receiver_groups", result)

        self.assertEqual(result["events"], ["new-event-id"])
        self.assertEqual(result["event_receivers"], ["new-receiver-id"])
        self.assertEqual(result["event_receiver_groups"], ["new-group-id"])

        # Verify client methods were called
        mock_client.create_event.assert_called_once()
        mock_client.create_event_receiver.assert_called_once()
        mock_client.create_event_receiver_group.assert_called_once()

    @patch("epr.search.Client")
    async def test_search_with_custom_fields(self, mock_client_class):
        """Test search function with custom field specifications."""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_client.search_events.return_value = {"data": {"events": [{"id": "event-1"}]}}

        # Set custom fields in config
        self.config.events = [self.test_event]
        self.config.event_fields = ["id", "name", "custom_field"]

        await search.search(self.config)

        # Verify custom fields were passed
        call_args = mock_client.search_events.call_args
        self.assertIn("fields", call_args.kwargs)
        self.assertEqual(call_args.kwargs["fields"], ["id", "name", "custom_field"])

    @patch("epr.search.Client")
    async def test_search_empty_config(self, mock_client_class):
        """Test search function with empty config."""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Empty config - no events, receivers, or groups
        empty_config = Config(url=self.test_url, token="test-token")

        result = await search.search(empty_config)

        # Should return empty results
        self.assertEqual(result["events"], [])
        self.assertEqual(result["event_receivers"], [])
        self.assertEqual(result["event_receiver_groups"], [])

        # Client methods should not be called
        mock_client.search_events.assert_not_called()
        mock_client.search_event_receivers.assert_not_called()
        mock_client.search_event_receiver_groups.assert_not_called()

    @patch("epr.create.Client")
    async def test_create_empty_config(self, mock_client_class):
        """Test create function with empty config."""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Empty config
        empty_config = Config(url=self.test_url, token="test-token")

        result = await create.create(empty_config)

        # Should return empty results
        self.assertEqual(result["events"], [])
        self.assertEqual(result["event_receivers"], [])
        self.assertEqual(result["event_receiver_groups"], [])

        # Client methods should not be called
        mock_client.create_event.assert_not_called()
        mock_client.create_event_receiver.assert_not_called()
        mock_client.create_event_receiver_group.assert_not_called()

    @patch("epr.search.Client")
    async def test_search_error_handling(self, mock_client_class):
        """Test error handling in search function."""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Setup client to raise an exception
        mock_client.search_events.side_effect = Exception("Network error")

        self.config.events = [self.test_event]

        # The search function should propagate the exception
        with self.assertRaises(Exception) as context:
            await search.search(self.config)

        self.assertIn("Network error", str(context.exception))

    @patch("epr.create.Client")
    async def test_create_error_handling(self, mock_client_class):
        """Test error handling in create function."""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Setup client to raise an exception
        mock_client.create_event.side_effect = Exception("Server error")

        self.config.events = [self.test_event]

        # The create function should propagate the exception
        with self.assertRaises(Exception) as context:
            await create.create(self.config)

        self.assertIn("Server error", str(context.exception))

    @patch("epr.create.Client")
    async def test_multiple_items_handling(self, mock_client_class):
        """Test handling of multiple items in config."""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Setup responses for multiple items
        mock_client.create_event.side_effect = [
            {"data": {"create_event": "event-id-1"}},
            {"data": {"create_event": "event-id-2"}},
        ]

        # Add multiple events to config
        event2 = Event(name="event-2", version="2.0.0")
        self.config.events = [self.test_event, event2]

        result = await create.create(self.config)

        # Should have created both events
        self.assertEqual(len(result["events"]), 2)
        self.assertEqual(result["events"], ["event-id-1", "event-id-2"])

        # Client method should be called twice
        self.assertEqual(mock_client.create_event.call_count, 2)

    def test_data_serialization(self):
        """Test that model data is properly serialized for API calls."""
        # Test as_dict method
        event_dict = self.test_event.as_dict()
        self.assertIsInstance(event_dict, dict)
        self.assertEqual(event_dict["name"], "test-event")
        self.assertEqual(event_dict["version"], "1.0.0")

        # Test as_dict_query method (filters out empty values)
        event_query = self.test_event.as_dict_query()
        self.assertIsInstance(event_query, dict)
        # Should only include non-empty values
        self.assertNotIn("id", event_query)  # id is empty by default
        self.assertIn("name", event_query)


# Run async tests using asyncio
def run_async_test(coro):
    """Helper to run async test methods."""

    def wrapper(self):
        return asyncio.run(coro(self))

    return wrapper


# Apply the async wrapper to all async test methods
for attr_name in dir(AsyncSearchCreateTestCase):
    attr = getattr(AsyncSearchCreateTestCase, attr_name)
    if callable(attr) and asyncio.iscoroutinefunction(attr) and attr_name.startswith("test_"):
        setattr(AsyncSearchCreateTestCase, attr_name, run_async_test(attr))


if __name__ == "__main__":
    unittest.main()
