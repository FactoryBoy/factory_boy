# -*- coding: utf-8 -*-
# Copyright: See the LICENSE file.

"""Tests for factory_boy/SQLAlchemy interactions."""

import factory
from .compat import mock
import warnings
import unittest

from factory.alchemy import SQLAlchemyModelFactory
from .alchemyapp import models


class StandardFactory(SQLAlchemyModelFactory):
    class Meta:
        model = models.StandardModel
        sqlalchemy_session = models.session

    id = factory.Sequence(lambda n: n)
    foo = factory.Sequence(lambda n: 'foo%d' % n)


class NonIntegerPkFactory(SQLAlchemyModelFactory):
    class Meta:
        model = models.NonIntegerPk
        sqlalchemy_session = models.session

    id = factory.Sequence(lambda n: 'foo%d' % n)


class NoSessionFactory(SQLAlchemyModelFactory):
    class Meta:
        model = models.StandardModel
        sqlalchemy_session = None

    id = factory.Sequence(lambda n: n)


class SQLAlchemyPkSequenceTestCase(unittest.TestCase):

    def setUp(self):
        super(SQLAlchemyPkSequenceTestCase, self).setUp()
        StandardFactory.reset_sequence(1)
        NonIntegerPkFactory._meta.sqlalchemy_session.rollback()

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
        self.assertEqual('foo0', std2.foo)
        self.assertEqual(0, std2.id)

    def test_pk_force_value(self):
        std1 = StandardFactory.create(id=10)
        self.assertEqual('foo1', std1.foo)  # sequence and pk are unrelated
        self.assertEqual(10, std1.id)

        StandardFactory.reset_sequence()
        std2 = StandardFactory.create()
        self.assertEqual('foo0', std2.foo)  # Sequence doesn't care about pk
        self.assertEqual(0, std2.id)


class SQLAlchemySessionPersistenceTestCase(unittest.TestCase):
    def setUp(self):
        super(SQLAlchemySessionPersistenceTestCase, self).setUp()
        self.mock_session = mock.NonCallableMagicMock(spec=models.session)

    def test_flushing(self):
        class FlushingPersistenceFactory(StandardFactory):
            class Meta:
                sqlalchemy_session = self.mock_session
                sqlalchemy_session_persistence = 'flush'

        self.mock_session.commit.assert_not_called()
        self.mock_session.flush.assert_not_called()

        FlushingPersistenceFactory.create()
        self.mock_session.commit.assert_not_called()
        self.mock_session.flush.assert_called_once_with()

    def test_committing(self):
        class CommittingPersistenceFactory(StandardFactory):
            class Meta:
                sqlalchemy_session = self.mock_session
                sqlalchemy_session_persistence = 'commit'

        self.mock_session.commit.assert_not_called()
        self.mock_session.flush.assert_not_called()

        CommittingPersistenceFactory.create()
        self.mock_session.commit.assert_called_once_with()
        self.mock_session.flush.assert_not_called()

    def test_noflush_nocommit(self):
        class InactivePersistenceFactory(StandardFactory):
            class Meta:
                sqlalchemy_session = self.mock_session
                sqlalchemy_session_persistence = None

        self.mock_session.commit.assert_not_called()
        self.mock_session.flush.assert_not_called()

        InactivePersistenceFactory.create()
        self.mock_session.commit.assert_not_called()
        self.mock_session.flush.assert_not_called()

    def test_type_error(self):
        with self.assertRaises(TypeError):
            class BadPersistenceFactory(StandardFactory):
                class Meta:
                    sqlalchemy_session_persistence = 'invalid_persistence_option'
                    model = models.StandardModel

    def test_force_flush_deprecation(self):
        with warnings.catch_warnings(record=True) as warning_list:
            class OutdatedPersistenceFactory(StandardFactory):
                class Meta:
                    force_flush = True
                    sqlalchemy_session = self.mock_session

        # There should be *1* DeprecationWarning
        self.assertEqual(len(warning_list), 1)
        warning = warning_list[0]
        self.assertTrue(issubclass(warning.category, DeprecationWarning))

        # The warning text should point to the class declaration.
        text = warnings.formatwarning(warning.message, warning.category, warning.filename, warning.lineno)
        self.assertIn('test_alchemy.py', text)
        self.assertIn('class OutdatedPersistenceFactory', text)

        # However, we shall keep the old-style behavior.
        self.mock_session.commit.assert_not_called()
        self.mock_session.flush.assert_not_called()

        OutdatedPersistenceFactory.create()
        self.mock_session.commit.assert_not_called()
        self.mock_session.flush.assert_called_once_with()


class SQLAlchemyNonIntegerPkTestCase(unittest.TestCase):
    def setUp(self):
        super(SQLAlchemyNonIntegerPkTestCase, self).setUp()
        NonIntegerPkFactory.reset_sequence()
        NonIntegerPkFactory._meta.sqlalchemy_session.rollback()

    def test_first(self):
        nonint = NonIntegerPkFactory.build()
        self.assertEqual('foo0', nonint.id)

    def test_many(self):
        nonint1 = NonIntegerPkFactory.build()
        nonint2 = NonIntegerPkFactory.build()

        self.assertEqual('foo0', nonint1.id)
        self.assertEqual('foo1', nonint2.id)

    def test_creation(self):
        nonint1 = NonIntegerPkFactory.create()
        self.assertEqual('foo0', nonint1.id)

        NonIntegerPkFactory.reset_sequence()
        nonint2 = NonIntegerPkFactory.build()
        self.assertEqual('foo0', nonint2.id)

    def test_force_pk(self):
        nonint1 = NonIntegerPkFactory.create(id='foo10')
        self.assertEqual('foo10', nonint1.id)

        NonIntegerPkFactory.reset_sequence()
        nonint2 = NonIntegerPkFactory.create()
        self.assertEqual('foo0', nonint2.id)


class SQLAlchemyNoSessionTestCase(unittest.TestCase):

    def test_create_raises_exception_when_no_session_was_set(self):
        with self.assertRaises(RuntimeError):
            NoSessionFactory.create()

    def test_build_does_not_raises_exception_when_no_session_was_set(self):
        inst0 = NoSessionFactory.build()
        inst1 = NoSessionFactory.build()
        self.assertEqual(inst0.id, 0)
        self.assertEqual(inst1.id, 1)
