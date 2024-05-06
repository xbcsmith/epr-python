# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2024 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

from dataclasses import asdict, dataclass, field
from typing import List

from .models import Event, EventReceiver, EventReceiverGroup


@dataclass
class Config:
    """Data class for Config"""

    url: str
    token: str
    debug: bool = False

    events: List[Event] = field(default_factory=list)
    event_receivers: List[EventReceiver] = field(default_factory=list)
    event_receiver_groups: List[EventReceiverGroup] = field(default_factory=list)

    event_fields: List[str] = field(default_factory=list)
    event_receiver_fields: List[str] = field(default_factory=list)
    event_receiver_group_fields: List[str] = field(default_factory=list)

    def as_dict(self):
        """Get a dictionary containing object properties"""
        return asdict(self)
