# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2024 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

from epr import common
from tests import base

class CommonTestCase(base.BaseTestCase):
    def setUp(self):
        super(CommonTestCase, self).setUp()

    def test_hash_string(self):
        assert common.hash_string("hello") == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"

    def test_hash_file(self):
        assert common.hash_file(__file__) == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
        
    def test_find_jsonpath(self):
        assert common.find_jsonpath({"hello": "world"}, "$.hello") == ["world"]

    def test_find_jsonpath_missing(self):
        assert common.find_jsonpath({"hello": "world"}, "$.missing") == []

