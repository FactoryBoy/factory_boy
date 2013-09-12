# -*- coding: utf-8 -*-
# Copyright (c) 2013 Romain Command&
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

"""Tests for factory_boy/SQLAlchemy interactions."""

import factory
from .compat import unittest


try:
    import mongoengine
except ImportError:
    mongoengine = None

if mongoengine:
    from factory.mongoengine import MongoEngineFactory

    class Person(mongoengine.Document):
        name = mongoengine.StringField()

    class PersonFactory(MongoEngineFactory):
        FACTORY_FOR = Person

        name = factory.Sequence(lambda n: 'name%d' % n)



@unittest.skipIf(mongoengine is None, "mongoengine not installed.")
class MongoEngineTestCase(unittest.TestCase):

    def setUp(self):
        mongoengine.connect('factory_boy_test')

    def test_build(self):
        std = PersonFactory.build()
        self.assertEqual('name0', std.name)
        self.assertIsNone(std.id)

    def test_creation(self):
        std1 = PersonFactory.create()
        self.assertEqual('name1', std1.name)
        self.assertIsNotNone(std1.id)


