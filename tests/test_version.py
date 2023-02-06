# Copyright: See the LICENSE file.

import unittest

import factory


class VersionTestCase(unittest.TestCase):
    def test_version(self):
        self.assertEqual(factory.__version__, "3.2.1.dev0")
