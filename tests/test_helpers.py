# -*- coding: utf-8 -*-
# Copyright: See the LICENSE file.

import logging
import unittest

from factory import helpers

from .compat import io


class DebugTest(unittest.TestCase):
    """Tests for the 'factory.debug()' helper."""

    def test_default_logger(self):
        stream1 = io.StringIO()
        stream2 = io.StringIO()

        logger = logging.getLogger('factory.test')
        h = logging.StreamHandler(stream1)
        h.setLevel(logging.INFO)
        logger.addHandler(h)

        # Non-debug: no text gets out
        logger.debug("Test")
        self.assertEqual('', stream1.getvalue())

        with helpers.debug(stream=stream2):
            # Debug: text goes to new stream only
            logger.debug("Test2")

        self.assertEqual('', stream1.getvalue())
        self.assertEqual("Test2\n", stream2.getvalue())

    def test_alternate_logger(self):
        stream1 = io.StringIO()
        stream2 = io.StringIO()

        l1 = logging.getLogger('factory.test')
        l2 = logging.getLogger('factory.foo')
        h = logging.StreamHandler(stream1)
        h.setLevel(logging.DEBUG)
        l2.addHandler(h)

        # Non-debug: no text gets out
        l1.debug("Test")
        self.assertEqual('', stream1.getvalue())
        l2.debug("Test")
        self.assertEqual('', stream1.getvalue())

        with helpers.debug('factory.test', stream=stream2):
            # Debug: text goes to new stream only
            l1.debug("Test2")
            l2.debug("Test3")

        self.assertEqual("", stream1.getvalue())
        self.assertEqual("Test2\n", stream2.getvalue())
