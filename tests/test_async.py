# Copyright: See the LICENSE file.

import asyncio
import unittest

import factory
from factory import enums


class TestModel:
    def __init__(self, one=None, two=None, three=None):
        self.one = one
        self.two = two
        self.three = three
        self.id = None


class TestModel2:
    def __init__(self, related=None, value=None):
        self.related = related
        self.value = value
        self.id = None


class TestModel3:
    def __init__(self, nested=None, name=None):
        self.nested = nested
        self.name = name
        self.id = None


class AsyncFactoryTestCase(unittest.TestCase):
    """Test async factory creation."""

    def test_async_create_strategy_constant(self):
        """Test that ASYNC_CREATE_STRATEGY is defined."""
        self.assertEqual('async_create', enums.ASYNC_CREATE_STRATEGY)
        self.assertEqual('async_create', factory.ASYNC_CREATE_STRATEGY)

    def test_async_create_basic(self):
        """Test basic async factory creation."""
        class TestModelFactory(factory.Factory):
            class Meta:
                model = TestModel

            one = 'one'
            two = 'two'

        async def run_test():
            obj = await TestModelFactory.async_create()
            self.assertEqual('one', obj.one)
            self.assertEqual('two', obj.two)

        asyncio.run(run_test())

    def test_async_create_with_params(self):
        """Test async factory creation with parameters."""
        class TestModelFactory(factory.Factory):
            class Meta:
                model = TestModel

            one = 'one'
            two = 'two'

        async def run_test():
            obj = await TestModelFactory.async_create(one='custom')
            self.assertEqual('custom', obj.one)
            self.assertEqual('two', obj.two)

        asyncio.run(run_test())

    def test_async_strategy_with_await(self):
        """Test that ASYNC_CREATE_STRATEGY allows await MyFactory() syntax."""
        class TestModelFactory(factory.Factory):
            class Meta:
                model = TestModel
                strategy = enums.ASYNC_CREATE_STRATEGY

            one = 'one'
            two = 'two'

        async def run_test():
            # This should work with await
            obj = await TestModelFactory()
            self.assertEqual('one', obj.one)
            self.assertEqual('two', obj.two)

        asyncio.run(run_test())

    def test_async_strategy_with_params(self):
        """Test ASYNC_CREATE_STRATEGY with parameters."""
        class TestModelFactory(factory.Factory):
            class Meta:
                model = TestModel
                strategy = enums.ASYNC_CREATE_STRATEGY

            one = 'one'
            two = 'two'

        async def run_test():
            obj = await TestModelFactory(one='custom', three='three')
            self.assertEqual('custom', obj.one)
            self.assertEqual('two', obj.two)
            self.assertEqual('three', obj.three)

        asyncio.run(run_test())

    def test_async_with_sequence(self):
        """Test async factory with Sequence."""
        class TestModelFactory(factory.Factory):
            class Meta:
                model = TestModel
                strategy = enums.ASYNC_CREATE_STRATEGY

            one = factory.Sequence(lambda n: f'item-{n}')

        async def run_test():
            obj1 = await TestModelFactory()
            obj2 = await TestModelFactory()
            self.assertEqual('item-0', obj1.one)
            self.assertEqual('item-1', obj2.one)

        asyncio.run(run_test())

    def test_async_with_lazy_attribute(self):
        """Test async factory with LazyAttribute."""
        class TestModelFactory(factory.Factory):
            class Meta:
                model = TestModel
                strategy = enums.ASYNC_CREATE_STRATEGY

            one = 'base'
            two = factory.LazyAttribute(lambda obj: f'{obj.one}-extended')

        async def run_test():
            obj = await TestModelFactory()
            self.assertEqual('base', obj.one)
            self.assertEqual('base-extended', obj.two)

        asyncio.run(run_test())


