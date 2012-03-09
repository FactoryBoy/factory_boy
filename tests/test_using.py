# -*- coding: utf-8 -*-
# Copyright (c) 2011 Raphaël Barrois
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
"""Tests using factory."""

import unittest

import factory



class TestObject(object):
    def __init__(self, one=None, two=None, three=None, four=None, five=None):
        self.one = one
        self.two = two
        self.three = three
        self.four = four
        self.five = five

class FakeDjangoModel(object):
    class FakeDjangoManager(object):
        def create(self, **kwargs):
            fake_model = FakeDjangoModel(**kwargs)
            fake_model.id = 1
            return fake_model

    objects = FakeDjangoManager()

    def __init__(self, **kwargs):
        for name, value in kwargs.iteritems():
            setattr(self, name, value)
            self.id = None

class TestModel(FakeDjangoModel):
    pass


class SimpleBuildTestCase(unittest.TestCase):
    """Tests the minimalist 'factory.build/create' functions."""

    def test_build(self):
        obj = factory.build(TestObject, two=2)
        self.assertEqual(obj.one, None)
        self.assertEqual(obj.two, 2)
        self.assertEqual(obj.three, None)
        self.assertEqual(obj.four, None)

    def test_complex(self):
        obj = factory.build(TestObject, two=2, three=factory.LazyAttribute(lambda o: o.two + 1))
        self.assertEqual(obj.one, None)
        self.assertEqual(obj.two, 2)
        self.assertEqual(obj.three, 3)
        self.assertEqual(obj.four, None)

    def test_build_batch(self):
        objs = factory.build_batch(TestObject, 4, two=2,
            three=factory.LazyAttribute(lambda o: o.two + 1))

        self.assertEqual(4, len(objs))
        self.assertEqual(4, len(set(objs)))

        for obj in objs:
            self.assertEqual(obj.one, None)
            self.assertEqual(obj.two, 2)
            self.assertEqual(obj.three, 3)
            self.assertEqual(obj.four, None)

    def test_create(self):
        obj = factory.create(FakeDjangoModel, foo='bar')
        self.assertEqual(obj.id, 1)
        self.assertEqual(obj.foo, 'bar')

    def test_create_batch(self):
        objs = factory.create_batch(FakeDjangoModel, 4, foo='bar')

        self.assertEqual(4, len(objs))
        self.assertEqual(4, len(set(objs)))

        for obj in objs:
            self.assertEqual(obj.id, 1)
            self.assertEqual(obj.foo, 'bar')

    def test_stub(self):
        obj = factory.stub(TestObject, three=3)
        self.assertEqual(obj.three, 3)
        self.assertFalse(hasattr(obj, 'two'))

    def test_stub_batch(self):
        objs = factory.stub_batch(FakeDjangoModel, 4, foo='bar')

        self.assertEqual(4, len(objs))
        self.assertEqual(4, len(set(objs)))

        for obj in objs:
            self.assertFalse(hasattr(obj, 'id'))
            self.assertEqual(obj.foo, 'bar')

    def test_generate_build(self):
        obj = factory.generate(FakeDjangoModel, factory.BUILD_STRATEGY, foo='bar')
        self.assertEqual(obj.id, None)
        self.assertEqual(obj.foo, 'bar')

    def test_generate_create(self):
        obj = factory.generate(FakeDjangoModel, factory.CREATE_STRATEGY, foo='bar')
        self.assertEqual(obj.id, 1)
        self.assertEqual(obj.foo, 'bar')

    def test_generate_stub(self):
        obj = factory.generate(FakeDjangoModel, factory.STUB_STRATEGY, foo='bar')
        self.assertFalse(hasattr(obj, 'id'))
        self.assertEqual(obj.foo, 'bar')

    def test_generate_batch_build(self):
        objs = factory.generate_batch(FakeDjangoModel, factory.BUILD_STRATEGY, 20, foo='bar')

        self.assertEqual(20, len(objs))
        self.assertEqual(20, len(set(objs)))

        for obj in objs:
            self.assertEqual(obj.id, None)
            self.assertEqual(obj.foo, 'bar')

    def test_generate_batch_create(self):
        objs = factory.generate_batch(FakeDjangoModel, factory.CREATE_STRATEGY, 20, foo='bar')

        self.assertEqual(20, len(objs))
        self.assertEqual(20, len(set(objs)))

        for obj in objs:
            self.assertEqual(obj.id, 1)
            self.assertEqual(obj.foo, 'bar')

    def test_generate_batch_stub(self):
        objs = factory.generate_batch(FakeDjangoModel, factory.STUB_STRATEGY, 20, foo='bar')

        self.assertEqual(20, len(objs))
        self.assertEqual(20, len(set(objs)))

        for obj in objs:
            self.assertFalse(hasattr(obj, 'id'))
            self.assertEqual(obj.foo, 'bar')

    def test_simple_generate_build(self):
        obj = factory.simple_generate(FakeDjangoModel, False, foo='bar')
        self.assertEqual(obj.id, None)
        self.assertEqual(obj.foo, 'bar')

    def test_simple_generate_create(self):
        obj = factory.simple_generate(FakeDjangoModel, True, foo='bar')
        self.assertEqual(obj.id, 1)
        self.assertEqual(obj.foo, 'bar')

    def test_simple_generate_batch_build(self):
        objs = factory.simple_generate_batch(FakeDjangoModel, False, 20, foo='bar')

        self.assertEqual(20, len(objs))
        self.assertEqual(20, len(set(objs)))

        for obj in objs:
            self.assertEqual(obj.id, None)
            self.assertEqual(obj.foo, 'bar')

    def test_simple_generate_batch_create(self):
        objs = factory.simple_generate_batch(FakeDjangoModel, True, 20, foo='bar')

        self.assertEqual(20, len(objs))
        self.assertEqual(20, len(set(objs)))

        for obj in objs:
            self.assertEqual(obj.id, 1)
            self.assertEqual(obj.foo, 'bar')

    def test_make_factory(self):
        fact = factory.make_factory(TestObject, two=2, three=factory.LazyAttribute(lambda o: o.two + 1))

        obj = fact.build()
        self.assertEqual(obj.one, None)
        self.assertEqual(obj.two, 2)
        self.assertEqual(obj.three, 3)
        self.assertEqual(obj.four, None)

        obj = fact.build(two=4)
        self.assertEqual(obj.one, None)
        self.assertEqual(obj.two, 4)
        self.assertEqual(obj.three, 5)
        self.assertEqual(obj.four, None)


