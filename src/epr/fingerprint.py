# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2024 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

import hashlib


class Fingerprint(object):
    def __init__(self, data, keys):
        self._data = data
        self._keys = sorted(keys)
        self._fingerprint = None
        if self._check():
            self._fingerprint = self._calculate()

    def _hash_string(self, data):
        hasher = hashlib.sha256()
        hasher.update(data.encode("utf-8"))
        return hasher.hexdigest()

    def _check(self):
        for k in self._keys:
            if not self._data.get(k, False):
                return False
        return True

    def _calculate(self):
        seed = "v1"
        for k in self._keys:
            v = self._data.get(k)
            if isinstance(v, (list, tuple)):
                for x in v:
                    seed += " " + str(x)
            elif isinstance(v, dict):
                for x, y in v.items():
                    seed += " " + str(x) + " " + str(y)
            else:
                seed += " " + str(v)
        print("SEED : %s" % seed)
        return self._hash_string(seed)

    @property
    def fingerprint(self):
        return self._fingerprint

    @classmethod
    def new(cls, data, keys):
        return cls(data, keys)


class ReceiverFingerprint(Fingerprint):
    def __init__(self, data):
        self._data = data
        self._keys = ("type", "description", "name", "version")
        self._fingerprint = None
        if self._check():
            self._fingerprint = self._calculate()

    @classmethod
    def new(cls, data):
        return cls(data)


class GroupFingerprint(Fingerprint):
    def __init__(self, data):
        self._data = data
        self._keys = ("type", "description", "name", "version", "enabled", "event_receiver_ids")
        self._fingerprint = None
        if self._check():
            self._fingerprint = self._calculate()

    @classmethod
    def new(cls, data):
        return cls(data)
