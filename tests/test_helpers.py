# -*- coding: utf-8 -*-
# Copyright (c) 2010 Mark Sandstrom
# Copyright (c) 2011-2015 Raphaël Barrois
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import logging

from factory import helpers

from .compat import io, unittest


class DebugTest(unittest.TestCase):
    """Tests for the 'factory.debug()' helper."""

    def test_default_logger(self):
        stream1 = io.StringIO()
        stream2 = io.StringIO()

        l = logging.getLogger('factory.test')
        h = logging.StreamHandler(stream1)
        h.setLevel(logging.INFO)
        l.addHandler(h)

        # Non-debug: no text gets out
        l.debug("Test")
        self.assertEqual('', stream1.getvalue())

        with helpers.debug(stream=stream2):
            # Debug: text goes to new stream only
            l.debug("Test2")

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