class FactoryTestCase(unittest.TestCase):
    def testAttribute(self):
        class TestObjectFactory(factory.Factory):
            one = 'one'

        test_object = TestObjectFactory.build()
        self.assertEqual(test_object.one, 'one')

    def testSequence(self):
        class TestObjectFactory(factory.Factory):
            one = factory.Sequence(lambda n: 'one' + n)
            two = factory.Sequence(lambda n: 'two' + n)

        test_object0 = TestObjectFactory.build()
        self.assertEqual(test_object0.one, 'one0')
        self.assertEqual(test_object0.two, 'two0')

        test_object1 = TestObjectFactory.build()
        self.assertEqual(test_object1.one, 'one1')
        self.assertEqual(test_object1.two, 'two1')

    def testSequenceCustomBegin(self):
        class TestObjectFactory(factory.Factory):
            @classmethod
            def _setup_next_sequence(cls):
                return 42

            one = factory.Sequence(lambda n: 'one' + n)
            two = factory.Sequence(lambda n: 'two' + n)

        test_object0 = TestObjectFactory.build()
        self.assertEqual('one42', test_object0.one)
        self.assertEqual('two42', test_object0.two)

        test_object1 = TestObjectFactory.build()
        self.assertEqual('one43', test_object1.one)
        self.assertEqual('two43', test_object1.two)

    def test_sequence_batch(self):
        class TestObjectFactory(factory.Factory):
            one = factory.Sequence(lambda n: 'one' + n)
            two = factory.Sequence(lambda n: 'two' + n)

        objs = TestObjectFactory.build_batch(20)

        self.assertEqual(20, len(objs))
        self.assertEqual(20, len(set(objs)))
        for i, obj in enumerate(objs):
            self.assertEqual('one%d' % i, obj.one)
            self.assertEqual('two%d' % i, obj.two)

    def testLazyAttribute(self):
        class TestObjectFactory(factory.Factory):
            one = factory.LazyAttribute(lambda a: 'abc' )
            two = factory.LazyAttribute(lambda a: a.one + ' xyz')

        test_object = TestObjectFactory.build()
        self.assertEqual(test_object.one, 'abc')
        self.assertEqual(test_object.two, 'abc xyz')

    def testLazyAttributeSequence(self):
        class TestObjectFactory(factory.Factory):
            one = factory.LazyAttributeSequence(lambda a, n: 'abc' + n)
            two = factory.LazyAttributeSequence(lambda a, n: a.one + ' xyz' + n)

        test_object0 = TestObjectFactory.build()
        self.assertEqual(test_object0.one, 'abc0')
        self.assertEqual(test_object0.two, 'abc0 xyz0')

        test_object1 = TestObjectFactory.build()
        self.assertEqual(test_object1.one, 'abc1')
        self.assertEqual(test_object1.two, 'abc1 xyz1')

    def testLazyAttributeDecorator(self):
        class TestObjectFactory(factory.Factory):
            @factory.lazy_attribute
            def one(a):
                return 'one'

        test_object = TestObjectFactory.build()
        self.assertEqual(test_object.one, 'one')

    def testSelfAttribute(self):
        class TmpObj(object):
            n = 3

        class TestObjectFactory(factory.Factory):
            one = 'xx'
            two = factory.SelfAttribute('one')
            three = TmpObj()
            four = factory.SelfAttribute('three.n')
            five = factory.SelfAttribute('three.nnn', 5)

        test_object = TestObjectFactory.build(one=1)
        self.assertEqual(1, test_object.two)
        self.assertEqual(3, test_object.three.n)
        self.assertEqual(3, test_object.four)
        self.assertEqual(5, test_object.five)

    def testSequenceDecorator(self):
        class TestObjectFactory(factory.Factory):
            @factory.sequence
            def one(n):
                return 'one' + n

        test_object = TestObjectFactory.build()
        self.assertEqual(test_object.one, 'one0')

    def testLazyAttributeSequenceDecorator(self):
        class TestObjectFactory(factory.Factory):
            @factory.lazy_attribute_sequence
            def one(a, n):
                return 'one' + n
            @factory.lazy_attribute_sequence
            def two(a, n):
                return a.one + ' two' + n

        test_object = TestObjectFactory.build()
        self.assertEqual(test_object.one, 'one0')
        self.assertEqual(test_object.two, 'one0 two0')

    def testBuildWithParameters(self):
        class TestObjectFactory(factory.Factory):
            one = factory.Sequence(lambda n: 'one' + n)
            two = factory.Sequence(lambda n: 'two' + n)

        test_object0 = TestObjectFactory.build(three='three')
        self.assertEqual(test_object0.one, 'one0')
        self.assertEqual(test_object0.two, 'two0')
        self.assertEqual(test_object0.three, 'three')

        test_object1 = TestObjectFactory.build(one='other')
        self.assertEqual(test_object1.one, 'other')
        self.assertEqual(test_object1.two, 'two1')

    def testCreate(self):
        class TestModelFactory(factory.Factory):
            one = 'one'

        test_model = TestModelFactory.create()
        self.assertEqual(test_model.one, 'one')
        self.assertTrue(test_model.id)

    def test_create_batch(self):
        class TestModelFactory(factory.Factory):
            one = 'one'

        objs = TestModelFactory.create_batch(20, two=factory.Sequence(int))

        self.assertEqual(20, len(objs))
        self.assertEqual(20, len(set(objs)))

        for i, obj in enumerate(objs):
            self.assertEqual('one', obj.one)
            self.assertEqual(i, obj.two)
            self.assertTrue(obj.id)

    def test_generate_build(self):
        class TestModelFactory(factory.Factory):
            one = 'one'

        test_model = TestModelFactory.generate(factory.BUILD_STRATEGY)
        self.assertEqual(test_model.one, 'one')
        self.assertFalse(test_model.id)

    def test_generate_create(self):
        class TestModelFactory(factory.Factory):
            one = 'one'

        test_model = TestModelFactory.generate(factory.CREATE_STRATEGY)
        self.assertEqual(test_model.one, 'one')
        self.assertTrue(test_model.id)

    def test_generate_stub(self):
        class TestModelFactory(factory.Factory):
            one = 'one'

        test_model = TestModelFactory.generate(factory.STUB_STRATEGY)
        self.assertEqual(test_model.one, 'one')
        self.assertFalse(hasattr(test_model, 'id'))

    def test_generate_batch_build(self):
        class TestModelFactory(factory.Factory):
            one = 'one'

        objs = TestModelFactory.generate_batch(factory.BUILD_STRATEGY, 20, two='two')

        self.assertEqual(20, len(objs))
        self.assertEqual(20, len(set(objs)))

        for i, obj in enumerate(objs):
            self.assertEqual('one', obj.one)
            self.assertEqual('two', obj.two)
            self.assertFalse(obj.id)

    def test_generate_batch_create(self):
        class TestModelFactory(factory.Factory):
            one = 'one'

        objs = TestModelFactory.generate_batch(factory.CREATE_STRATEGY, 20, two='two')

        self.assertEqual(20, len(objs))
        self.assertEqual(20, len(set(objs)))

        for i, obj in enumerate(objs):
            self.assertEqual('one', obj.one)
            self.assertEqual('two', obj.two)
            self.assertTrue(obj.id)

    def test_generate_batch_stub(self):
        class TestModelFactory(factory.Factory):
            one = 'one'

        objs = TestModelFactory.generate_batch(factory.STUB_STRATEGY, 20, two='two')

        self.assertEqual(20, len(objs))
        self.assertEqual(20, len(set(objs)))

        for i, obj in enumerate(objs):
            self.assertEqual('one', obj.one)
            self.assertEqual('two', obj.two)
            self.assertFalse(hasattr(obj, 'id'))

    def test_simple_generate_build(self):
        class TestModelFactory(factory.Factory):
            one = 'one'

        test_model = TestModelFactory.simple_generate(False)
        self.assertEqual(test_model.one, 'one')
        self.assertFalse(test_model.id)

    def test_simple_generate_create(self):
        class TestModelFactory(factory.Factory):
            one = 'one'

        test_model = TestModelFactory.simple_generate(True)
        self.assertEqual(test_model.one, 'one')
        self.assertTrue(test_model.id)

    def test_simple_generate_batch_build(self):
        class TestModelFactory(factory.Factory):
            one = 'one'

        objs = TestModelFactory.simple_generate_batch(False, 20, two='two')

        self.assertEqual(20, len(objs))
        self.assertEqual(20, len(set(objs)))

        for i, obj in enumerate(objs):
            self.assertEqual('one', obj.one)
            self.assertEqual('two', obj.two)
            self.assertFalse(obj.id)

    def test_simple_generate_batch_create(self):
        class TestModelFactory(factory.Factory):
            one = 'one'

        objs = TestModelFactory.simple_generate_batch(True, 20, two='two')

        self.assertEqual(20, len(objs))
        self.assertEqual(20, len(set(objs)))

        for i, obj in enumerate(objs):
            self.assertEqual('one', obj.one)
            self.assertEqual('two', obj.two)
            self.assertTrue(obj.id)

    def test_stub_batch(self):
        class TestObjectFactory(factory.Factory):
            one = 'one'
            two = factory.LazyAttribute(lambda a: a.one + ' two')
            three = factory.Sequence(lambda n: int(n))

        objs = TestObjectFactory.stub_batch(20,
            one=factory.Sequence(lambda n: n))

        self.assertEqual(20, len(objs))
        self.assertEqual(20, len(set(objs)))

        for i, obj in enumerate(objs):
            self.assertEqual(str(i), obj.one)
            self.assertEqual('%d two' % i, obj.two)
            self.assertEqual(i, obj.three)

    def testInheritance(self):
        class TestObjectFactory(factory.Factory):
            one = 'one'
            two = factory.LazyAttribute(lambda a: a.one + ' two')

        class TestObjectFactory2(TestObjectFactory):
            FACTORY_FOR = TestObject

            three = 'three'
            four = factory.LazyAttribute(lambda a: a.three + ' four')

        test_object = TestObjectFactory2.build()
        self.assertEqual(test_object.one, 'one')
        self.assertEqual(test_object.two, 'one two')
        self.assertEqual(test_object.three, 'three')
        self.assertEqual(test_object.four, 'three four')

        test_object_alt = TestObjectFactory.build()
        self.assertEqual(None, test_object_alt.three)

    def testInheritanceWithInheritedClass(self):
        class TestObjectFactory(factory.Factory):
            one = 'one'
            two = factory.LazyAttribute(lambda a: a.one + ' two')

        class TestFactory(TestObjectFactory):
            three = 'three'
            four = factory.LazyAttribute(lambda a: a.three + ' four')

        test_object = TestFactory.build()
        self.assertEqual(test_object.one, 'one')
        self.assertEqual(test_object.two, 'one two')
        self.assertEqual(test_object.three, 'three')
        self.assertEqual(test_object.four, 'three four')

    def testDualInheritance(self):
        class TestObjectFactory(factory.Factory):
            one = 'one'

        class TestOtherFactory(factory.Factory):
            FACTORY_FOR = TestObject
            two = 'two'
            four = 'four'

        class TestFactory(TestObjectFactory, TestOtherFactory):
            three = 'three'

        obj = TestFactory.build(two=2)
        self.assertEqual('one', obj.one)
        self.assertEqual(2, obj.two)
        self.assertEqual('three', obj.three)
        self.assertEqual('four', obj.four)

    def testSetCreationFunction(self):
        def creation_function(class_to_create, **kwargs):
            return "This doesn't even return an instance of {0}".format(class_to_create.__name__)

        class TestModelFactory(factory.Factory):
            pass

        TestModelFactory.set_creation_function(creation_function)

        test_object = TestModelFactory.create()
        self.assertEqual(test_object, "This doesn't even return an instance of TestModel")

    def testClassMethodAccessible(self):
        class TestObjectFactory(factory.Factory):
            @classmethod
            def alt_create(cls, **kwargs):
                return kwargs

        self.assertEqual(TestObjectFactory.alt_create(foo=1), {"foo": 1})

    def testStaticMethodAccessible(self):
        class TestObjectFactory(factory.Factory):
            @staticmethod
            def alt_create(**kwargs):
                return kwargs

        self.assertEqual(TestObjectFactory.alt_create(foo=1), {"foo": 1})


