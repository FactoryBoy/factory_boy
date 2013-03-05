# -*- coding: utf-8 -*-
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
"""Tests using factory."""


import functools
import os
import sys
import warnings

import factory

from .compat import is_python2, unittest
from . import tools


class TestObject(object):
    def __init__(self, one=None, two=None, three=None, four=None, five=None):
        self.one = one
        self.two = two
        self.three = three
        self.four = four
        self.five = five


class FakeModel(object):
    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        instance.id = 1
        return instance

    class FakeModelManager(object):
        def create(self, **kwargs):
            instance = FakeModel.create(**kwargs)
            instance.id = 2
            return instance

    objects = FakeModelManager()

    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)
            self.id = None


class FakeModelFactory(factory.Factory):
    ABSTRACT_FACTORY = True

    @classmethod
    def _create(cls, target_class, *args, **kwargs):
        return target_class.create(**kwargs)


class TestModel(FakeModel):
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

    @tools.disable_warnings
    def test_create(self):
        obj = factory.create(FakeModel, foo='bar')
        self.assertEqual(obj.id, 2)
        self.assertEqual(obj.foo, 'bar')

    @tools.disable_warnings
    def test_create_batch(self):
        objs = factory.create_batch(FakeModel, 4, foo='bar')

        self.assertEqual(4, len(objs))
        self.assertEqual(4, len(set(objs)))

        for obj in objs:
            self.assertEqual(obj.id, 2)
            self.assertEqual(obj.foo, 'bar')

    def test_stub(self):
        obj = factory.stub(TestObject, three=3)
        self.assertEqual(obj.three, 3)
        self.assertFalse(hasattr(obj, 'two'))

    def test_stub_batch(self):
        objs = factory.stub_batch(FakeModel, 4, foo='bar')

        self.assertEqual(4, len(objs))
        self.assertEqual(4, len(set(objs)))

        for obj in objs:
            self.assertFalse(hasattr(obj, 'id'))
            self.assertEqual(obj.foo, 'bar')

    def test_generate_build(self):
        obj = factory.generate(FakeModel, factory.BUILD_STRATEGY, foo='bar')
        self.assertEqual(obj.id, None)
        self.assertEqual(obj.foo, 'bar')

    @tools.disable_warnings
    def test_generate_create(self):
        obj = factory.generate(FakeModel, factory.CREATE_STRATEGY, foo='bar')
        self.assertEqual(obj.id, 2)
        self.assertEqual(obj.foo, 'bar')

    def test_generate_stub(self):
        obj = factory.generate(FakeModel, factory.STUB_STRATEGY, foo='bar')
        self.assertFalse(hasattr(obj, 'id'))
        self.assertEqual(obj.foo, 'bar')

    def test_generate_batch_build(self):
        objs = factory.generate_batch(FakeModel, factory.BUILD_STRATEGY, 20, foo='bar')

        self.assertEqual(20, len(objs))
        self.assertEqual(20, len(set(objs)))

        for obj in objs:
            self.assertEqual(obj.id, None)
            self.assertEqual(obj.foo, 'bar')

    @tools.disable_warnings
    def test_generate_batch_create(self):
        objs = factory.generate_batch(FakeModel, factory.CREATE_STRATEGY, 20, foo='bar')

        self.assertEqual(20, len(objs))
        self.assertEqual(20, len(set(objs)))

        for obj in objs:
            self.assertEqual(obj.id, 2)
            self.assertEqual(obj.foo, 'bar')

    def test_generate_batch_stub(self):
        objs = factory.generate_batch(FakeModel, factory.STUB_STRATEGY, 20, foo='bar')

        self.assertEqual(20, len(objs))
        self.assertEqual(20, len(set(objs)))

        for obj in objs:
            self.assertFalse(hasattr(obj, 'id'))
            self.assertEqual(obj.foo, 'bar')

    def test_simple_generate_build(self):
        obj = factory.simple_generate(FakeModel, False, foo='bar')
        self.assertEqual(obj.id, None)
        self.assertEqual(obj.foo, 'bar')

    @tools.disable_warnings
    def test_simple_generate_create(self):
        obj = factory.simple_generate(FakeModel, True, foo='bar')
        self.assertEqual(obj.id, 2)
        self.assertEqual(obj.foo, 'bar')

    def test_simple_generate_batch_build(self):
        objs = factory.simple_generate_batch(FakeModel, False, 20, foo='bar')

        self.assertEqual(20, len(objs))
        self.assertEqual(20, len(set(objs)))

        for obj in objs:
            self.assertEqual(obj.id, None)
            self.assertEqual(obj.foo, 'bar')

    @tools.disable_warnings
    def test_simple_generate_batch_create(self):
        objs = factory.simple_generate_batch(FakeModel, True, 20, foo='bar')

        self.assertEqual(20, len(objs))
        self.assertEqual(20, len(set(objs)))

        for obj in objs:
            self.assertEqual(obj.id, 2)
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


