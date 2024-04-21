# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2024 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

from epr import constants
from tests import base


class ConstantsTestCase(base.BaseTestCase):
    def setUp(self):
        super(ConstantsTestCase, self).setUp()
        self.data = dict(
            __title__=(str, "epr"),
            __version__=(str, "0.1.0"),
            __build__=(str, "1"),
            __author__=(str, "Brett Smith"),
            __license__=(str, "Apache 2.0"),
            __version_info__=(tuple, tuple("0.1.0".split("."))),
        )

    def test_constants(self):
        for k, v in self.data.items():
            const = getattr(constants, k)
            assert isinstance(const, v[0])
            if "version" not in k:
                assert const == v[1]

    def test_version(self):
        assert len(constants.__version__.split(".")) >= 3
        assert len(constants.__version_info__) >= 3
        assert tuple(constants.__version__.split(".")) == constants.__version_info__