class SubFactoryTestCase(unittest.TestCase):
    def testSubFactory(self):
        class TestModel2(FakeDjangoModel):
            pass

        class TestModelFactory(factory.Factory):
            FACTORY_FOR = TestModel
            one = 3

        class TestModel2Factory(factory.Factory):
            FACTORY_FOR = TestModel2
            two = factory.SubFactory(TestModelFactory, one=1)

        test_model = TestModel2Factory(two__one=4)
        self.assertEqual(4, test_model.two.one)
        self.assertEqual(1, test_model.id)
        self.assertEqual(1, test_model.two.id)

    def testSubFactoryWithLazyFields(self):
        class TestModel2(FakeDjangoModel):
            pass

        class TestModelFactory(factory.Factory):
            FACTORY_FOR = TestModel

        class TestModel2Factory(factory.Factory):
            FACTORY_FOR = TestModel2
            two = factory.SubFactory(TestModelFactory,
                                          one=factory.Sequence(lambda n: 'x%sx' % n),
                                          two=factory.LazyAttribute(
                                              lambda o: '%s%s' % (o.one, o.one)))

        test_model = TestModel2Factory(one=42)
        self.assertEqual('x0x', test_model.two.one)
        self.assertEqual('x0xx0x', test_model.two.two)

    def testSubFactoryOverriding(self):
        class TestObject(object):
            def __init__(self, **kwargs):
                for k, v in kwargs.iteritems():
                    setattr(self, k, v)

        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

        class WrappingTestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            wrapped = factory.SubFactory(TestObjectFactory, two=2, four=4)
            wrapped__two = 4
            wrapped__three = 3

        wrapping = WrappingTestObjectFactory.build()
        self.assertEqual(wrapping.wrapped.two, 4)
        self.assertEqual(wrapping.wrapped.three, 3)
        self.assertEqual(wrapping.wrapped.four, 4)

    def testNestedSubFactory(self):
        """Test nested sub-factories."""

        class TestObject(object):
            def __init__(self, **kwargs):
                for k, v in kwargs.iteritems():
                    setattr(self, k, v)

        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

        class WrappingTestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            wrapped = factory.SubFactory(TestObjectFactory)
            wrapped_bis = factory.SubFactory(TestObjectFactory, one=1)

        class OuterWrappingTestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            wrap = factory.SubFactory(WrappingTestObjectFactory, wrapped__two=2)

        outer = OuterWrappingTestObjectFactory.build()
        self.assertEqual(outer.wrap.wrapped.two, 2)
        self.assertEqual(outer.wrap.wrapped_bis.one, 1)

    def testNestedSubFactoryWithOverriddenSubFactories(self):
        """Test nested sub-factories, with attributes overridden with subfactories."""

        class TestObject(object):
            def __init__(self, **kwargs):
                for k, v in kwargs.iteritems():
                    setattr(self, k, v)

        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject
            two = 'two'

        class WrappingTestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            wrapped = factory.SubFactory(TestObjectFactory)
            friend = factory.LazyAttribute(lambda o: o.wrapped.two.four + 1)

        class OuterWrappingTestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            wrap = factory.SubFactory(WrappingTestObjectFactory,
                    wrapped__two=factory.SubFactory(TestObjectFactory, four=4))

        outer = OuterWrappingTestObjectFactory.build()
        self.assertEqual(outer.wrap.wrapped.two.four, 4)
        self.assertEqual(outer.wrap.friend, 5)

    def testSubFactoryAndInheritance(self):
        """Test inheriting from a factory with subfactories, overriding."""
        class TestObject(object):
            def __init__(self, **kwargs):
                for k, v in kwargs.iteritems():
                    setattr(self, k, v)

        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject
            two = 'two'

        class WrappingTestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            wrapped = factory.SubFactory(TestObjectFactory)
            friend = factory.LazyAttribute(lambda o: o.wrapped.two + 1)

        class ExtendedWrappingTestObjectFactory(WrappingTestObjectFactory):
            wrapped__two = 4

        wrapping = ExtendedWrappingTestObjectFactory.build()
        self.assertEqual(wrapping.wrapped.two, 4)
        self.assertEqual(wrapping.friend, 5)

    def testDiamondSubFactory(self):
        """Tests the case where an object has two fields with a common field."""
        class InnerMost(object):
            def __init__(self, a, b):
                self.a = a
                self.b = b

        class SideA(object):
            def __init__(self, inner_from_a):
                self.inner_from_a = inner_from_a

        class SideB(object):
            def __init__(self, inner_from_b):
                self.inner_from_b = inner_from_b

        class OuterMost(object):
            def __init__(self, foo, side_a, side_b):
                self.foo = foo
                self.side_a = side_a
                self.side_b = side_b

        class InnerMostFactory(factory.Factory):
            FACTORY_FOR = InnerMost
            a = 15
            b = 20

        class SideAFactory(factory.Factory):
            FACTORY_FOR = SideA
            inner_from_a = factory.SubFactory(InnerMostFactory, a=20)

        class SideBFactory(factory.Factory):
            FACTORY_FOR = SideB
            inner_from_b = factory.SubFactory(InnerMostFactory, b=15)

        class OuterMostFactory(factory.Factory):
            FACTORY_FOR = OuterMost

            foo = 30
            side_a = factory.SubFactory(SideAFactory,
                inner_from_a__a=factory.ContainerAttribute(lambda obj, containers: containers[1].foo * 2))
            side_b = factory.SubFactory(SideBFactory,
                inner_from_b=factory.ContainerAttribute(lambda obj, containers: containers[0].side_a.inner_from_a))

        outer = OuterMostFactory.build()
        self.assertEqual(outer.foo, 30)
        self.assertEqual(outer.side_a.inner_from_a, outer.side_b.inner_from_b)
        self.assertEqual(outer.side_a.inner_from_a.a, outer.foo * 2)
        self.assertEqual(outer.side_a.inner_from_a.b, 20)

        outer = OuterMostFactory.build(side_a__inner_from_a__b = 4)
        self.assertEqual(outer.foo, 30)
        self.assertEqual(outer.side_a.inner_from_a, outer.side_b.inner_from_b)
        self.assertEqual(outer.side_a.inner_from_a.a, outer.foo * 2)
        self.assertEqual(outer.side_a.inner_from_a.b, 4)


