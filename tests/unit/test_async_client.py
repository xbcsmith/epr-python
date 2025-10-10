# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2024 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

import asyncio
import unittest
from unittest.mock import MagicMock, patch

import httpx

from epr.client import Client
from epr.models import GraphQLQuery
from tests import base


class AsyncClientTestCase(base.BaseTestCase):
    """Test cases for the async Client class."""

    def setUp(self):
        super().setUp()
        self.test_url = "http://test-server:8042"
        self.test_headers = {"Authorization": "Bearer test-token"}

    def test_client_initialization(self):
        """Test client initialization with various parameters."""
        # Test default initialization
        client = Client(None)
        self.assertEqual(client.url, "http://localhost:8042")
        self.assertEqual(client.target, "http://localhost:8042/api/v1/graphql/query")
        self.assertEqual(client.headers["Content-Type"], "application/json")

        # Test with custom URL and headers
        client = Client(self.test_url, headers=self.test_headers)
        self.assertEqual(client.url, self.test_url)
        self.assertEqual(client.target, f"{self.test_url}/api/v1/graphql/query")
        self.assertIn("Authorization", client.headers)
        self.assertEqual(client.headers["Authorization"], "Bearer test-token")

    def test_graphql_search_query_generation(self):
        """Test GraphQL search query generation."""
        client = Client(self.test_url)

        # Test basic search query
        query = client._new_graphql_search_query("events", {"name": "test"}, ["id", "name"])
        self.assertIsInstance(query, GraphQLQuery)
        self.assertIn("query", query.query)
        self.assertIn("FindEventInput!", query.query)
        self.assertIn("events", query.query)
        self.assertEqual(query.variables["obj"]["name"], "test")

        # Test with no parameters
        query = client._new_graphql_search_query("events", None, ["id"])
        self.assertEqual(query.variables["obj"], None)

        # Test with no fields (should default to "id")
        query = client._new_graphql_search_query("events", {"name": "test"}, None)
        self.assertIn("id", query.query)

    def test_graphql_mutation_query_generation(self):
        """Test GraphQL mutation query generation."""
        client = Client(self.test_url)

        # Test mutation query
        params = {"name": "test-event", "version": "1.0.0"}
        query = client._new_graphql_mutation_query("create_event", params)

        self.assertIsInstance(query, GraphQLQuery)
        self.assertIn("mutation", query.query)
        self.assertIn("CreateEventInput!", query.query)
        self.assertIn("create_event", query.query)
        self.assertEqual(query.variables["obj"], params)

    async def test_async_context_manager(self):
        """Test async context manager functionality."""
        client = Client(self.test_url)

        # Test that client starts with no HTTP client
        self.assertIsNone(client._client)

        async with client as c:
            # Should be the same client instance
            self.assertIs(c, client)
            # Should have an HTTP client now
            self.assertIsNotNone(client._client)
            self.assertIsInstance(client._client, httpx.AsyncClient)

        # Client should be closed after context exit
        self.assertIsNone(client._client)

    async def test_manual_client_management(self):
        """Test manual client lifecycle management."""
        client = Client(self.test_url)

        # Manually enter
        result = await client.__aenter__()
        self.assertIs(result, client)
        self.assertIsNotNone(client._client)

        # Manually exit
        await client.__aexit__(None, None, None)
        self.assertIsNone(client._client)

    @patch("httpx.AsyncClient.post")
    async def test_post_method(self, mock_post):
        """Test the async _post method."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"test": "result"}}
        mock_post.return_value = mock_response

        async with Client(self.test_url) as client:
            data = {"query": "test query", "variables": {}}
            response = await client._post(client.target, data)

            # Verify the response
            self.assertEqual(response, mock_response)

            # Verify the post was called correctly
            mock_post.assert_called_once()
            call_args = mock_post.call_args

            # Check URL
            self.assertEqual(call_args[1]["url"] if "url" in call_args[1] else call_args[0][0], client.target)

            # Check headers
            self.assertEqual(call_args[1]["headers"], client.headers)

            # Check that response.raise_for_status was called
            mock_response.raise_for_status.assert_called_once()

    @patch("httpx.AsyncClient.post")
    async def test_query_method(self, mock_post):
        """Test the async _query method."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"events": [{"id": "test-id"}]}}
        mock_post.return_value = mock_response

        async with Client(self.test_url) as client:
            query = GraphQLQuery(query="query test { events { id } }", variables={"obj": {"name": "test"}})

            result = await client._query(query)

            # Should return the JSON response
            self.assertEqual(result, {"data": {"events": [{"id": "test-id"}]}})

            # Verify the underlying post call
            mock_post.assert_called_once()

    @patch("httpx.AsyncClient.post")
    async def test_search_events(self, mock_post):
        """Test async search_events method."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {"events": [{"id": "test-id", "name": "test-event", "version": "1.0.0"}]}
        }
        mock_post.return_value = mock_response

        async with Client(self.test_url) as client:
            result = await client.search_events(params={"name": "test-event"}, fields=["id", "name", "version"])

            self.assertEqual(result["data"]["events"][0]["name"], "test-event")
            mock_post.assert_called_once()

    @patch("httpx.AsyncClient.post")
    async def test_create_event(self, mock_post):
        """Test async create_event method."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"create_event": "new-event-id"}}
        mock_post.return_value = mock_response

        async with Client(self.test_url) as client:
            event_data = {"name": "new-event", "version": "1.0.0", "description": "Test event"}

            result = await client.create_event(params=event_data)

            self.assertEqual(result["data"]["create_event"], "new-event-id")
            mock_post.assert_called_once()

    @patch("httpx.AsyncClient.post")
    async def test_batch_operations(self, mock_post):
        """Test concurrent batch operations."""
        # Setup different responses for different calls
        responses = [MagicMock(), MagicMock(), MagicMock()]

        responses[0].json.return_value = {"data": {"events": [{"id": "event-1"}]}}
        responses[1].json.return_value = {"data": {"event_receivers": [{"id": "receiver-1"}]}}
        responses[2].json.return_value = {"data": {"event_receiver_groups": [{"id": "group-1"}]}}

        mock_post.side_effect = responses

        async with Client(self.test_url) as client:
            # Run multiple operations concurrently
            results = await asyncio.gather(
                client.search_events(fields=["id"]),
                client.search_event_receivers(fields=["id"]),
                client.search_event_receiver_groups(fields=["id"]),
            )

            # Verify all operations completed
            self.assertEqual(len(results), 3)
            self.assertEqual(results[0]["data"]["events"][0]["id"], "event-1")
            self.assertEqual(results[1]["data"]["event_receivers"][0]["id"], "receiver-1")
            self.assertEqual(results[2]["data"]["event_receiver_groups"][0]["id"], "group-1")

            # Verify all HTTP calls were made
            self.assertEqual(mock_post.call_count, 3)

    @patch("httpx.AsyncClient.post")
    async def test_http_error_handling(self, mock_post):
        """Test HTTP error handling."""
        # Setup mock to raise an HTTP error
        mock_post.side_effect = httpx.HTTPStatusError("404 Not Found", request=MagicMock(), response=MagicMock())

        async with Client(self.test_url) as client:
            with self.assertRaises(httpx.HTTPStatusError):
                await client.search_events()

    async def test_client_without_context_manager(self):
        """Test that client works without context manager by auto-creating HTTP client."""
        client = Client(self.test_url)

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"data": {"events": []}}
            mock_post.return_value = mock_response

            # This should auto-create the HTTP client
            await client.search_events()

            # Verify HTTP client was created
            self.assertIsNotNone(client._client)
            mock_post.assert_called_once()

            # Clean up
            await client.close()

    def test_sync_utility_methods(self):
        """Test synchronous utility methods that don't require async."""
        client = Client(self.test_url)

        # Test operation mapping
        self.assertIn("events", client._operation_map["search"])
        self.assertIn("create_event", client._operation_map["mutation"])

        # Test that all expected operations are mapped
        expected_search_ops = ["events", "event_receivers", "event_receiver_groups"]
        expected_mutation_ops = ["create_event", "create_event_receiver", "create_event_receiver_group"]

        for op in expected_search_ops:
            self.assertIn(op, client._operation_map["search"])

        for op in expected_mutation_ops:
            self.assertIn(op, client._operation_map["mutation"])


# Run async tests using asyncio
def run_async_test(coro):
    """Helper to run async test methods."""

    def wrapper(self):
        return asyncio.run(coro(self))

    return wrapper


# Apply the async wrapper to all async test methods
for attr_name in dir(AsyncClientTestCase):
    attr = getattr(AsyncClientTestCase, attr_name)
    if callable(attr) and asyncio.iscoroutinefunction(attr) and attr_name.startswith("test_"):
        setattr(AsyncClientTestCase, attr_name, run_async_test(attr))


if __name__ == "__main__":
    unittest.main()
