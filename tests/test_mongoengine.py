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

"""Tests for factory_boy/MongoEngine interactions."""

import factory
import os
from .compat import unittest


try:
    import mongoengine
except ImportError:
    mongoengine = None

if os.environ.get('SKIP_MONGOENGINE') == '1':
    mongoengine = None

if mongoengine:
    from factory.mongoengine import MongoEngineFactory

    class Address(mongoengine.EmbeddedDocument):
        street = mongoengine.StringField()

    class Person(mongoengine.Document):
        name = mongoengine.StringField()
        address = mongoengine.EmbeddedDocumentField(Address)

    class AddressFactory(MongoEngineFactory):
        class Meta:
            model = Address

        street = factory.Sequence(lambda n: 'street%d' % n)

    class PersonFactory(MongoEngineFactory):
        class Meta:
            model = Person

        name = factory.Sequence(lambda n: 'name%d' % n)
        address = factory.SubFactory(AddressFactory)


@unittest.skipIf(mongoengine is None, "mongoengine not installed.")
class MongoEngineTestCase(unittest.TestCase):

    db_name = os.environ.get('MONGO_DATABASE', 'factory_boy_test')
    db_host = os.environ.get('MONGO_HOST', 'localhost')
    db_port = int(os.environ.get('MONGO_PORT', '27017'))
    server_timeout_ms = int(os.environ.get('MONGO_TIMEOUT', '300'))

    @classmethod
    def setUpClass(cls):
        from pymongo import read_preferences as mongo_rp
        cls.db = mongoengine.connect(
            db=cls.db_name,
            host=cls.db_host,
            port=cls.db_port,
            # PyMongo>=2.1 requires an explicit read_preference.
            read_preference=mongo_rp.ReadPreference.PRIMARY,
            # PyMongo>=2.1 has a 20s timeout, use 100ms instead
            serverselectiontimeoutms=cls.server_timeout_ms,
        )

    @classmethod
    def tearDownClass(cls):
        cls.db.drop_database(cls.db_name)

    def setUp(self):
        mongoengine.connect('factory_boy_test')

    def test_build(self):
        std = PersonFactory.build()
        self.assertEqual('name0', std.name)
        self.assertEqual('street0', std.address.street)
        self.assertIsNone(std.id)

    def test_creation(self):
        std1 = PersonFactory.create()
        self.assertEqual('name1', std1.name)
        self.assertEqual('street1', std1.address.street)
        self.assertIsNotNone(std1.id)
