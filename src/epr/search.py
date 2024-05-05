# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2024 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

import json

from .client import Client
from .config import Config


def search(config: Config):
    """Search for events and event receivers"""

    url = config.url
    if url is None:
        url = "http://localhost:8042"
    # headers = {"Authorization": "Bearer " + config.token}
    headers = {}
    client = Client(url, headers=headers)

    events = []
    for e in config.events:
        fields = config.event_fields
        if fields is None:
            fields = [
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
        event = client.search_events(params=e.as_dict_query(), fields=fields)
        event_result = event["data"]["events"][-1]
        events.append(event_result)
    event_receivers = []
    for er in config.event_receivers:
        fields = config.event_receiver_fields
        if fields is None:
            fields = ["id", "name", "type", "version", "description", "schema", "fingerprint", "created_at"]
        event_receiver = client.search_event_receivers(params=er.as_dict_query(), fields=fields)
        event_receiver_result = event_receiver["data"]["event_receivers"][-1]
        event_receivers.append(event_receiver_result)
    event_receiver_groups = []
    for erg in config.event_receiver_groups:
        fields = config.event_receiver_group_fields
        if fields is None:
            fields = ["id", "name", "type", "version", "description", "enabled", "created_at"]
        event_receiver_group = client.search_event_receiver_groups(params=erg.as_dict_query(), fields=fields)
        event_receiver_group_result = event_receiver_group["data"]["event_receiver_groups"][-1]
        event_receiver_groups.append(event_receiver_group_result)

    results = {"events": events, "event_receivers": event_receivers, "event_receiver_groups": event_receiver_groups}
    stdout = json.dumps(results)
    print(f"{stdout}")

    return results
