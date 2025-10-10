# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2024 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

import sys
import unittest
from io import StringIO
from unittest.mock import AsyncMock, patch

from epr import main
from tests import base


class AsyncMainTestCase(base.BaseTestCase):
    """Test cases for main module with async functionality."""

    def setUp(self):
        super().setUp()
        # Capture stdout for testing CLI output
        self.old_stdout = sys.stdout
        self.captured_output = StringIO()
        sys.stdout = self.captured_output

        # Store original sys.argv
        self.original_argv = sys.argv

    def tearDown(self):
        super().tearDown()
        # Restore stdout
        sys.stdout = self.old_stdout
        # Restore sys.argv
        sys.argv = self.original_argv

    @patch("epr.create.create")
    def test_cli_create_calls_async_function(self, mock_create):
        """Test that CLI create command properly calls async create function."""
        # Setup mock to return a result
        mock_create.return_value = {"events": ["event-id-1"], "event_receivers": [], "event_receiver_groups": []}

        # Simulate CLI arguments for create command
        test_args = [
            "eprcli",
            "create",
            "event",
            "--name",
            "test-event",
            "--version",
            "1.0.0",
            "--release",
            "stable",
            "--platform-id",
            "linux-x64",
            "--package",
            "test-package",
            "--description",
            "Test event",
            "--success",
        ]

        with patch.object(sys, "argv", test_args):
            try:
                # This should work without raising an exception
                cmd = main.CmdLine()
                self.assertIsNotNone(cmd)
                # The create method should have been called with asyncio.run()
                mock_create.assert_called_once()
            except SystemExit:
                # CLI may exit after completion, that's expected
                pass

    @patch("epr.search.search")
    def test_cli_search_calls_async_function(self, mock_search):
        """Test that CLI search command properly calls async search function."""
        # Setup mock to return a result
        mock_search.return_value = {
            "events": [{"id": "event-1", "name": "test-event"}],
            "event_receivers": [],
            "event_receiver_groups": [],
        }

        # Simulate CLI arguments for search command
        test_args = ["eprcli", "search", "event", "--name", "test-event"]

        with patch.object(sys, "argv", test_args):
            try:
                # This should work without raising an exception
                cmd = main.CmdLine()
                self.assertIsNotNone(cmd)
                # The search method should have been called with asyncio.run()
                mock_search.assert_called_once()
            except SystemExit:
                # CLI may exit after completion, that's expected
                pass

    def test_cli_help_still_works(self):
        """Test that CLI help functionality still works after async changes."""
        test_args = ["eprcli", "--help"]

        with patch.object(sys, "argv", test_args):
            with self.assertRaises(SystemExit) as context:
                main.CmdLine()

            # Help should exit with code 0
            self.assertEqual(context.exception.code, 0)

    @patch("epr.create.create")
    def test_create_command_error_handling(self, mock_create):
        """Test error handling in create command with async function."""
        # Setup mock to raise an exception
        mock_create.side_effect = Exception("Async operation failed")

        test_args = [
            "eprcli",
            "create",
            "event",
            "--name",
            "test-event",
            "--version",
            "1.0.0",
            "--release",
            "stable",
            "--platform-id",
            "linux-x64",
            "--package",
            "test-package",
            "--description",
            "Test event",
        ]

        with patch.object(sys, "argv", test_args):
            # The exception should propagate (or be handled gracefully by CLI)
            with self.assertRaises((Exception, SystemExit)):
                main.CmdLine()

    @patch("epr.search.search")
    def test_search_command_error_handling(self, mock_search):
        """Test error handling in search command with async function."""
        # Setup mock to raise an exception
        mock_search.side_effect = Exception("Async search failed")

        test_args = ["eprcli", "search", "event", "--name", "test-event"]

        with patch.object(sys, "argv", test_args):
            # The exception should propagate (or be handled gracefully by CLI)
            with self.assertRaises((Exception, SystemExit)):
                main.CmdLine()

    def test_field_handling_utility(self):
        """Test the _handle_fields utility method works correctly."""
        cmd = main.CmdLine.__new__(main.CmdLine)  # Create instance without __init__

        # Test comma-separated values
        result = cmd._handle_fields("field1,field2,field3")
        self.assertEqual(result, ["field1", "field2", "field3"])

        # Test space-separated values
        result = cmd._handle_fields("field1 field2 field3")
        self.assertEqual(result, ["field1", "field2", "field3"])

        # Test single ULID-like value (26 characters)
        ulid = "01ARZ3NDEKTSV4RRFFQ69G5FAV"
        result = cmd._handle_fields(ulid)
        self.assertEqual(result, [ulid])

        # Test None input
        result = cmd._handle_fields(None)
        self.assertEqual(result, [])

        # Test invalid input should raise ValueError
        with self.assertRaises(ValueError):
            cmd._handle_fields("invalid-input")

    def test_import_compatibility(self):
        """Test that all imports still work after async refactoring."""
        # These imports should work without errors
        from epr.client import Client
        from epr.config import Config
        from epr.models import Event

        # Basic smoke test - creating instances should work
        client = Client("http://localhost:8042")
        self.assertIsNotNone(client)

        config = Config(url="http://localhost:8042", token="test-token")
        self.assertIsNotNone(config)

        event = Event()
        self.assertIsNotNone(event)

    @patch("epr.create.create", new_callable=AsyncMock)
    @patch("asyncio.run")
    def test_asyncio_run_usage(self, mock_asyncio_run, mock_create):
        """Test that asyncio.run is properly used for async function calls."""
        mock_asyncio_run.return_value = {"events": [], "event_receivers": [], "event_receiver_groups": []}
        mock_create.return_value = {"events": [], "event_receivers": [], "event_receiver_groups": []}

        test_args = [
            "eprcli",
            "create",
            "event",
            "--name",
            "test-event",
            "--version",
            "1.0.0",
            "--release",
            "stable",
            "--platform-id",
            "linux-x64",
            "--package",
            "test-package",
            "--description",
            "Test event",
            "--payload",
            '{"key": "value"}',
            "--event-receiver-id",
            "test-receiver-id",
        ]

        with patch.object(sys, "argv", test_args):
            try:
                main.CmdLine()
            except SystemExit:
                pass

        # asyncio.run should have been called
        mock_asyncio_run.assert_called()


if __name__ == "__main__":
    unittest.main()