class AsyncSubFactoryTestCase(unittest.TestCase):
    """Test async factory with SubFactory."""

    def test_async_with_subfactory(self):
        """Test that SubFactory works in async context."""
        class TestModelFactory(factory.Factory):
            class Meta:
                model = TestModel

            one = 'one'

        class TestModel2Factory(factory.Factory):
            class Meta:
                model = TestModel2
                strategy = enums.ASYNC_CREATE_STRATEGY

            related = factory.SubFactory(TestModelFactory)
            value = 'value'

        async def run_test():
            obj = await TestModel2Factory()
            self.assertEqual('value', obj.value)
            self.assertIsNotNone(obj.related)
            self.assertEqual('one', obj.related.one)

        asyncio.run(run_test())

    def test_async_with_subfactory_params(self):
        """Test SubFactory with parameters in async context."""
        class TestModelFactory(factory.Factory):
            class Meta:
                model = TestModel

            one = 'one'
            two = 'two'

        class TestModel2Factory(factory.Factory):
            class Meta:
                model = TestModel2
                strategy = enums.ASYNC_CREATE_STRATEGY

            related = factory.SubFactory(TestModelFactory, one='custom')
            value = 'value'

        async def run_test():
            obj = await TestModel2Factory()
            self.assertEqual('value', obj.value)
            self.assertEqual('custom', obj.related.one)
            self.assertEqual('two', obj.related.two)

        asyncio.run(run_test())

    def test_async_with_nested_subfactory(self):
        """Test nested SubFactory in async context."""
        class TestModelFactory(factory.Factory):
            class Meta:
                model = TestModel

            one = 'one'

        class TestModel2Factory(factory.Factory):
            class Meta:
                model = TestModel2

            related = factory.SubFactory(TestModelFactory)
            value = 'value'

        class TestModel3Factory(factory.Factory):
            class Meta:
                model = TestModel3
                strategy = enums.ASYNC_CREATE_STRATEGY

            nested = factory.SubFactory(TestModel2Factory)
            name = 'name'

        async def run_test():
            obj = await TestModel3Factory()
            self.assertEqual('name', obj.name)
            self.assertIsNotNone(obj.nested)
            self.assertEqual('value', obj.nested.value)
            self.assertIsNotNone(obj.nested.related)
            self.assertEqual('one', obj.nested.related.one)

        asyncio.run(run_test())

    def test_async_with_subfactory_override(self):
        """Test SubFactory override in async context."""
        class TestModelFactory(factory.Factory):
            class Meta:
                model = TestModel

            one = 'one'
            two = 'two'

        class TestModel2Factory(factory.Factory):
            class Meta:
                model = TestModel2
                strategy = enums.ASYNC_CREATE_STRATEGY

            related = factory.SubFactory(TestModelFactory)
            value = 'value'

        async def run_test():
            obj = await TestModel2Factory(related__one='override')
            self.assertEqual('override', obj.related.one)
            self.assertEqual('two', obj.related.two)

        asyncio.run(run_test())


class AsyncBatchTestCase(unittest.TestCase):
    """Test async batch factory creation."""

    def test_async_create_batch(self):
        """Test async_create_batch creates multiple instances concurrently."""
        class TestModelFactory(factory.Factory):
            class Meta:
                model = TestModel

            one = factory.Sequence(lambda n: f'item-{n}')
            two = 'two'

        async def run_test():
            # Create 5 instances in batch
            objs = await TestModelFactory.async_create_batch(5)

            self.assertEqual(5, len(objs))
            # Each should have unique sequence
            for i, obj in enumerate(objs):
                self.assertEqual(f'item-{i}', obj.one)
                self.assertEqual('two', obj.two)

        asyncio.run(run_test())

    def test_async_build_batch(self):
        """Test async_build_batch creates multiple instances concurrently."""
        class TestModelFactory(factory.Factory):
            class Meta:
                model = TestModel

            one = factory.Sequence(lambda n: f'build-{n}')

        async def run_test():
            # Build 3 instances in batch
            objs = await TestModelFactory.async_build_batch(3)

            self.assertEqual(3, len(objs))
            for i, obj in enumerate(objs):
                self.assertEqual(f'build-{i}', obj.one)

        asyncio.run(run_test())

    def test_async_create_batch_with_params(self):
        """Test async_create_batch with parameters."""
        class TestModelFactory(factory.Factory):
            class Meta:
                model = TestModel

            one = 'default'
            two = factory.Sequence(lambda n: n)

        async def run_test():
            objs = await TestModelFactory.async_create_batch(4, one='custom')

            self.assertEqual(4, len(objs))
            for obj in objs:
                self.assertEqual('custom', obj.one)

        asyncio.run(run_test())

    def test_async_batch_with_subfactory(self):
        """Test async batch with SubFactory."""
        class TestModelFactory(factory.Factory):
            class Meta:
                model = TestModel

            one = factory.Sequence(lambda n: f'user-{n}')

        class TestModel2Factory(factory.Factory):
            class Meta:
                model = TestModel2

            related = factory.SubFactory(TestModelFactory)
            value = factory.Sequence(lambda n: f'value-{n}')

        async def run_test():
            objs = await TestModel2Factory.async_create_batch(3)

            self.assertEqual(3, len(objs))
            for i, obj in enumerate(objs):
                self.assertEqual(f'value-{i}', obj.value)
                self.assertIsNotNone(obj.related)
                # SubFactory should also have unique sequences
                self.assertTrue(obj.related.one.startswith('user-'))

        asyncio.run(run_test())


if __name__ == '__main__':
    unittest.main()