class IteratorTestCase(unittest.TestCase):

    def test_iterator(self):
        class TestObjectFactory(factory.Factory):
            one = factory.Iterator(xrange(10, 30))

        objs = TestObjectFactory.build_batch(20)

        for i, obj in enumerate(objs):
            self.assertEqual(i + 10, obj.one)

    def test_infinite_iterator(self):
        class TestObjectFactory(factory.Factory):
            one = factory.InfiniteIterator(xrange(5))

        objs = TestObjectFactory.build_batch(20)

        for i, obj in enumerate(objs):
            self.assertEqual(i % 5, obj.one)

    def test_infinite_iterator_list_comprehension(self):
        class TestObjectFactory(factory.Factory):
            one = factory.InfiniteIterator([j * 3 for j in xrange(5)])

        # Scope bleeding: j will end up in TestObjectFactory's scope.

        self.assertRaises(TypeError, TestObjectFactory.build)

    def test_infinite_iterator_list_comprehension_protected(self):
        class TestObjectFactory(factory.Factory):
            one = factory.InfiniteIterator([_j * 3 for _j in xrange(5)])

        # Scope bleeding : _j will end up in TestObjectFactory's scope.
        # But factory_boy ignores it, as a protected variable.
        objs = TestObjectFactory.build_batch(20)

        for i, obj in enumerate(objs):
            self.assertEqual(3 * (i % 5), obj.one)

    def test_iterator_decorator(self):
        class TestObjectFactory(factory.Factory):
            @factory.iterator
            def one():
                for i in xrange(10, 50):
                    yield i

        objs = TestObjectFactory.build_batch(20)

        for i, obj in enumerate(objs):
            self.assertEqual(i + 10, obj.one)

    def test_infinite_iterator_decorator(self):
        class TestObjectFactory(factory.Factory):
            @factory.infinite_iterator
            def one():
                for i in xrange(5):
                    yield i

        objs = TestObjectFactory.build_batch(20)

        for i, obj in enumerate(objs):
            self.assertEqual(i % 5, obj.one)



if __name__ == '__main__':
    unittest.main()
