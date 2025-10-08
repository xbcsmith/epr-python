# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2024 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

import unittest

from epr.models import Event, EventReceiver, EventReceiverGroup, GraphQLQuery
from tests import base


class ModelsTestCase(base.BaseTestCase):
    """Test cases for updated model classes."""

    def setUp(self):
        super().setUp()

    def test_graphql_query_model(self):
        """Test the updated GraphQLQuery model with dict variables."""
        # Test basic creation
        query = GraphQLQuery(query="query test { events { id } }", variables={"name": "test", "version": "1.0"})

        self.assertEqual(query.query, "query test { events { id } }")
        self.assertIsInstance(query.variables, dict)
        self.assertEqual(query.variables["name"], "test")
        self.assertEqual(query.variables["version"], "1.0")

    def test_graphql_query_as_dict(self):
        """Test GraphQLQuery as_dict method works correctly."""
        query = GraphQLQuery(
            query="query test { events { id } }", variables={"name": "test", "nested": {"key": "value"}}
        )

        query_dict = query.as_dict()

        self.assertIsInstance(query_dict, dict)
        self.assertIn("query", query_dict)
        self.assertIn("variables", query_dict)
        self.assertEqual(query_dict["query"], "query test { events { id } }")
        self.assertEqual(query_dict["variables"]["name"], "test")
        self.assertEqual(query_dict["variables"]["nested"]["key"], "value")

    def test_graphql_query_default_variables(self):
        """Test GraphQLQuery with default empty variables."""
        query = GraphQLQuery(query="query test { events { id } }")

        self.assertEqual(query.query, "query test { events { id } }")
        self.assertIsInstance(query.variables, dict)
        self.assertEqual(len(query.variables), 0)

    def test_event_model_unchanged(self):
        """Test that Event model still works as expected."""
        event = Event(name="test-event", version="1.0.0", description="Test event")

        self.assertEqual(event.name, "test-event")
        self.assertEqual(event.version, "1.0.0")
        self.assertEqual(event.description, "Test event")

        # Test as_dict
        event_dict = event.as_dict()
        self.assertIn("name", event_dict)
        self.assertEqual(event_dict["name"], "test-event")

        # Test as_dict_query (filters empty values)
        event_query = event.as_dict_query()
        self.assertIn("name", event_query)
        self.assertNotIn("id", event_query)  # Should be filtered out if empty

    def test_event_receiver_model_unchanged(self):
        """Test that EventReceiver model still works as expected."""
        receiver = EventReceiver(name="test-receiver", type="webhook", version="1.0.0", description="Test receiver")

        self.assertEqual(receiver.name, "test-receiver")
        self.assertEqual(receiver.type, "webhook")

        # Test serialization
        receiver_dict = receiver.as_dict()
        self.assertIn("name", receiver_dict)
        self.assertIn("type", receiver_dict)

    def test_event_receiver_group_model_unchanged(self):
        """Test that EventReceiverGroup model still works as expected."""
        group = EventReceiverGroup(
            name="test-group",
            type="group",
            version="1.0.0",
            event_receiver_ids=["receiver-1", "receiver-2"],
            enabled=True,
        )

        self.assertEqual(group.name, "test-group")
        self.assertEqual(group.enabled, True)
        self.assertEqual(len(group.event_receiver_ids), 2)

        # Test serialization
        group_dict = group.as_dict()
        self.assertIn("name", group_dict)
        self.assertIn("enabled", group_dict)
        self.assertIn("event_receiver_ids", group_dict)

    def test_model_inheritance(self):
        """Test that all models properly inherit from Model base class."""
        event = Event()
        receiver = EventReceiver()
        group = EventReceiverGroup()
        query = GraphQLQuery(query="test")

        # All should have as_dict method
        self.assertTrue(hasattr(event, "as_dict"))
        self.assertTrue(hasattr(receiver, "as_dict"))
        self.assertTrue(hasattr(group, "as_dict"))
        self.assertTrue(hasattr(query, "as_dict"))

        # All should have as_dict_query method
        self.assertTrue(hasattr(event, "as_dict_query"))
        self.assertTrue(hasattr(receiver, "as_dict_query"))
        self.assertTrue(hasattr(group, "as_dict_query"))
        self.assertTrue(hasattr(query, "as_dict_query"))

    def test_complex_variables_serialization(self):
        """Test that complex variables in GraphQLQuery serialize correctly."""
        complex_vars = {
            "string": "test",
            "number": 42,
            "boolean": True,
            "list": ["a", "b", "c"],
            "nested_dict": {"inner": "value", "inner_list": [1, 2, 3]},
            "null_value": None,
        }

        query = GraphQLQuery(
            query="mutation complex($input: ComplexInput!) { create(input: $input) }", variables=complex_vars
        )

        # Test that all variable types are preserved
        self.assertEqual(query.variables["string"], "test")
        self.assertEqual(query.variables["number"], 42)
        self.assertEqual(query.variables["boolean"], True)
        self.assertEqual(query.variables["list"], ["a", "b", "c"])
        self.assertEqual(query.variables["nested_dict"]["inner"], "value")
        self.assertIsNone(query.variables["null_value"])

        # Test serialization
        query_dict = query.as_dict()
        self.assertEqual(query_dict["variables"]["nested_dict"]["inner_list"], [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
