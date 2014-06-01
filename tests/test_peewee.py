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

"""Tests for factory_boy/peewee interactions."""

import factory
from .compat import unittest


try:
    import peewee
except ImportError:
    peewee = None

if peewee:
    from factory.peewee import PeeweeModelFactory
    from .peeweeapp import models
else:

    class Fake(object):
        class Meta:
            database = None

    models = Fake()
    models.StandardModel = Fake()
    models.NonIntegerPk = Fake()
    models.session = Fake()
    PeeweeModelFactory = Fake


class StandardFactory(PeeweeModelFactory):
    class Meta:
        model = models.StandardModel
        database = models.database

    id = factory.Sequence(lambda n: n)
    foo = factory.Sequence(lambda n: 'foo%d' % n)


class NonIntegerPkFactory(PeeweeModelFactory):
    class Meta:
        model = models.NonIntegerPk
        database = models.database

    id = factory.Sequence(lambda n: 'foo%d' % n)


@unittest.skipIf(peewee is None, "peewee not installed.")
class PeeweePkSequenceTestCase(unittest.TestCase):

    def setUp(self):
        super(PeeweePkSequenceTestCase, self).setUp()
        StandardFactory.reset_sequence(1)
        StandardFactory._meta.database.rollback()

    def test_pk_first(self):
        std = StandardFactory.build()
        self.assertEqual('foo1', std.foo)

    def test_pk_many(self):
        std1 = StandardFactory.build()
        std2 = StandardFactory.build()
        self.assertEqual('foo1', std1.foo)
        self.assertEqual('foo2', std2.foo)

    def test_pk_creation(self):
        std1 = StandardFactory.create()
        self.assertEqual('foo1', std1.foo)
        self.assertEqual(1, std1.id)

        StandardFactory.reset_sequence()
        std2 = StandardFactory.create()
        self.assertEqual('foo2', std2.foo)
        self.assertEqual(2, std2.id)

    def test_pk_force_value(self):
        std1 = StandardFactory.create(id=10)
        self.assertEqual('foo1', std1.foo)  # sequence was set before pk
        self.assertEqual(10, std1.id)

        StandardFactory.reset_sequence()
        std2 = StandardFactory.create()
        self.assertEqual('foo11', std2.foo)
        self.assertEqual(11, std2.id)


@unittest.skipIf(peewee is None, "peewee not installed.")
class PeeweeNonIntegerPkTestCase(unittest.TestCase):
    def setUp(self):
        super(PeeweeNonIntegerPkTestCase, self).setUp()
        NonIntegerPkFactory.reset_sequence()
        NonIntegerPkFactory._meta.database.rollback()

    def test_first(self):
        nonint = NonIntegerPkFactory.build()
        self.assertEqual('foo1', nonint.id)

    def test_many(self):
        nonint1 = NonIntegerPkFactory.build()
        nonint2 = NonIntegerPkFactory.build()

        self.assertEqual('foo1', nonint1.id)
        self.assertEqual('foo2', nonint2.id)

    def test_creation(self):
        nonint1 = NonIntegerPkFactory.create()
        self.assertEqual('foo1', nonint1.id)

        NonIntegerPkFactory.reset_sequence()
        nonint2 = NonIntegerPkFactory.build()
        self.assertEqual('foo1', nonint2.id)

    def test_force_pk(self):
        nonint1 = NonIntegerPkFactory.create(id='foo10')
        self.assertEqual('foo10', nonint1.id)

        NonIntegerPkFactory.reset_sequence()
        nonint2 = NonIntegerPkFactory.create()
        self.assertEqual('foo1', nonint2.id)
