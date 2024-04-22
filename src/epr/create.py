# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2024 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

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
        event = client.create_event(params=e)
        events.append(event)
    event_receivers = []
    for er in config.event_receivers:
        event_receiver = client.create_event_receiver(params=er)
        event_receivers.append(event_receiver)
    event_receiver_groups = []
    for erg in config.event_receiver_groups:
        event_receiver_group = client.create_event_receiver_group(params=erg)
        event_receiver_groups.append(event_receiver_group)

    results = {"events": events, "event_receivers": event_receivers, "event_receiver_groups": event_receiver_groups}
    print(f"{results}")

    import pdb

    pdb.set_trace()