class UsingFactoryTestCase(unittest.TestCase):
    def testAttribute(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            one = 'one'

        test_object = TestObjectFactory.build()
        self.assertEqual(test_object.one, 'one')

    def test_inheritance(self):
        @factory.use_strategy(factory.BUILD_STRATEGY)
        class TestObjectFactory(factory.Factory, TestObject):
            FACTORY_FOR = TestObject

            one = 'one'

        test_object = TestObjectFactory()
        self.assertEqual(test_object.one, 'one')

    def test_abstract(self):
        class SomeAbstractFactory(factory.Factory):
            ABSTRACT_FACTORY = True
            one = 'one'

        class InheritedFactory(SomeAbstractFactory):
            FACTORY_FOR = TestObject

        test_object = InheritedFactory.build()
        self.assertEqual(test_object.one, 'one')

    def testSequence(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

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
            FACTORY_FOR = TestObject

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

    def test_custom_create(self):
        class TestModelFactory(factory.Factory):
            FACTORY_FOR = TestModel

            two = 2

            @classmethod
            def _create(cls, target_class, *args, **kwargs):
                obj = target_class.create(**kwargs)
                obj.properly_created = True
                return obj

        obj = TestModelFactory.create(one=1)
        self.assertEqual(1, obj.one)
        self.assertEqual(2, obj.two)
        self.assertEqual(1, obj.id)
        self.assertTrue(obj.properly_created)

    def test_non_django_create(self):
        class NonDjango(object):
            def __init__(self, x, y=2):
                self.x = x
                self.y = y

        class NonDjangoFactory(factory.Factory):
            FACTORY_FOR = NonDjango

            x = 3

        obj = NonDjangoFactory.create()
        self.assertEqual(3, obj.x)
        self.assertEqual(2, obj.y)

    def test_sequence_batch(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

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
            FACTORY_FOR = TestObject

            one = factory.LazyAttribute(lambda a: 'abc' )
            two = factory.LazyAttribute(lambda a: a.one + ' xyz')

        test_object = TestObjectFactory.build()
        self.assertEqual(test_object.one, 'abc')
        self.assertEqual(test_object.two, 'abc xyz')

    def testLazyAttributeSequence(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

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
            FACTORY_FOR = TestObject

            @factory.lazy_attribute
            def one(a):
                return 'one'

        test_object = TestObjectFactory.build()
        self.assertEqual(test_object.one, 'one')

    def testSelfAttribute(self):
        class TmpObj(object):
            n = 3

        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

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

    def testSelfAttributeParent(self):
        class TestModel2(FakeModel):
            pass

        class TestModelFactory(FakeModelFactory):
            FACTORY_FOR = TestModel
            one = 3
            three = factory.SelfAttribute('..bar')

        class TestModel2Factory(FakeModelFactory):
            FACTORY_FOR = TestModel2
            bar = 4
            two = factory.SubFactory(TestModelFactory, one=1)

        test_model = TestModel2Factory()
        self.assertEqual(4, test_model.two.three)

    def testSequenceDecorator(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            @factory.sequence
            def one(n):
                return 'one' + n

        test_object = TestObjectFactory.build()
        self.assertEqual(test_object.one, 'one0')

    def testLazyAttributeSequenceDecorator(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

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
            FACTORY_FOR = TestObject

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
        class TestModelFactory(FakeModelFactory):
            FACTORY_FOR = TestModel

            one = 'one'

        test_model = TestModelFactory.create()
        self.assertEqual(test_model.one, 'one')
        self.assertTrue(test_model.id)

    def test_create_batch(self):
        class TestModelFactory(FakeModelFactory):
            FACTORY_FOR = TestModel

            one = 'one'

        objs = TestModelFactory.create_batch(20, two=factory.Sequence(int))

        self.assertEqual(20, len(objs))
        self.assertEqual(20, len(set(objs)))

        for i, obj in enumerate(objs):
            self.assertEqual('one', obj.one)
            self.assertEqual(i, obj.two)
            self.assertTrue(obj.id)

    def test_generate_build(self):
        class TestModelFactory(FakeModelFactory):
            FACTORY_FOR = TestModel

            one = 'one'

        test_model = TestModelFactory.generate(factory.BUILD_STRATEGY)
        self.assertEqual(test_model.one, 'one')
        self.assertFalse(test_model.id)

    def test_generate_create(self):
        class TestModelFactory(FakeModelFactory):
            FACTORY_FOR = TestModel

            one = 'one'

        test_model = TestModelFactory.generate(factory.CREATE_STRATEGY)
        self.assertEqual(test_model.one, 'one')
        self.assertTrue(test_model.id)

    def test_generate_stub(self):
        class TestModelFactory(FakeModelFactory):
            FACTORY_FOR = TestModel

            one = 'one'

        test_model = TestModelFactory.generate(factory.STUB_STRATEGY)
        self.assertEqual(test_model.one, 'one')
        self.assertFalse(hasattr(test_model, 'id'))

    def test_generate_batch_build(self):
        class TestModelFactory(FakeModelFactory):
            FACTORY_FOR = TestModel

            one = 'one'

        objs = TestModelFactory.generate_batch(factory.BUILD_STRATEGY, 20, two='two')

        self.assertEqual(20, len(objs))
        self.assertEqual(20, len(set(objs)))

        for i, obj in enumerate(objs):
            self.assertEqual('one', obj.one)
            self.assertEqual('two', obj.two)
            self.assertFalse(obj.id)

    def test_generate_batch_create(self):
        class TestModelFactory(FakeModelFactory):
            FACTORY_FOR = TestModel

            one = 'one'

        objs = TestModelFactory.generate_batch(factory.CREATE_STRATEGY, 20, two='two')

        self.assertEqual(20, len(objs))
        self.assertEqual(20, len(set(objs)))

        for i, obj in enumerate(objs):
            self.assertEqual('one', obj.one)
            self.assertEqual('two', obj.two)
            self.assertTrue(obj.id)

    def test_generate_batch_stub(self):
        class TestModelFactory(FakeModelFactory):
            FACTORY_FOR = TestModel

            one = 'one'

        objs = TestModelFactory.generate_batch(factory.STUB_STRATEGY, 20, two='two')

        self.assertEqual(20, len(objs))
        self.assertEqual(20, len(set(objs)))

        for i, obj in enumerate(objs):
            self.assertEqual('one', obj.one)
            self.assertEqual('two', obj.two)
            self.assertFalse(hasattr(obj, 'id'))

    def test_simple_generate_build(self):
        class TestModelFactory(FakeModelFactory):
            FACTORY_FOR = TestModel

            one = 'one'

        test_model = TestModelFactory.simple_generate(False)
        self.assertEqual(test_model.one, 'one')
        self.assertFalse(test_model.id)

    def test_simple_generate_create(self):
        class TestModelFactory(FakeModelFactory):
            FACTORY_FOR = TestModel

            one = 'one'

        test_model = TestModelFactory.simple_generate(True)
        self.assertEqual(test_model.one, 'one')
        self.assertTrue(test_model.id)

    def test_simple_generate_batch_build(self):
        class TestModelFactory(FakeModelFactory):
            FACTORY_FOR = TestModel

            one = 'one'

        objs = TestModelFactory.simple_generate_batch(False, 20, two='two')

        self.assertEqual(20, len(objs))
        self.assertEqual(20, len(set(objs)))

        for i, obj in enumerate(objs):
            self.assertEqual('one', obj.one)
            self.assertEqual('two', obj.two)
            self.assertFalse(obj.id)

    def test_simple_generate_batch_create(self):
        class TestModelFactory(FakeModelFactory):
            FACTORY_FOR = TestModel

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
            FACTORY_FOR = TestObject

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
            FACTORY_FOR = TestObject

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
            FACTORY_FOR = TestObject

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
            FACTORY_FOR = TestObject

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

    @tools.disable_warnings
    def test_set_building_function(self):
        def building_function(class_to_create, **kwargs):
            return "This doesn't even return an instance of {0}".format(class_to_create.__name__)

        class TestModelFactory(FakeModelFactory):
            FACTORY_FOR = TestModel

        TestModelFactory.set_building_function(building_function)

        test_object = TestModelFactory.build()
        self.assertEqual(test_object, "This doesn't even return an instance of TestModel")

    @tools.disable_warnings
    def testSetCreationFunction(self):
        def creation_function(class_to_create, **kwargs):
            return "This doesn't even return an instance of {0}".format(class_to_create.__name__)

        class TestModelFactory(FakeModelFactory):
            FACTORY_FOR = TestModel

        TestModelFactory.set_creation_function(creation_function)

        test_object = TestModelFactory.create()
        self.assertEqual(test_object, "This doesn't even return an instance of TestModel")

    def testClassMethodAccessible(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            @classmethod
            def alt_create(cls, **kwargs):
                return kwargs

        self.assertEqual(TestObjectFactory.alt_create(foo=1), {"foo": 1})

    def testStaticMethodAccessible(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            @staticmethod
            def alt_create(**kwargs):
                return kwargs

        self.assertEqual(TestObjectFactory.alt_create(foo=1), {"foo": 1})


class NonKwargParametersTestCase(unittest.TestCase):
    def test_build(self):
        class TestObject(object):
            def __init__(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs

        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject
            FACTORY_ARG_PARAMETERS = ('one', 'two',)

            one = 1
            two = 2
            three = 3

        obj = TestObjectFactory.build()
        self.assertEqual((1, 2), obj.args)
        self.assertEqual({'three': 3}, obj.kwargs)

    def test_create(self):
        class TestObject(object):
            def __init__(self, *args, **kwargs):
                self.args = None
                self.kwargs = None

            @classmethod
            def create(cls, *args, **kwargs):
                inst = cls()
                inst.args = args
                inst.kwargs = kwargs
                return inst

        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject
            FACTORY_ARG_PARAMETERS = ('one', 'two')

            one = 1
            two = 2
            three = 3

            @classmethod
            def _create(cls, target_class, *args, **kwargs):
                return target_class.create(*args, **kwargs)

        obj = TestObjectFactory.create()
        self.assertEqual((1, 2), obj.args)
        self.assertEqual({'three': 3}, obj.kwargs)


class KwargAdjustTestCase(unittest.TestCase):
    """Tests for the _adjust_kwargs method."""

    def test_build(self):
        class TestObject(object):
            def __init__(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs

        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            @classmethod
            def _adjust_kwargs(cls, **kwargs):
                kwargs['foo'] = len(kwargs)
                return kwargs

        obj = TestObjectFactory.build(x=1, y=2, z=3)
        self.assertEqual({'x': 1, 'y': 2, 'z': 3, 'foo': 3}, obj.kwargs)
        self.assertEqual((), obj.args)


class SubFactoryTestCase(unittest.TestCase):
    def testSubFactory(self):
        class TestModel2(FakeModel):
            pass

        class TestModelFactory(FakeModelFactory):
            FACTORY_FOR = TestModel
            one = 3

        class TestModel2Factory(FakeModelFactory):
            FACTORY_FOR = TestModel2
            two = factory.SubFactory(TestModelFactory, one=1)

        test_model = TestModel2Factory(two__one=4)
        self.assertEqual(4, test_model.two.one)
        self.assertEqual(1, test_model.id)
        self.assertEqual(1, test_model.two.id)

    def testSubFactoryWithLazyFields(self):
        class TestModel2(FakeModel):
            pass

        class TestModelFactory(FakeModelFactory):
            FACTORY_FOR = TestModel

        class TestModel2Factory(FakeModelFactory):
            FACTORY_FOR = TestModel2
            two = factory.SubFactory(TestModelFactory,
                                          one=factory.Sequence(lambda n: 'x%sx' % n),
                                          two=factory.LazyAttribute(
                                              lambda o: '%s%s' % (o.one, o.one)))

        test_model = TestModel2Factory(one=42)
        self.assertEqual('x0x', test_model.two.one)
        self.assertEqual('x0xx0x', test_model.two.two)

    def testSubFactoryAndSequence(self):
        class TestObject(object):
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)

        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            one = factory.Sequence(lambda n: int(n))

        class WrappingTestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            wrapped = factory.SubFactory(TestObjectFactory)

        wrapping = WrappingTestObjectFactory.build()
        self.assertEqual(0, wrapping.wrapped.one)
        wrapping = WrappingTestObjectFactory.build()
        self.assertEqual(1, wrapping.wrapped.one)

    def testSubFactoryOverriding(self):
        class TestObject(object):
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)

        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject


        class OtherTestObject(object):
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)

        class WrappingTestObjectFactory(factory.Factory):
            FACTORY_FOR = OtherTestObject

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
                for k, v in kwargs.items():
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
                for k, v in kwargs.items():
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
                for k, v in kwargs.items():
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

    def test_nonstrict_container_attribute(self):
        class TestModel2(FakeModel):
            pass

        class TestModelFactory(FakeModelFactory):
            FACTORY_FOR = TestModel
            one = 3
            two = factory.ContainerAttribute(lambda obj, containers: len(containers or []), strict=False)

        class TestModel2Factory(FakeModelFactory):
            FACTORY_FOR = TestModel2
            one = 1
            two = factory.SubFactory(TestModelFactory, one=1)

        obj = TestModel2Factory.build()
        self.assertEqual(1, obj.one)
        self.assertEqual(1, obj.two.one)
        self.assertEqual(1, obj.two.two)

        obj = TestModelFactory()
        self.assertEqual(3, obj.one)
        self.assertEqual(0, obj.two)

    def test_strict_container_attribute(self):
        class TestModel2(FakeModel):
            pass

        class TestModelFactory(FakeModelFactory):
            FACTORY_FOR = TestModel
            one = 3
            two = factory.ContainerAttribute(lambda obj, containers: len(containers or []), strict=True)

        class TestModel2Factory(FakeModelFactory):
            FACTORY_FOR = TestModel2
            one = 1
            two = factory.SubFactory(TestModelFactory, one=1)

        obj = TestModel2Factory.build()
        self.assertEqual(1, obj.one)
        self.assertEqual(1, obj.two.one)
        self.assertEqual(1, obj.two.two)

        self.assertRaises(TypeError, TestModelFactory.build)

    def test_function_container_attribute(self):
        class TestModel2(FakeModel):
            pass

        class TestModelFactory(FakeModelFactory):
            FACTORY_FOR = TestModel
            one = 3

            @factory.container_attribute
            def two(self, containers):
                if containers:
                    return len(containers)
                return 42

        class TestModel2Factory(FakeModelFactory):
            FACTORY_FOR = TestModel2
            one = 1
            two = factory.SubFactory(TestModelFactory, one=1)

        obj = TestModel2Factory.build()
        self.assertEqual(1, obj.one)
        self.assertEqual(1, obj.two.one)
        self.assertEqual(1, obj.two.two)

        obj = TestModelFactory()
        self.assertEqual(3, obj.one)
        self.assertEqual(42, obj.two)


class IteratorTestCase(unittest.TestCase):

    def test_iterator(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            one = factory.Iterator(range(10, 30))

        objs = TestObjectFactory.build_batch(20)

        for i, obj in enumerate(objs):
            self.assertEqual(i + 10, obj.one)

    def test_infinite_iterator_deprecated(self):
        with warnings.catch_warnings(record=True) as w:
            __warningregistry__.clear()

            warnings.simplefilter('always')
            class TestObjectFactory(factory.Factory):
                FACTORY_FOR = TestObject

                foo = factory.InfiniteIterator(range(5))

            self.assertEqual(1, len(w))
            self.assertIn('InfiniteIterator', str(w[0].message))
            self.assertIn('deprecated', str(w[0].message))

    @tools.disable_warnings
    def test_infinite_iterator(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            one = factory.InfiniteIterator(range(5))

        objs = TestObjectFactory.build_batch(20)

        for i, obj in enumerate(objs):
            self.assertEqual(i % 5, obj.one)

    @unittest.skipUnless(is_python2, "Scope bleeding fixed in Python3+")
    @tools.disable_warnings
    def test_infinite_iterator_list_comprehension_scope_bleeding(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            one = factory.InfiniteIterator([j * 3 for j in range(5)])

        # Scope bleeding: j will end up in TestObjectFactory's scope.

        self.assertRaises(TypeError, TestObjectFactory.build)

    @tools.disable_warnings
    def test_infinite_iterator_list_comprehension_protected(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            one = factory.InfiniteIterator([_j * 3 for _j in range(5)])

        # Scope bleeding : _j will end up in TestObjectFactory's scope.
        # But factory_boy ignores it, as a protected variable.
        objs = TestObjectFactory.build_batch(20)

        for i, obj in enumerate(objs):
            self.assertEqual(3 * (i % 5), obj.one)

    def test_iterator_decorator(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            @factory.iterator
            def one():
                for i in range(10, 50):
                    yield i

        objs = TestObjectFactory.build_batch(20)

        for i, obj in enumerate(objs):
            self.assertEqual(i + 10, obj.one)

    def test_infinite_iterator_decorator_deprecated(self):
        with warnings.catch_warnings(record=True) as w:
            __warningregistry__.clear()

            warnings.simplefilter('always')
            class TestObjectFactory(factory.Factory):
                FACTORY_FOR = TestObject

                @factory.infinite_iterator
                def one():
                    return range(5)

            self.assertEqual(1, len(w))
            self.assertIn('infinite_iterator', str(w[0].message))
            self.assertIn('deprecated', str(w[0].message))

    @tools.disable_warnings
    def test_infinite_iterator_decorator(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            @factory.infinite_iterator
            def one():
                for i in range(5):
                    yield i

        objs = TestObjectFactory.build_batch(20)

        for i, obj in enumerate(objs):
            self.assertEqual(i % 5, obj.one)


class PostGenerationTestCase(unittest.TestCase):
    def test_post_generation(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            one = 1

            @factory.post_generation
            def incr_one(self, _create, _increment):
                self.one += 1

        obj = TestObjectFactory.build()
        self.assertEqual(2, obj.one)
        self.assertFalse(hasattr(obj, 'incr_one'))

        obj = TestObjectFactory.build(one=2)
        self.assertEqual(3, obj.one)
        self.assertFalse(hasattr(obj, 'incr_one'))

    def test_post_generation_hook(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            one = 1

            @factory.post_generation
            def incr_one(self, _create, _increment):
                self.one += 1
                return 42

            @classmethod
            def _after_postgeneration(cls, obj, create, results):
                obj.create = create
                obj.results = results

        obj = TestObjectFactory.build()
        self.assertEqual(2, obj.one)
        self.assertFalse(obj.create)
        self.assertEqual({'incr_one': 42}, obj.results)

    @tools.disable_warnings
    def test_post_generation_calling(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            one = 1

            @factory.post_generation()
            def incr_one(self, _create, _increment):
                self.one += 1

        obj = TestObjectFactory.build()
        self.assertEqual(2, obj.one)
        self.assertFalse(hasattr(obj, 'incr_one'))

        obj = TestObjectFactory.build(one=2)
        self.assertEqual(3, obj.one)
        self.assertFalse(hasattr(obj, 'incr_one'))

    def test_post_generation_extraction(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            one = 1

            @factory.post_generation
            def incr_one(self, _create, increment=1):
                self.one += increment

        obj = TestObjectFactory.build(incr_one=2)
        self.assertEqual(3, obj.one)
        self.assertFalse(hasattr(obj, 'incr_one'))

        obj = TestObjectFactory.build(one=2, incr_one=2)
        self.assertEqual(4, obj.one)
        self.assertFalse(hasattr(obj, 'incr_one'))

    def test_post_generation_extraction_lambda(self):

        def my_lambda(obj, create, extracted, **kwargs):
            self.assertTrue(isinstance(obj, TestObject))
            self.assertFalse(create)
            self.assertEqual(extracted, 42)
            self.assertEqual(kwargs, {'foo': 13})

        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            bar = factory.PostGeneration(my_lambda)

        obj = TestObjectFactory.build(bar=42, bar__foo=13)

    def test_post_generation_method_call(self):
        calls = []

        class TestObject(object):
            def __init__(self, one=None, two=None):
                self.one = one
                self.two = two
                self.extra = None

            def call(self, *args, **kwargs):
                self.extra = (args, kwargs)

        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject
            one = 3
            two = 2
            post_call = factory.PostGenerationMethodCall('call', one=1)

        obj = TestObjectFactory.build()
        self.assertEqual(3, obj.one)
        self.assertEqual(2, obj.two)
        self.assertEqual(((), {'one': 1}), obj.extra)

        obj = TestObjectFactory.build(post_call__one=2, post_call__two=3)
        self.assertEqual(3, obj.one)
        self.assertEqual(2, obj.two)
        self.assertEqual(((), {'one': 2, 'two': 3}), obj.extra)

    def test_related_factory(self):
        class TestRelatedObject(object):
            def __init__(self, obj=None, one=None, two=None):
                obj.related = self
                self.one = one
                self.two = two
                self.three = obj

        class TestRelatedObjectFactory(factory.Factory):
            FACTORY_FOR = TestRelatedObject
            one = 1
            two = factory.LazyAttribute(lambda o: o.one + 1)

        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject
            one = 3
            two = 2
            three = factory.RelatedFactory(TestRelatedObjectFactory, name='obj')

        obj = TestObjectFactory.build()
        # Normal fields
        self.assertEqual(3, obj.one)
        self.assertEqual(2, obj.two)
        # RelatedFactory was built
        self.assertIsNone(obj.three)
        self.assertIsNotNone(obj.related)
        self.assertEqual(1, obj.related.one)
        self.assertEqual(2, obj.related.two)
        # RelatedFactory was passed "parent" object
        self.assertEqual(obj, obj.related.three)

        obj = TestObjectFactory.build(three__one=3)
        # Normal fields
        self.assertEqual(3, obj.one)
        self.assertEqual(2, obj.two)
        # RelatedFactory was build
        self.assertIsNone(obj.three)
        self.assertIsNotNone(obj.related)
        # three__one was correctly parse
        self.assertEqual(3, obj.related.one)
        self.assertEqual(4, obj.related.two)
        # RelatedFactory received "parent" object
        self.assertEqual(obj, obj.related.three)

    def test_related_factory_no_name(self):
        relateds = []
        class TestRelatedObject(object):
            def __init__(self, obj=None, one=None, two=None):
                relateds.append(self)
                self.one = one
                self.two = two
                self.three = obj

        class TestRelatedObjectFactory(factory.Factory):
            FACTORY_FOR = TestRelatedObject
            one = 1
            two = factory.LazyAttribute(lambda o: o.one + 1)

        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject
            one = 3
            two = 2
            three = factory.RelatedFactory(TestRelatedObjectFactory)

        obj = TestObjectFactory.build()
        # Normal fields
        self.assertEqual(3, obj.one)
        self.assertEqual(2, obj.two)
        # RelatedFactory was built
        self.assertIsNone(obj.three)
        self.assertEqual(1, len(relateds))
        related = relateds[0]
        self.assertEqual(1, related.one)
        self.assertEqual(2, related.two)
        self.assertIsNone(related.three)

        obj = TestObjectFactory.build(three__one=3)
        # Normal fields
        self.assertEqual(3, obj.one)
        self.assertEqual(2, obj.two)
        # RelatedFactory was build
        self.assertIsNone(obj.three)
        self.assertEqual(2, len(relateds))

        related = relateds[1]
        self.assertEqual(3, related.one)
        self.assertEqual(4, related.two)


class CircularTestCase(unittest.TestCase):
    def test_example(self):
        sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

        from .cyclic import foo
        f = foo.FooFactory.build(bar__foo=None)
        self.assertEqual(42, f.x)
        self.assertEqual(13, f.bar.y)
        self.assertIsNone(f.bar.foo)

        from .cyclic import bar
        b = bar.BarFactory.build(foo__bar__foo__bar=None)
        self.assertEqual(13, b.y)
        self.assertEqual(42, b.foo.x)
        self.assertEqual(13, b.foo.bar.y)
        self.assertEqual(42, b.foo.bar.foo.x)
        self.assertIsNone(b.foo.bar.foo.bar)



if __name__ == '__main__':
    unittest.main()
