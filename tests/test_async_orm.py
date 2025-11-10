# Copyright: See the LICENSE file.

"""Test async support for ORM factories."""

import asyncio
import unittest

import factory


class TestModel:
    """Simple test model."""
    def __init__(self, name=None, value=None):
        self.name = name
        self.value = value
        self.saved = False

    def save(self):
        """Simulate save operation."""
        self.saved = True

    def __repr__(self):
        return f"TestModel(name={self.name}, value={self.value}, saved={self.saved})"


class MogoLikeFactory(factory.mogo.MogoFactory):
    """Test factory that mimics MogoFactory behavior."""
    class Meta:
        model = TestModel

    name = factory.Sequence(lambda n: f'mogo-{n}')
    value = 'test'


class FakeDocument:
    """Fake document class."""
    _is_document = True

    def __init__(self, name=None, value=None):
        self.name = name
        self.value = value
        self.saved = False

    def save(self):
        self.saved = True

    def __repr__(self):
        return f"FakeDocument(name={self.name}, value={self.value}, saved={self.saved})"


class MongoEngineLikeFactory(factory.mongoengine.MongoEngineFactory):
    """Test factory that mimics MongoEngineFactory behavior."""

    class Meta:
        model = FakeDocument

    name = factory.Sequence(lambda n: f'mongoengine-{n}')
    value = 'test'


class AsyncORMTestCase(unittest.TestCase):
    """Test async support for ORM factories."""

    def test_mogo_async_create(self):
        """Test MogoFactory async_create."""
        async def run_test():
            obj = await MogoLikeFactory.async_create()
            self.assertEqual('mogo-0', obj.name)
            self.assertEqual('test', obj.value)
            self.assertTrue(obj.saved)

        asyncio.run(run_test())

    def test_mogo_async_create_batch(self):
        """Test MogoFactory async_create_batch."""
        async def run_test():
            objs = await MogoLikeFactory.async_create_batch(3)
            self.assertEqual(3, len(objs))
            for i, obj in enumerate(objs):
                self.assertEqual(f'mogo-{i + 1}', obj.name)
                self.assertTrue(obj.saved)

        asyncio.run(run_test())

    def test_mongoengine_async_create(self):
        """Test MongoEngineFactory async_create."""
        async def run_test():
            obj = await MongoEngineLikeFactory.async_create()
            self.assertEqual('mongoengine-0', obj.name)
            self.assertEqual('test', obj.value)
            self.assertTrue(obj.saved)

        asyncio.run(run_test())

    def test_mongoengine_async_create_batch(self):
        """Test MongoEngineFactory async_create_batch."""
        async def run_test():
            objs = await MongoEngineLikeFactory.async_create_batch(3)
            self.assertEqual(3, len(objs))
            for i, obj in enumerate(objs):
                self.assertEqual(f'mongoengine-{i + 1}', obj.name)
                self.assertTrue(obj.saved)

        asyncio.run(run_test())

    def test_custom_async_create_override(self):
        """Test that users can override _async_create for true async ORM."""
        
        class AsyncModel:
            def __init__(self, name=None):
                self.name = name
                self.async_saved = False
            
            async def async_save(self):
                """Simulate async save."""
                await asyncio.sleep(0.01)
                self.async_saved = True
        
        class CustomAsyncFactory(factory.mogo.MogoFactory):
            class Meta:
                model = AsyncModel
            
            name = 'custom'
            
            @classmethod
            async def _async_create(cls, model_class, *args, **kwargs):
                """Custom async create using async ORM."""
                instance = model_class(*args, **kwargs)
                await instance.async_save()
                return instance
        
        async def run_test():
            obj = await CustomAsyncFactory.async_create()
            self.assertEqual('custom', obj.name)
            self.assertTrue(obj.async_saved)
        
        asyncio.run(run_test())


class SQLAlchemyLikeTestCase(unittest.TestCase):
    """Test SQLAlchemyModelFactory async support."""

    def test_sqlalchemy_async_create_with_async_session(self):
        """Test that SQLAlchemyModelFactory._async_create works with AsyncSession."""

        class FakeAsyncSession:
            def __init__(self):
                self.added = []
                self.flushed = False
                self.committed = False

            def add(self, obj):
                self.added.append(obj)

            async def flush(self):
                self.flushed = True

            async def commit(self):
                self.committed = True

        class FakeModel:
            def __init__(self, name=None):
                self.name = name

        class FakeSQLAlchemyFactory(factory.alchemy.SQLAlchemyModelFactory):
            class Meta:
                model = FakeModel
                sqlalchemy_session = FakeAsyncSession()
                sqlalchemy_session_persistence = factory.alchemy.SESSION_PERSISTENCE_FLUSH

            name = 'test'

        async def run_test():
            obj = await FakeSQLAlchemyFactory.async_create()
            self.assertEqual('test', obj.name)
            # Verify async session was used
            session = FakeSQLAlchemyFactory._meta.sqlalchemy_session
            self.assertEqual(1, len(session.added))
            self.assertTrue(session.flushed)

        asyncio.run(run_test())


class DjangoLikeTestCase(unittest.TestCase):
    """Test DjangoModelFactory async support."""

    def test_django_async_create_with_async_orm(self):
        """Test that DjangoModelFactory._async_create works with Django async ORM."""

        class FakeAsyncManager:
            def __init__(self):
                self.created = []

            async def acreate(self, *args, **kwargs):
                obj = FakeModel(*args, **kwargs)
                self.created.append(obj)
                return obj

            def using(self, db):
                return self

        class FakeModel:
            objects = FakeAsyncManager()
            _default_manager = objects

            def __init__(self, name=None):
                self.name = name

        class FakeDjangoFactory(factory.django.DjangoModelFactory):
            class Meta:
                model = FakeModel

            name = 'test'

        async def run_test():
            obj = await FakeDjangoFactory.async_create()
            self.assertEqual('test', obj.name)
            # Verify manager.acreate was called
            self.assertEqual(1, len(FakeModel.objects.created))

        asyncio.run(run_test())


if __name__ == '__main__':
    unittest.main()

