# Copyright: See the LICENSE file.

"""Tests for factory_boy/SQLAlchemy interactions."""

import unittest
from unittest import mock

try:
    import sqlalchemy
except ImportError:
    raise unittest.SkipTest("sqlalchemy tests disabled.")

import factory
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


class MultifieldModelFactory(SQLAlchemyModelFactory):
    class Meta:
        model = models.MultiFieldModel
        sqlalchemy_get_or_create = ('slug',)
        sqlalchemy_session = models.session
        sqlalchemy_session_persistence = 'commit'

    id = factory.Sequence(lambda n: n)
    foo = factory.Sequence(lambda n: 'foo%d' % n)


class WithGetOrCreateFieldFactory(SQLAlchemyModelFactory):
    class Meta:
        model = models.StandardModel
        sqlalchemy_get_or_create = ('foo',)
        sqlalchemy_session = models.session
        sqlalchemy_session_persistence = 'commit'

    id = factory.Sequence(lambda n: n)
    foo = factory.Sequence(lambda n: 'foo%d' % n)


class WithMultipleGetOrCreateFieldsFactory(SQLAlchemyModelFactory):
    class Meta:
        model = models.MultifieldUniqueModel
        sqlalchemy_get_or_create = ("slug", "text",)
        sqlalchemy_session = models.session
        sqlalchemy_session_persistence = 'commit'

    id = factory.Sequence(lambda n: n)
    slug = factory.Sequence(lambda n: "slug%s" % n)
    text = factory.Sequence(lambda n: "text%s" % n)


class TransactionTestCase(unittest.TestCase):
    def setUp(self):
        models.Base.metadata.create_all(models.engine)

    def tearDown(self):
        models.session.remove()
        models.Base.metadata.drop_all(models.engine)


class SQLAlchemyPkSequenceTestCase(TransactionTestCase):
    def setUp(self):
        super().setUp()
        StandardFactory.reset_sequence(1)

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


class SQLAlchemyGetOrCreateTests(TransactionTestCase):
    def test_simple_call(self):
        obj1 = WithGetOrCreateFieldFactory(foo='foo1')
        obj2 = WithGetOrCreateFieldFactory(foo='foo1')
        self.assertEqual(obj1, obj2)

    def test_missing_arg(self):
        with self.assertRaises(factory.FactoryError):
            MultifieldModelFactory()

    def test_raises_exception_when_existing_objs(self):
        StandardFactory.create_batch(2, foo='foo')
        with self.assertRaises(sqlalchemy.orm.exc.MultipleResultsFound):
            WithGetOrCreateFieldFactory(foo='foo')

    def test_multicall(self):
        objs = MultifieldModelFactory.create_batch(
            6,
            slug=factory.Iterator(['main', 'alt']),
        )
        self.assertEqual(6, len(objs))
        self.assertEqual(2, len(set(objs)))
        self.assertEqual(
            list(
                obj.slug for obj in models.session.query(
                    models.MultiFieldModel.slug
                ).order_by(models.MultiFieldModel.slug)
            ),
            ["alt", "main"],
        )


class MultipleGetOrCreateFieldsTest(TransactionTestCase):
    def test_one_defined(self):
        obj1 = WithMultipleGetOrCreateFieldsFactory()
        obj2 = WithMultipleGetOrCreateFieldsFactory(slug=obj1.slug)
        self.assertEqual(obj1, obj2)

    def test_both_defined(self):
        obj1 = WithMultipleGetOrCreateFieldsFactory()
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            WithMultipleGetOrCreateFieldsFactory(slug=obj1.slug, text="alt")

    def test_unique_field_not_in_get_or_create(self):
        WithMultipleGetOrCreateFieldsFactory(title='Title')
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            WithMultipleGetOrCreateFieldsFactory(title='Title')


class SQLAlchemySessionPersistenceTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()
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


class SQLAlchemyNonIntegerPkTestCase(TransactionTestCase):
    def tearDown(self):
        super().tearDown()
        NonIntegerPkFactory.reset_sequence()

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


class SQLAlchemyNoSessionTestCase(TransactionTestCase):

    def test_create_raises_exception_when_no_session_was_set(self):
        with self.assertRaises(RuntimeError):
            NoSessionFactory.create()

    def test_build_does_not_raises_exception_when_no_session_was_set(self):
        NoSessionFactory.reset_sequence()  # Make sure we start at test ID 0
        inst0 = NoSessionFactory.build()
        inst1 = NoSessionFactory.build()
        self.assertEqual(inst0.id, 0)
        self.assertEqual(inst1.id, 1)


class SQLAlchemySessionFactoryTestCase(TransactionTestCase):
    def test_create_get_session_from_sqlalchemy_session_factory(self):
        class SessionGetterFactory(SQLAlchemyModelFactory):
            class Meta:
                model = models.StandardModel
                sqlalchemy_session_factory = lambda: models.session

            id = factory.Sequence(lambda n: n)

        SessionGetterFactory.create()
        self.assertEqual(SessionGetterFactory._meta.sqlalchemy_session, models.session)
        # Reuse the session obtained from sqlalchemy_session_factory.
        SessionGetterFactory.create()

    def test_create_raise_exception_sqlalchemy_session_factory_not_callable(self):
        message = "^Provide either a sqlalchemy_session or a sqlalchemy_session_factory, not both$"
        with self.assertRaisesRegex(RuntimeError, message):
            class SessionAndGetterFactory(SQLAlchemyModelFactory):
                class Meta:
                    model = models.StandardModel
                    sqlalchemy_session = models.session
                    sqlalchemy_session_factory = lambda: models.session

                id = factory.Sequence(lambda n: n)


class NameConflictTests(TransactionTestCase):
    """Regression test for `TypeError: _save() got multiple values for argument 'session'`

    See #775.
    """
    def test_no_name_conflict_on_save(self):
        class SpecialFieldWithSaveFactory(SQLAlchemyModelFactory):
            class Meta:
                model = models.SpecialFieldModel
                sqlalchemy_session = models.session

            id = factory.Sequence(lambda n: n)
            session = ''

        saved_child = SpecialFieldWithSaveFactory()
        self.assertEqual(saved_child.session, "")

    def test_no_name_conflict_on_get_or_create(self):
        class SpecialFieldWithGetOrCreateFactory(SQLAlchemyModelFactory):
            class Meta:
                model = models.SpecialFieldModel
                sqlalchemy_get_or_create = ('session',)
                sqlalchemy_session = models.session

            id = factory.Sequence(lambda n: n)
            session = ''

        get_or_created_child = SpecialFieldWithGetOrCreateFactory()
        self.assertEqual(get_or_created_child.session, "")
