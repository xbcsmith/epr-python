# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2024 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

import json
import logging
from typing import Any, Optional
from urllib.parse import urljoin

import urllib3

from .common import EnhancedJSONEncoder
from .models import GraphQLQuery

urllib3.disable_warnings()

logger = logging.getLogger(__name__)


class Client(object):
    def __init__(self, url, headers=None):
        self.url = url
        self.api_version = "v1"
        self.graphql_query = "graphql/query"
        if self.url is None:
            self.url = "http://localhost:8042"
        self.endpoint = "/".join(["api", self.api_version, self.graphql_query])
        self.target = urljoin(self.url, self.endpoint)
        self.headers = {"Content-Type": "application/json"}
        if headers is not None:
            self.headers.update(headers)
        self._operation_map = {
            "search": {
                "events": "FindEventInput!",
                "event_receivers": "FindEventReceiverInput!",
                "event_receiver_groups": "FindEventReceiverGroupInput!",
            },
            "mutation": {
                "create_event": "CreateEventInput!",
                "create_event_receiver": "CreateEventReceiverInput!",
                "create_event_receiver_group": "CreateEventReceiverGroupInput!",
            },
            "operation": {
                "events": "event",
                "event_receivers": "event_receiver",
                "event_receiver_groups": "event_receiver_group",
            },
            "create": {
                "create_event": "event",
                "create_event_receiver": "event_receiver",
                "create_event_receiver_group": "event_receiver_group",
            },
        }

    def _new_graphql_search_query(
        self, operation: str, params: Optional[dict] = None, fields: Optional[list] = None
    ) -> GraphQLQuery:
        """
        Generates a new GraphQL search query based on the given operation, parameters, and fields.

        Args:
            operation (str): The operation to be performed.
            params (dict, optional): The parameters for the search query. Defaults to None.
            fields (list, optional): The fields to be included in the search results. Defaults to None.

        Returns:
            dict: A dictionary containing the generated GraphQL query and variables.
                - query (str): The generated GraphQL query string.
                - variables (dict): The variables to be used in the query.

        Example:
            new_graphql_search_query("events", {"name": "foo"}, ["id", "name", "email"])
            # Returns:
            # GraphQLQuery({
            #     "query": "query ($obj: FindEventInput!) {events(event: $obj) {id, name, version, release}}",
            #     "variables": {"obj": {"name": "foo"}}
            # })
        """
        variables = dict(obj=params)
        method = self._operation_map["search"][operation]
        op = self._operation_map["operation"][operation]
        _fields = ",".join(fields) if fields is not None else "id"
        query = f"""query ($obj: {method}){{{operation}({op}: $obj) {{ {_fields} }}}}"""
        return GraphQLQuery(query=query, variables=variables)

    def _new_graphql_mutation_query(self, operation: str, params: Optional[dict] = None) -> GraphQLQuery:
        """
        Creates a new GraphQL mutation query based on the provided operation and parameters.

        Args:
            operation (str): The operation to be performed.
            params (dict, optional): The parameters for the mutation query. Defaults to None.

        Returns:
            dict: A dictionary containing the query and variables for the mutation.

        Example:
            new_graphql_mutation_query("create_event", {"name": "foo", "version": "1.0.1"})
            # Returns:
            # GraphQLQuery({
            #     "query": "mutation ($obj: CreateEventInput!) {create_event(event: $obj) {id, name, version}}",
            #     "variables": {"obj": {"name": "foo", "version": "1.0.1"}}
            # })
        """
        variables = dict(obj=params)
        method = self._operation_map["mutation"][operation]
        op = self._operation_map["create"][operation]
        query = f"""mutation ($obj: {method}){{{operation}({op}: $obj)}}"""
        return GraphQLQuery(query=query, variables=variables)

    def _query(self, query: GraphQLQuery) -> Any:
        """
        Sends a GraphQL query to the server.

        Args:
            query (str): The GraphQL query string.
            variables (dict, optional): The variables to be used in the query. Defaults to None.

        Returns:
            Any: The response data from the server.
        """
        response = self._post(self.target, data=query.as_dict())
        return json.loads(response.decode("utf-8"))

    def _post(self, url: str, data: dict) -> bytes:
        """
        Sends a POST request to the specified URL with the provided data.

        Args:
            url (str): The URL to which the POST request will be sent.
            data (dict): The data to be sent in the POST request.

        Returns:
            bytes: The data received in the response to the POST request.
        """
        timeout = urllib3.Timeout(connect=2.0, read=10.0)
        http = urllib3.PoolManager(timeout=timeout)
        encoded_data = json.dumps(data, cls=EnhancedJSONEncoder).encode("utf-8")
        response = http.request("POST", url, body=encoded_data, headers=self.headers)
        return response.data

    def _search(self, operation: str, params: Optional[dict] = None, fields: Optional[list] = None) -> Any:
        """
        Sends a GraphQL search query to the server.

        Args:
            operation (str): The operation to be performed.
            params (dict, optional): The parameters for the search query. Defaults to None.
            fields (list, optional): The fields to be included in the search results. Defaults to None.

        Returns:
            Any: The response data from the server.
        """
        query = self._new_graphql_search_query(operation, params, fields)

        return self._query(query=query)

    def _mutation(self, operation: str, params: Optional[dict] = None) -> Any:
        """
        Sends a GraphQL mutation query to the server.

        Args:
            operation (str): The operation to be performed.
            params (dict, optional): The parameters for the mutation query. Defaults to None.

        Returns:
            Any: The response data from the server.

        This function creates a new GraphQL mutation query using the provided operation and parameters.
        It then sends the query to the server using the `query` method and returns the response data.
        """
        query = self._new_graphql_mutation_query(operation, params)
        return self._query(query)

    def search_events(self, params: Optional[dict] = None, fields: Optional[list] = None) -> Any:
        """
        Searches for events based on the provided parameters and fields.

        Args:
            params (dict, optional): Parameters for the search query. Defaults to None.
            fields (list, optional): Fields to be included in the search results. Defaults to None.

        Returns:
            Any: The search results for events based on the provided parameters and fields.

        This function performs a search for events based on the provided parameters and fields.
        """
        return self._search("events", params, fields)

    def search_event_receivers(self, params: Optional[dict] = None, fields: Optional[list] = None) -> Any:
        """
        Search for event receivers based on the given parameters and fields.

        Args:
            params (dict, optional): The parameters to filter the search by. Defaults to None.
            fields (list, optional): The fields to include in the search results. Defaults to None.

        Returns:
            Any: The search results.

        This function performs a search for event receivers based on the given parameters and fields.
        """
        return self._search("event_receivers", params, fields)

    def search_event_receiver_groups(self, params: Optional[dict] = None, fields: Optional[list] = None) -> Any:
        """
        Search for event receiver groups based on the given parameters and fields.

        Args:
            params (dict, optional): The parameters to filter the search by. Defaults to None.
            fields (list, optional): The fields to include in the search results. Defaults to None.

        Returns:
            Any: The search results for event receiver groups based on the provided parameters and fields.

        This function performs a search for event receiver groups based on the given parameters and fields.
        """
        return self._search("event_receiver_groups", params, fields)

    def create_event(self, params: Optional[dict] = None) -> Any:
        """
        Creates an event using the provided parameters.

        Args:
            params (dict, optional): The parameters for creating the event. Defaults to None.

        Returns:
            Any: The result of creating the event.

        This function sends a mutation query to create an event using the provided parameters.
        """
        return self._mutation("create_event", params)

    def create_event_receiver(self, params: Optional[dict] = None) -> Any:
        """
        Creates an event receiver using the provided parameters.

        Args:
            params (dict, optional): The parameters for creating the event receiver. Defaults to None.

        Returns:
            Any: The result of creating the event receiver.

        This function sends a mutation query to create an event receiver using the provided parameters.
        """
        return self._mutation("create_event_receiver", params)

    def create_event_receiver_group(self, params: Optional[dict] = None) -> Any:
        """
        Creates an event receiver group using the provided parameters.

        Args:
            params (dict, optional): The parameters for creating the event receiver group. Defaults to None.

        Returns:
            Any: The result of creating the event receiver group.

        This function sends a mutation query to create an event receiver group using the provided parameters.
        """
        return self._mutation("create_event_receiver_group", params)
