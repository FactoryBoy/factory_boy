# -*- coding: utf-8 -*-
# Copyright (c) 2010 Mark Sandstrom
# Copyright (c) 2011-2013 Raphaël Barrois
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

"""Tests for deprecated features."""

import warnings

import factory

from .compat import mock, unittest
from . import tools


class DeprecationTests(unittest.TestCase):
    def test_factory_for(self):
        class Foo(object):
            pass

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            class FooFactory(factory.Factory):
                FACTORY_FOR = Foo

            self.assertEqual(1, len(w))
            warning = w[0]
            # Message is indeed related to the current file
            # This is to ensure error messages are readable by end users.
            self.assertIn(warning.filename, __file__)
            self.assertIn('FACTORY_FOR', str(warning.message))
            self.assertIn('model', str(warning.message))
