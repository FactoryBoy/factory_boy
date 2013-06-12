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
        def get_or_create(self, **kwargs):
            defaults = kwargs.pop('defaults', {})
            kwargs.update(defaults)
            instance = FakeModel.create(**kwargs)
            instance.id = 2
            instance._defaults = defaults
            return instance, True

        def create(self, **kwargs):
            instance = FakeModel.create(**kwargs)
            instance.id = 2
            instance._defaults = None
            return instance

        def values_list(self, *args, **kwargs):
            return self

        def order_by(self, *args, **kwargs):
            return [1]

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

    def test_create(self):
        obj = factory.create(FakeModel, foo='bar')
        self.assertEqual(obj.id, None)
        self.assertEqual(obj.foo, 'bar')

    def test_create_custom_base(self):
        obj = factory.create(FakeModel, foo='bar', FACTORY_CLASS=factory.django.DjangoModelFactory)
        self.assertEqual(obj.id, 2)
        self.assertEqual(obj.foo, 'bar')

    def test_create_batch(self):
        objs = factory.create_batch(FakeModel, 4, foo='bar')

        self.assertEqual(4, len(objs))
        self.assertEqual(4, len(set(objs)))

        for obj in objs:
            self.assertEqual(obj.id, None)
            self.assertEqual(obj.foo, 'bar')

    def test_create_batch_custom_base(self):
        objs = factory.create_batch(FakeModel, 4, foo='bar',
                FACTORY_CLASS=factory.django.DjangoModelFactory)

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

    def test_generate_create(self):
        obj = factory.generate(FakeModel, factory.CREATE_STRATEGY, foo='bar')
        self.assertEqual(obj.id, None)
        self.assertEqual(obj.foo, 'bar')

    def test_generate_create_custom_base(self):
        obj = factory.generate(FakeModel, factory.CREATE_STRATEGY, foo='bar',
                FACTORY_CLASS=factory.django.DjangoModelFactory)
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

    def test_generate_batch_create(self):
        objs = factory.generate_batch(FakeModel, factory.CREATE_STRATEGY, 20, foo='bar')

        self.assertEqual(20, len(objs))
        self.assertEqual(20, len(set(objs)))

        for obj in objs:
            self.assertEqual(obj.id, None)
            self.assertEqual(obj.foo, 'bar')

    def test_generate_batch_create_custom_base(self):
        objs = factory.generate_batch(FakeModel, factory.CREATE_STRATEGY, 20, foo='bar',
                FACTORY_CLASS=factory.django.DjangoModelFactory)

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

    def test_simple_generate_create(self):
        obj = factory.simple_generate(FakeModel, True, foo='bar')
        self.assertEqual(obj.id, None)
        self.assertEqual(obj.foo, 'bar')

    def test_simple_generate_create_custom_base(self):
        obj = factory.simple_generate(FakeModel, True, foo='bar', FACTORY_CLASS=factory.django.DjangoModelFactory)
        self.assertEqual(obj.id, 2)
        self.assertEqual(obj.foo, 'bar')

    def test_simple_generate_batch_build(self):
        objs = factory.simple_generate_batch(FakeModel, False, 20, foo='bar')

        self.assertEqual(20, len(objs))
        self.assertEqual(20, len(set(objs)))

        for obj in objs:
            self.assertEqual(obj.id, None)
            self.assertEqual(obj.foo, 'bar')

    def test_simple_generate_batch_create(self):
        objs = factory.simple_generate_batch(FakeModel, True, 20, foo='bar')

        self.assertEqual(20, len(objs))
        self.assertEqual(20, len(set(objs)))

        for obj in objs:
            self.assertEqual(obj.id, None)
            self.assertEqual(obj.foo, 'bar')

    def test_simple_generate_batch_create_custom_base(self):
        objs = factory.simple_generate_batch(FakeModel, True, 20, foo='bar',
                FACTORY_CLASS=factory.django.DjangoModelFactory)

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
    def test_attribute(self):
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

    def test_sequence(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            one = factory.Sequence(lambda n: 'one%d' % n)
            two = factory.Sequence(lambda n: 'two%d' % n)

        test_object0 = TestObjectFactory.build()
        self.assertEqual(test_object0.one, 'one0')
        self.assertEqual(test_object0.two, 'two0')

        test_object1 = TestObjectFactory.build()
        self.assertEqual(test_object1.one, 'one1')
        self.assertEqual(test_object1.two, 'two1')

    def test_sequence_custom_begin(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            @classmethod
            def _setup_next_sequence(cls):
                return 42

            one = factory.Sequence(lambda n: 'one%d' % n)
            two = factory.Sequence(lambda n: 'two%d' % n)

        test_object0 = TestObjectFactory.build()
        self.assertEqual('one42', test_object0.one)
        self.assertEqual('two42', test_object0.two)

        test_object1 = TestObjectFactory.build()
        self.assertEqual('one43', test_object1.one)
        self.assertEqual('two43', test_object1.two)

    def test_sequence_override(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            one = factory.Sequence(lambda n: 'one%d' % n)

        o1 = TestObjectFactory()
        o2 = TestObjectFactory()
        o3 = TestObjectFactory(__sequence=42)
        o4 = TestObjectFactory()

        self.assertEqual('one0', o1.one)
        self.assertEqual('one1', o2.one)
        self.assertEqual('one42', o3.one)
        self.assertEqual('one2', o4.one)

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

            one = factory.Sequence(lambda n: 'one%d' % n)
            two = factory.Sequence(lambda n: 'two%d' % n)

        objs = TestObjectFactory.build_batch(20)

        self.assertEqual(20, len(objs))
        self.assertEqual(20, len(set(objs)))
        for i, obj in enumerate(objs):
            self.assertEqual('one%d' % i, obj.one)
            self.assertEqual('two%d' % i, obj.two)

    def test_lazy_attribute(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            one = factory.LazyAttribute(lambda a: 'abc' )
            two = factory.LazyAttribute(lambda a: a.one + ' xyz')

        test_object = TestObjectFactory.build()
        self.assertEqual(test_object.one, 'abc')
        self.assertEqual(test_object.two, 'abc xyz')

    def test_lazy_attribute_sequence(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            one = factory.LazyAttributeSequence(lambda a, n: 'abc%d' % n)
            two = factory.LazyAttributeSequence(lambda a, n: a.one + ' xyz%d' % n)

        test_object0 = TestObjectFactory.build()
        self.assertEqual(test_object0.one, 'abc0')
        self.assertEqual(test_object0.two, 'abc0 xyz0')

        test_object1 = TestObjectFactory.build()
        self.assertEqual(test_object1.one, 'abc1')
        self.assertEqual(test_object1.two, 'abc1 xyz1')

    def test_lazy_attribute_decorator(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            @factory.lazy_attribute
            def one(a):
                return 'one'

        test_object = TestObjectFactory.build()
        self.assertEqual(test_object.one, 'one')

    def test_self_attribute(self):
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

    def test_self_attribute_parent(self):
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

    def test_sequence_decorator(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            @factory.sequence
            def one(n):
                return 'one%d' % n

        test_object = TestObjectFactory.build()
        self.assertEqual(test_object.one, 'one0')

    def test_lazy_attribute_sequence_decorator(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            @factory.lazy_attribute_sequence
            def one(a, n):
                return 'one%d' % n
            @factory.lazy_attribute_sequence
            def two(a, n):
                return a.one + ' two%d' % n

        test_object = TestObjectFactory.build()
        self.assertEqual(test_object.one, 'one0')
        self.assertEqual(test_object.two, 'one0 two0')

    def test_build_with_parameters(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            one = factory.Sequence(lambda n: 'one%d' % n)
            two = factory.Sequence(lambda n: 'two%d' % n)

        test_object0 = TestObjectFactory.build(three='three')
        self.assertEqual(test_object0.one, 'one0')
        self.assertEqual(test_object0.two, 'two0')
        self.assertEqual(test_object0.three, 'three')

        test_object1 = TestObjectFactory.build(one='other')
        self.assertEqual(test_object1.one, 'other')
        self.assertEqual(test_object1.two, 'two1')

    def test_create(self):
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
            one=factory.Sequence(lambda n: str(n)))

        self.assertEqual(20, len(objs))
        self.assertEqual(20, len(set(objs)))

        for i, obj in enumerate(objs):
            self.assertEqual(str(i), obj.one)
            self.assertEqual('%d two' % i, obj.two)
            self.assertEqual(i, obj.three)

    def test_inheritance(self):
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

    def test_inheritance_with_inherited_class(self):
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

    def test_dual_inheritance(self):
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

    def test_class_method_accessible(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            @classmethod
            def alt_create(cls, **kwargs):
                return kwargs

        self.assertEqual(TestObjectFactory.alt_create(foo=1), {"foo": 1})

    def test_static_method_accessible(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            @staticmethod
            def alt_create(**kwargs):
                return kwargs

        self.assertEqual(TestObjectFactory.alt_create(foo=1), {"foo": 1})

    def test_arg_parameters(self):
        class TestObject(object):
            def __init__(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs

        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject
            FACTORY_ARG_PARAMETERS = ('x', 'y')

            x = 1
            y = 2
            z = 3
            t = 4

        obj = TestObjectFactory.build(x=42, z=5)
        self.assertEqual((42, 2), obj.args)
        self.assertEqual({'z': 5, 't': 4}, obj.kwargs)

    def test_hidden_args(self):
        class TestObject(object):
            def __init__(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs

        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject
            FACTORY_HIDDEN_ARGS = ('x', 'z')

            x = 1
            y = 2
            z = 3
            t = 4

        obj = TestObjectFactory.build(x=42, z=5)
        self.assertEqual((), obj.args)
        self.assertEqual({'y': 2, 't': 4}, obj.kwargs)

    def test_hidden_args_and_arg_parameters(self):
        class TestObject(object):
            def __init__(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs

        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject
            FACTORY_HIDDEN_ARGS = ('x', 'z')
            FACTORY_ARG_PARAMETERS = ('y',)

            x = 1
            y = 2
            z = 3
            t = 4

        obj = TestObjectFactory.build(x=42, z=5)
        self.assertEqual((2,), obj.args)
        self.assertEqual({'t': 4}, obj.kwargs)



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
    def test_sub_factory(self):
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

    def test_sub_factory_with_lazy_fields(self):
        class TestModel2(FakeModel):
            pass

        class TestModelFactory(FakeModelFactory):
            FACTORY_FOR = TestModel

        class TestModel2Factory(FakeModelFactory):
            FACTORY_FOR = TestModel2
            two = factory.SubFactory(TestModelFactory,
                                          one=factory.Sequence(lambda n: 'x%dx' % n),
                                          two=factory.LazyAttribute(
                                              lambda o: '%s%s' % (o.one, o.one)))

        test_model = TestModel2Factory(one=42)
        self.assertEqual('x0x', test_model.two.one)
        self.assertEqual('x0xx0x', test_model.two.two)

    def test_sub_factory_and_sequence(self):
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

    def test_sub_factory_overriding(self):
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

    def test_nested_sub_factory(self):
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

    def test_nested_sub_factory_with_overridden_sub_factories(self):
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

    def test_sub_factory_and_inheritance(self):
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

    def test_diamond_sub_factory(self):
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

    @unittest.skipUnless(is_python2, "Scope bleeding fixed in Python3+")
    @tools.disable_warnings
    def test_iterator_list_comprehension_scope_bleeding(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            one = factory.Iterator([j * 3 for j in range(5)])

        # Scope bleeding: j will end up in TestObjectFactory's scope.

        self.assertRaises(TypeError, TestObjectFactory.build)

    @tools.disable_warnings
    def test_iterator_list_comprehension_protected(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject

            one = factory.Iterator([_j * 3 for _j in range(5)])

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


class BetterFakeModelManager(object):
    def __init__(self, keys, instance):
        self.keys = keys
        self.instance = instance

    def get_or_create(self, **kwargs):
        defaults = kwargs.pop('defaults', {})
        if kwargs == self.keys:
            return self.instance, False
        kwargs.update(defaults)
        instance = FakeModel.create(**kwargs)
        instance.id = 2
        return instance, True

    def values_list(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return [1]


class BetterFakeModel(object):
    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        instance.id = 1
        return instance

    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)
            self.id = None


class DjangoModelFactoryTestCase(unittest.TestCase):
    def test_simple(self):
        class FakeModelFactory(factory.django.DjangoModelFactory):
            FACTORY_FOR = FakeModel

        obj = FakeModelFactory(one=1)
        self.assertEqual(1, obj.one)
        self.assertEqual(2, obj.id)

    def test_existing_instance(self):
        prev = BetterFakeModel.create(x=1, y=2, z=3)
        prev.id = 42

        class MyFakeModel(BetterFakeModel):
            objects = BetterFakeModelManager({'x': 1}, prev)

        class MyFakeModelFactory(factory.django.DjangoModelFactory):
            FACTORY_FOR = MyFakeModel
            FACTORY_DJANGO_GET_OR_CREATE = ('x',)
            x = 1
            y = 4
            z = 6

        obj = MyFakeModelFactory()
        self.assertEqual(prev, obj)
        self.assertEqual(1, obj.x)
        self.assertEqual(2, obj.y)
        self.assertEqual(3, obj.z)
        self.assertEqual(42, obj.id)

    def test_existing_instance_complex_key(self):
        prev = BetterFakeModel.create(x=1, y=2, z=3)
        prev.id = 42

        class MyFakeModel(BetterFakeModel):
            objects = BetterFakeModelManager({'x': 1, 'y': 2, 'z': 3}, prev)

        class MyFakeModelFactory(factory.django.DjangoModelFactory):
            FACTORY_FOR = MyFakeModel
            FACTORY_DJANGO_GET_OR_CREATE = ('x', 'y', 'z')
            x = 1
            y = 4
            z = 6

        obj = MyFakeModelFactory(y=2, z=3)
        self.assertEqual(prev, obj)
        self.assertEqual(1, obj.x)
        self.assertEqual(2, obj.y)
        self.assertEqual(3, obj.z)
        self.assertEqual(42, obj.id)

    def test_new_instance(self):
        prev = BetterFakeModel.create(x=1, y=2, z=3)
        prev.id = 42

        class MyFakeModel(BetterFakeModel):
            objects = BetterFakeModelManager({'x': 1}, prev)

        class MyFakeModelFactory(factory.django.DjangoModelFactory):
            FACTORY_FOR = MyFakeModel
            FACTORY_DJANGO_GET_OR_CREATE = ('x',)
            x = 1
            y = 4
            z = 6

        obj = MyFakeModelFactory(x=2)
        self.assertNotEqual(prev, obj)
        self.assertEqual(2, obj.x)
        self.assertEqual(4, obj.y)
        self.assertEqual(6, obj.z)
        self.assertEqual(2, obj.id)

    def test_new_instance_complex_key(self):
        prev = BetterFakeModel.create(x=1, y=2, z=3)
        prev.id = 42

        class MyFakeModel(BetterFakeModel):
            objects = BetterFakeModelManager({'x': 1, 'y': 2, 'z': 3}, prev)

        class MyFakeModelFactory(factory.django.DjangoModelFactory):
            FACTORY_FOR = MyFakeModel
            FACTORY_DJANGO_GET_OR_CREATE = ('x', 'y', 'z')
            x = 1
            y = 4
            z = 6

        obj = MyFakeModelFactory(y=2, z=4)
        self.assertNotEqual(prev, obj)
        self.assertEqual(1, obj.x)
        self.assertEqual(2, obj.y)
        self.assertEqual(4, obj.z)
        self.assertEqual(2, obj.id)


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


class DictTestCase(unittest.TestCase):
    def test_empty_dict(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject
            one = factory.Dict({})

        o = TestObjectFactory()
        self.assertEqual({}, o.one)

    def test_naive_dict(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject
            one = factory.Dict({'a': 1})

        o = TestObjectFactory()
        self.assertEqual({'a': 1}, o.one)

    def test_sequence_dict(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject
            one = factory.Dict({'a': factory.Sequence(lambda n: n + 2)})

        o1 = TestObjectFactory()
        o2 = TestObjectFactory()

        self.assertEqual({'a': 2}, o1.one)
        self.assertEqual({'a': 3}, o2.one)

    def test_dict_override(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject
            one = factory.Dict({'a': 1})

        o = TestObjectFactory(one__a=2)
        self.assertEqual({'a': 2}, o.one)

    def test_dict_extra_key(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject
            one = factory.Dict({'a': 1})

        o = TestObjectFactory(one__b=2)
        self.assertEqual({'a': 1, 'b': 2}, o.one)

    def test_dict_merged_fields(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject
            two = 13
            one = factory.Dict({
                'one': 1,
                'two': 2,
                'three': factory.SelfAttribute('two'),
            })

        o = TestObjectFactory(one__one=42)
        self.assertEqual({'one': 42, 'two': 2, 'three': 2}, o.one)

    def test_nested_dicts(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject
            one = 1
            two = factory.Dict({
                'one': 3,
                'two': factory.SelfAttribute('one'),
                'three': factory.Dict({
                    'one': 5,
                    'two': factory.SelfAttribute('..one'),
                    'three': factory.SelfAttribute('...one'),
                }),
            })

        o = TestObjectFactory()
        self.assertEqual(1, o.one)
        self.assertEqual({
            'one': 3,
            'two': 3,
            'three': {
                'one': 5,
                'two': 3,
                'three': 1,
            },
        }, o.two)


class ListTestCase(unittest.TestCase):
    def test_empty_list(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject
            one = factory.List([])

        o = TestObjectFactory()
        self.assertEqual([], o.one)

    def test_naive_list(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject
            one = factory.List([1])

        o = TestObjectFactory()
        self.assertEqual([1], o.one)

    def test_sequence_list(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject
            one = factory.List([factory.Sequence(lambda n: n + 2)])

        o1 = TestObjectFactory()
        o2 = TestObjectFactory()

        self.assertEqual([2], o1.one)
        self.assertEqual([3], o2.one)

    def test_list_override(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject
            one = factory.List([1])

        o = TestObjectFactory(one__0=2)
        self.assertEqual([2], o.one)

    def test_list_extra_key(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject
            one = factory.List([1])

        o = TestObjectFactory(one__1=2)
        self.assertEqual([1, 2], o.one)

    def test_list_merged_fields(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject
            two = 13
            one = factory.List([
                1,
                2,
                factory.SelfAttribute('1'),
            ])

        o = TestObjectFactory(one__0=42)
        self.assertEqual([42, 2, 2], o.one)

    def test_nested_lists(self):
        class TestObjectFactory(factory.Factory):
            FACTORY_FOR = TestObject
            one = 1
            two = factory.List([
                3,
                factory.SelfAttribute('0'),
                factory.List([
                    5,
                    factory.SelfAttribute('..0'),
                    factory.SelfAttribute('...one'),
                ]),
            ])

        o = TestObjectFactory()
        self.assertEqual(1, o.one)
        self.assertEqual([
            3,
            3,
            [
                5,
                3,
                1,
            ],
        ], o.two)


class DjangoModelFactoryTestCase(unittest.TestCase):
    def test_sequence(self):
        class TestModelFactory(factory.django.DjangoModelFactory):
            FACTORY_FOR = TestModel

            a = factory.Sequence(lambda n: 'foo_%s' % n)

        o1 = TestModelFactory()
        o2 = TestModelFactory()

        self.assertEqual('foo_2', o1.a)
        self.assertEqual('foo_3', o2.a)

        o3 = TestModelFactory.build()
        o4 = TestModelFactory.build()

        self.assertEqual('foo_4', o3.a)
        self.assertEqual('foo_5', o4.a)

    def test_no_get_or_create(self):
        class TestModelFactory(factory.django.DjangoModelFactory):
            FACTORY_FOR = TestModel

            a = factory.Sequence(lambda n: 'foo_%s' % n)

        o = TestModelFactory()
        self.assertEqual(None, o._defaults)
        self.assertEqual('foo_2', o.a)
        self.assertEqual(2, o.id)

    def test_get_or_create(self):
        class TestModelFactory(factory.django.DjangoModelFactory):
            FACTORY_FOR = TestModel
            FACTORY_DJANGO_GET_OR_CREATE = ('a', 'b')

            a = factory.Sequence(lambda n: 'foo_%s' % n)
            b = 2
            c = 3
            d = 4

        o = TestModelFactory()
        self.assertEqual({'c': 3, 'd': 4}, o._defaults)
        self.assertEqual('foo_2', o.a)
        self.assertEqual(2, o.b)
        self.assertEqual(3, o.c)
        self.assertEqual(4, o.d)
        self.assertEqual(2, o.id)

    def test_full_get_or_create(self):
        """Test a DjangoModelFactory with all fields in get_or_create."""
        class TestModelFactory(factory.django.DjangoModelFactory):
            FACTORY_FOR = TestModel
            FACTORY_DJANGO_GET_OR_CREATE = ('a', 'b', 'c', 'd')

            a = factory.Sequence(lambda n: 'foo_%s' % n)
            b = 2
            c = 3
            d = 4

        o = TestModelFactory()
        self.assertEqual({}, o._defaults)
        self.assertEqual('foo_2', o.a)
        self.assertEqual(2, o.b)
        self.assertEqual(3, o.c)
        self.assertEqual(4, o.d)
        self.assertEqual(2, o.id)


if __name__ == '__main__':
    unittest.main()
