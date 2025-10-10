# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2024 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

import asyncio


def test_import():
    """Validate epr is importable"""
    import epr

    print(epr)

    assert True


def test_async_client_import():
    """Validate async client functionality is importable and works"""
    from epr.client import Client
    from epr.models import GraphQLQuery

    # Test that we can create a client
    client = Client("http://localhost:8042")
    assert client is not None
    assert client.url == "http://localhost:8042"

    # Test that we can create GraphQL queries with dict variables
    query = GraphQLQuery(query="query test { events { id } }", variables={"name": "test", "version": "1.0"})
    assert query.query == "query test { events { id } }"
    assert query.variables["name"] == "test"

    print("✓ Async client imports and basic functionality work")


def test_async_client_context_manager():
    """Test that async client context manager works"""

    async def async_test():
        from epr.client import Client

        async with Client("http://localhost:8042") as client:
            assert client is not None
            assert client._client is not None  # HTTP client should be created
            return True

    # Run the async test
    result = asyncio.run(async_test())
    assert result is True

    print("✓ Async client context manager works")


def test_async_search_create_imports():
    """Test that async search and create functions are importable"""
    from epr.create import create
    from epr.search import search

    # These should be async functions now
    assert asyncio.iscoroutinefunction(search)
    assert asyncio.iscoroutinefunction(create)

    print("✓ Async search and create functions are properly async")
