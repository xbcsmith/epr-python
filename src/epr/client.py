# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2024 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

import json
import logging
from typing import Any, Optional
from urllib.parse import urljoin

import urllib3

from .common import EnhancedJSONEncoder

urllib3.disable_warnings()

logger = logging.getLogger(__name__)


class Client(object):
    def __init__(self, url, headers=None):
        self.url = url
        self.api_version = "v1"
        self.graphql_query = "graphql/query"
        if self.url is None:
            self.url = " http://localhost:8042"
        self.endpoint = "/".join(["api", self.api_version, self.graphql_query])
        self.target = urljoin(self.url, self.endpoint)
        self.headers = {"Content-Type": "application/json"}
        if headers is not None:
            self.headers.update(headers)
        self._operation_map = {
            "search": {
                "events": "FindEventInput!",
                "event_receivers": "FindEventReceiver!",
                "event_receiver_groups": "FindEventReceiverGroup!",
            },
            "mutation": {
                "event": "EventInput!",
                "event_receiver": "EventReceiverInput!",
                "event_receiver_group": "EventReceiverGroupInput!",
            },
            "operation": {
                "events": "event",
                "event_receivers": "event_receiver",
                "event_receiver_groups": "event_receiver_group",
            },
            "create": {
                "event": "create_event",
                "event_receiver": "create_event_receiver",
                "event_receiver_group": "create_event_receiver_group",
            },
        }

    def new_graphql_search_query(self, operation: str, params: dict = None, fields: Optional[list] = None) -> dict:
        variables = dict(obj=params)
        method = self._operation_map["search"][operation]
        op = self._operation_map["operation"][operation]
        _fields = ",".join(fields) if fields is not None else "id"
        query = f"""query ($obj: {method}){{{operation}({op}: $obj) {{ {_fields} }}}}"""
        return {"query": query, "variables": variables}

    def new_graphql_mutation_query(self, operation: str, params: dict = None) -> dict:
        variables = dict(obj=params)
        method = self._operation_map["mutation"][operation]
        op = self._operation_map["create"][operation]
        query = f"query ($obj: {method}){operation}({op}: $obj)"
        return {"query": query, "variables": variables}

    def query(self, query: str, variables: dict = None) -> Any:
        """
        Sends a GraphQL query to the server.

        Args:
            query (str): The GraphQL query string.
            variables (dict, optional): The variables to be used in the query. Defaults to None.

        Returns:
            Any: The response data from the server.
        """
        response = self.post(self.target, data={"query": query, "variables": variables})
        return json.loads(response.decode("utf-8"))

    def post(self, url, data):
        http = urllib3.PoolManager()
        encoded_data = json.dumps(data, cls=EnhancedJSONEncoder).encode("utf-8")
        response = http.request("POST", url, body=encoded_data, headers=self.headers)
        return response.data

    def search(self, operation: str, params: dict = None, fields: list = None) -> Any:
        query = self.new_graphql_search_query(operation, params, fields)
        return self.query(query["query"], query["variables"])

    def mutation(self, operation: str, params: dict = None) -> Any:
        query = self.new_graphql_mutation_query(operation, params)
        return self.query(query["query"], query["variables"])

    def search_events(self, params: dict = None, fields: Optional[list] = None) -> Any:
        return self.search("events", params, fields)

    def search_event_receivers(self, params: dict = None, fields: Optional[list] = None) -> Any:
        return self.search("event_receivers", params, fields)

    def search_event_receiver_groups(self, params: dict = None, fields: Optional[list] = None) -> Any:
        return self.search("event_receiver_groups", params, fields)

    def create_event(self, params: dict = None) -> Any:
        return self.mutation("event", params)

    def create_event_receiver(self, params: dict = None) -> Any:
        return self.mutation("event_receiver", params)

    def create_event_receiver_group(self, params: dict = None) -> Any:
        return self.mutation("event_receiver_group", params)
