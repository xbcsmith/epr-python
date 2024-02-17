# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2023 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""
Classes for holding object data
"""
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List

from .fingerprint import GroupFingerprint, ReceiverFingerprint


class ModelType(Enum):
    EVENT = "Event"
    RECEIVER = "Event_Receiver"
    GROUP = "Event_Receiver_Group"

    def lower(self):
        return self.value.lower()

    def lower_plural(self):
        return self.lower() + "s"


@dataclass
class Model:
    """Base class for data objects. Provides as_dict"""

    def as_dict(self):
        """Get a dictionary containg object properties"""
        return asdict(self)


@dataclass
class Event(Model):
    """Data class for Events"""

    id: str = field(default="", compare=False)
    name: str = ""
    version: str = ""
    release: str = ""
    platform_id: str = ""
    package: str = ""
    description: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    success: bool = False
    created_at: str = field(default="", compare=False)
    event_receiver_id: str = ""


@dataclass
class Event_Receiver(Model):
    """Data class for Event_Receivers"""

    id: str = field(default="", compare=False)
    name: str = ""
    type: str = ""
    version: str = ""
    description: str = ""
    schema: Dict[str, str] = field(default_factory=dict)
    fingerprint: str = ""
    created_at: str = field(default="", compare=False)

    def compute_fingerprint(self):
        return ReceiverFingerprint.new(self.as_dict()).fingerprint


@dataclass
class Event_Receiver_Group(Model):
    """Data class for Event_Receiver_Groups"""

    id: str = field(default="", compare=False)
    name: str = ""
    type: str = ""
    version: str = ""
    description: str = ""
    enabled: bool = False
    event_receiver_ids: List[str] = field(default_factory=list)
    created_at: str = field(default="", compare=False)
    updated_at: str = field(default="", compare=False)
    fingerprint: str = ""

    def compute_fingerprint(self):
        return GroupFingerprint.new(self.as_dict()).fingerprint


@dataclass
class Data(Model):
    """Data class for Data"""

    events = List[Event]
    receivers = List[Event_Receiver]
    receiver_groups = List[Event_Receiver_Group]


@dataclass
class Message(Model):
    """Data class for message to be sent to the message bus"""

    success: bool
    id: str
    specversion: str
    type: str
    source: str
    api_version: str
    name: str
    version: str
    release: str
    platform_id: str
    package: str
    data: Data
