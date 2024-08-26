# Copyright: See the LICENSE file.

"""Tests for factory_boy/MongoEngine interactions."""

import os
import unittest

try:
    import mongoengine
except ImportError:
    raise unittest.SkipTest("mongodb tests disabled.")

import mongomock

import factory
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
            mongo_client_class=mongomock.MongoClient,
            # PyMongo>=2.1 requires an explicit read_preference.
            read_preference=mongo_rp.ReadPreference.PRIMARY,
            # PyMongo>=2.1 has a 20s timeout, use 100ms instead
            serverselectiontimeoutms=cls.server_timeout_ms,
            uuidRepresentation='standard',
        )

    @classmethod
    def tearDownClass(cls):
        cls.db.drop_database(cls.db_name)

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
