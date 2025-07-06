# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2024 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

import json

from .client import Client
from .config import Config


def create(config: Config):
    """Create an event provenance registry object"""

    url = config.url
    if url is None:
        url = "http://localhost:8042"
    # headers = {"Authorization": "Bearer " + config.token}
    headers = {}
    client = Client(url, headers=headers)

    events = []
    for e in config.events:
        event = client.create_event(params=e.as_dict())
        event_id = event["data"]["create_event"]
        events.append(event_id)
    event_receivers = []
    for er in config.event_receivers:
        event_receiver = client.create_event_receiver(params=er.as_dict())
        event_receiver_id = event_receiver["data"]["create_event_receiver"]
        event_receivers.append(event_receiver_id)
    event_receiver_groups = []
    for erg in config.event_receiver_groups:
        event_receiver_group = client.create_event_receiver_group(params=erg.as_dict())
        event_receiver_group_id = event_receiver_group["data"]["create_event_receiver_group"]
        event_receiver_groups.append(event_receiver_group_id)

    results = {"events": events, "event_receivers": event_receivers, "event_receiver_groups": event_receiver_groups}
    stdout = json.dumps(results)
    print(f"{stdout}")

    return results
