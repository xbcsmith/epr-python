# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2024 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

import dataclasses
import hashlib
import json
import logging
import os
import sys

from jsonpath_ng import parse

from .errors import debug_except_hook

logger = logging.getLogger(__name__)


debug = os.environ.get("EPR_DEBUG")
if debug:
    sys.excepthook = debug_except_hook
    logger.setLevel(logging.DEBUG)


def hash_file(path):
    BLOCKSIZE = 65536
    hasher = hashlib.sha256()
    with open(path, "rb") as fh:
        buf = fh.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = fh.read(BLOCKSIZE)
    result = "sha256:" + hasher.hexdigest()
    return result


def hash_string(data):
    hasher = hashlib.sha256()
    hasher.update(data.encode("utf-8"))
    return hasher.hexdigest()


def find_jsonpath(data, expr):
    jsonpath_expression = parse(expr)
    match = jsonpath_expression.find(data)
    return [x.value for x in match]


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)
