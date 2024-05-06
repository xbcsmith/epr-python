# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2024 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0

import mock

from epr import errors
from tests import base


class ErrorsTestCase(base.BaseTestCase):
    def setUp(self):
        super(ErrorsTestCase, self).setUp()
        self.errors = dict(
            BaseError="BaseError",
            RunCmdError="BaseError",
            CmdMissingError="BaseError",
            FileNotFoundError="BaseError",
            InvalidKeyError="BaseError",
            KeyNotFoundError="BaseError",
            NotImplemented="BaseError",
            EPRError="EPRError",
            GraphQLError="EPRError",
        )

    def test_errors(self):
        for fnc, msg in self.errors.items():
            assert hasattr(errors, fnc)
            exc = getattr(errors, fnc)
            test_exc = FakeTestClass(exc, msg)
            self.assertRaises(exc, test_exc.raise_exception)

    @mock.patch("epr.errors.traceback.print_exception")
    @mock.patch("epr.errors.pdb.post_mortem")
    def test_dbg_hook(self, mock_pdb, mock_trc):
        hook = errors.debug_except_hook
        exc_type, exc_value, exc_tb = fake_exception()
        hook(exc_type, exc_value, exc_tb)
        mock_trc.assert_called_once_with(exc_type, exc_value, exc_tb)
        mock_pdb.assert_called_once_with(exc_tb)


class FakeTestClass:
    def __init__(self, exc, msg):
        self._exc = exc
        self._msg = msg

    def raise_exception(self):
        raise self._exc(self._msg)


def fake_exception():
    code = FakeCode("foo.py", "non_existent_function")
    frame = FakeFrame(code, {})
    tb = FakeTraceback([frame], [1])
    exc = FakeException("foo").with_traceback(tb)
    return FakeException, exc, tb


class FakeCode(object):
    def __init__(self, co_filename, co_name):
        self.co_filename = co_filename
        self.co_name = co_name


class FakeFrame(object):
    def __init__(self, f_code, f_globals):
        self.f_code = f_code
        self.f_globals = f_globals


class FakeTraceback(object):
    def __init__(self, frames, line_nums):
        if len(frames) != len(line_nums):
            raise ValueError("FOooooo!")
        self._frames = frames
        self._line_nums = line_nums
        self.tb_frame = frames[0]
        self.tb_lineno = line_nums[0]

    @property
    def tb_next(self):
        if len(self._frames) > 1:
            return FakeTraceback(self._frames[1:], self._line_nums[1:])


class FakeException(Exception):
    def __init__(self, *args, **kwargs):
        self._tb = None
        super(FakeException, self).__init__(*args, **kwargs)

    @property
    def __traceback__(self):
        return self._tb

    @__traceback__.setter
    def __traceback__(self, value):
        self._tb = value

    def with_traceback(self, value):
        self._tb = value
        return self
