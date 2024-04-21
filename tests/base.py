# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: © 2024 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0


import os
import shutil
import tempfile
import unittest


class BaseTestCase(unittest.TestCase):
    test_dir = "epr-test-"

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix=self.test_dir)
        self.addCleanup(shutil.rmtree, self.test_dir, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.test_dir)

    def mkfile(self, path, contents=None):
        if contents is None:
            contents = "\n"
        fpath = os.path.join(self.test_dir, path)
        if isinstance(contents, str):
            mode = "w"
        else:
            mode = "wb"
        with open(fpath, mode) as fh:
            fh.write(contents)
        return fpath

    def mkdir(self, path):
        path = os.path.join(self.test_dir, path)
        os.makedirs(path)
        return path
