# Copyright (c) 2010 Mark Sandstrom
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

import unittest

from base import BaseFactory, Factory, StubFactory, BUILD_STRATEGY, CREATE_STRATEGY, STUB_STRATEGY
import declarations

class TestObject(object):
    def __init__(self, one=None, two=None, three=None, four=None):
        self.one = one
        self.two = two
        self.three = three
        self.four = four

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


class SafetyTestCase(unittest.TestCase):
    def testBaseFactory(self):
        self.assertRaises(RuntimeError, BaseFactory)


class FactoryTestCase(unittest.TestCase):
    def testAttribute(self):
        class TestObjectFactory(Factory):
            one = 'one'

        test_object = TestObjectFactory.build()
        self.assertEqual(test_object.one, 'one')

    def testSequence(self):
        class TestObjectFactory(Factory):
            one = declarations.Sequence(lambda n: 'one' + n)
            two = declarations.Sequence(lambda n: 'two' + n)

        test_object0 = TestObjectFactory.build()
        self.assertEqual(test_object0.one, 'one0')
        self.assertEqual(test_object0.two, 'two0')

        test_object1 = TestObjectFactory.build()
        self.assertEqual(test_object1.one, 'one1')
        self.assertEqual(test_object1.two, 'two1')

    def testSequenceCustomBegin(self):
        class TestObjectFactory(Factory):
            @classmethod
            def _setup_next_sequence(cls):
                return 42

            one = declarations.Sequence(lambda n: 'one' + n)
            two = declarations.Sequence(lambda n: 'two' + n)

        test_object0 = TestObjectFactory.build()
        self.assertEqual('one42', test_object0.one)
        self.assertEqual('two42', test_object0.two)

        test_object1 = TestObjectFactory.build()
        self.assertEqual('one43', test_object1.one)
        self.assertEqual('two43', test_object1.two)

    def testLazyAttribute(self):
        class TestObjectFactory(Factory):
            one = declarations.LazyAttribute(lambda a: 'abc' )
            two = declarations.LazyAttribute(lambda a: a.one + ' xyz')

        test_object = TestObjectFactory.build()
        self.assertEqual(test_object.one, 'abc')
        self.assertEqual(test_object.two, 'abc xyz')

    def testLazyAttributeNonExistentParam(self):
        class TestObjectFactory(Factory):
            one = declarations.LazyAttribute(lambda a: a.does_not_exist )

        try:
            TestObjectFactory()
            self.fail()
        except AttributeError as e:
            self.assertTrue('does not exist' in str(e))

    def testLazyAttributeSequence(self):
        class TestObjectFactory(Factory):
            one = declarations.LazyAttributeSequence(lambda a, n: 'abc' + n)
            two = declarations.LazyAttributeSequence(lambda a, n: a.one + ' xyz' + n)

        test_object0 = TestObjectFactory.build()
        self.assertEqual(test_object0.one, 'abc0')
        self.assertEqual(test_object0.two, 'abc0 xyz0')

        test_object1 = TestObjectFactory.build()
        self.assertEqual(test_object1.one, 'abc1')
        self.assertEqual(test_object1.two, 'abc1 xyz1')

    def testLazyAttributeDecorator(self):
        class TestObjectFactory(Factory):
            @declarations.lazy_attribute
            def one(a):
                return 'one'

        test_object = TestObjectFactory.build()
        self.assertEqual(test_object.one, 'one')

    def testSelfAttribute(self):
        class TestObjectFactory(Factory):
            one = 'xx'
            two = declarations.SelfAttribute('one')

        test_object = TestObjectFactory.build(one=1)
        self.assertEqual(1, test_object.two)

    def testSequenceDecorator(self):
        class TestObjectFactory(Factory):
            @declarations.sequence
            def one(n):
                return 'one' + n

        test_object = TestObjectFactory.build()
        self.assertEqual(test_object.one, 'one0')

    def testLazyAttributeSequenceDecorator(self):
        class TestObjectFactory(Factory):
            @declarations.lazy_attribute_sequence
            def one(a, n):
                return 'one' + n
            @declarations.lazy_attribute_sequence
            def two(a, n):
                return a.one + ' two' + n

        test_object = TestObjectFactory.build()
        self.assertEqual(test_object.one, 'one0')
        self.assertEqual(test_object.two, 'one0 two0')

    def testBuildWithParameters(self):
        class TestObjectFactory(Factory):
            one = declarations.Sequence(lambda n: 'one' + n)
            two = declarations.Sequence(lambda n: 'two' + n)

        test_object0 = TestObjectFactory.build(three='three')
        self.assertEqual(test_object0.one, 'one0')
        self.assertEqual(test_object0.two, 'two0')
        self.assertEqual(test_object0.three, 'three')

        test_object1 = TestObjectFactory.build(one='other')
        self.assertEqual(test_object1.one, 'other')
        self.assertEqual(test_object1.two, 'two1')

    def testCreate(self):
        class TestModelFactory(Factory):
            one = 'one'

        test_model = TestModelFactory.create()
        self.assertEqual(test_model.one, 'one')
        self.assertTrue(test_model.id)

    def testInheritance(self):
        class TestObjectFactory(Factory):
            one = 'one'
            two = declarations.LazyAttribute(lambda a: a.one + ' two')

        class TestObjectFactory2(TestObjectFactory):
            FACTORY_FOR = TestObject

            three = 'three'
            four = declarations.LazyAttribute(lambda a: a.three + ' four')

        test_object = TestObjectFactory2.build()
        self.assertEqual(test_object.one, 'one')
        self.assertEqual(test_object.two, 'one two')
        self.assertEqual(test_object.three, 'three')
        self.assertEqual(test_object.four, 'three four')

        test_object_alt = TestObjectFactory.build()
        self.assertEqual(None, test_object_alt.three)

    def testInheritanceWithInheritedClass(self):
        class TestObjectFactory(Factory):
            one = 'one'
            two = declarations.LazyAttribute(lambda a: a.one + ' two')

        class TestFactory(TestObjectFactory):
            three = 'three'
            four = declarations.LazyAttribute(lambda a: a.three + ' four')

        test_object = TestFactory.build()
        self.assertEqual(test_object.one, 'one')
        self.assertEqual(test_object.two, 'one two')
        self.assertEqual(test_object.three, 'three')
        self.assertEqual(test_object.four, 'three four')

    def testSetCreationFunction(self):
        def creation_function(class_to_create, **kwargs):
            return "This doesn't even return an instance of {0}".format(class_to_create.__name__)

        class TestModelFactory(Factory):
            pass

        TestModelFactory.set_creation_function(creation_function)

        test_object = TestModelFactory.create()
        self.assertEqual(test_object, "This doesn't even return an instance of TestModel")

class FactoryDefaultStrategyTestCase(unittest.TestCase):
    def setUp(self):
        self.default_strategy = Factory.default_strategy

    def tearDown(self):
        Factory.default_strategy = self.default_strategy

    def testBuildStrategy(self):
        Factory.default_strategy = BUILD_STRATEGY

        class TestModelFactory(Factory):
            one = 'one'

        test_model = TestModelFactory()
        self.assertEqual(test_model.one, 'one')
        self.assertFalse(test_model.id)

    def testCreateStrategy(self):
        # Default default_strategy

        class TestModelFactory(Factory):
            one = 'one'

        test_model = TestModelFactory()
        self.assertEqual(test_model.one, 'one')
        self.assertTrue(test_model.id)

    def testSubFactory(self):
        class TestModel2(FakeDjangoModel):
            pass

        class TestModelFactory(Factory):
            FACTORY_FOR = TestModel
            one = 3

        class TestModel2Factory(Factory):
            FACTORY_FOR = TestModel2
            two = declarations.SubFactory(TestModelFactory, one=1)

        test_model = TestModel2Factory(two__one=4)
        self.assertEqual(4, test_model.two.one)
        self.assertEqual(1, test_model.id)
        self.assertEqual(1, test_model.two.id)

    def testSubFactoryWithLazyFields(self):
        class TestModel2(FakeDjangoModel):
            pass

        class TestModelFactory(Factory):
            FACTORY_FOR = TestModel

        class TestModel2Factory(Factory):
            FACTORY_FOR = TestModel2
            two = declarations.SubFactory(TestModelFactory,
                                          one=declarations.Sequence(lambda n: 'x%sx' % n),
                                          two=declarations.LazyAttribute(
                                              lambda o: '%s%s' % (o.one, o.one)))

        test_model = TestModel2Factory(one=42)
        self.assertEqual('x0x', test_model.two.one)
        self.assertEqual('x0xx0x', test_model.two.two)

    def testStubStrategy(self):
        Factory.default_strategy = STUB_STRATEGY

        class TestModelFactory(Factory):
            one = 'one'

        test_model = TestModelFactory()
        self.assertEqual(test_model.one, 'one')
        self.assertFalse(hasattr(test_model, 'id'))  # We should have a plain old object

    def testUnknownStrategy(self):
        Factory.default_strategy = 'unknown'

        class TestModelFactory(Factory):
            one = 'one'

        self.assertRaises(Factory.UnknownStrategy, TestModelFactory)

    def testStubWithNonStubStrategy(self):
        class TestModelFactory(StubFactory):
            one = 'one'

        TestModelFactory.default_strategy = CREATE_STRATEGY

        self.assertRaises(StubFactory.UnsupportedStrategy, TestModelFactory)

        TestModelFactory.default_strategy = BUILD_STRATEGY
        self.assertRaises(StubFactory.UnsupportedStrategy, TestModelFactory)

class FactoryCreationTestCase(unittest.TestCase):
    def testFactoryFor(self):
        class TestFactory(Factory):
            FACTORY_FOR = TestObject

        self.assertTrue(isinstance(TestFactory.build(), TestObject))

    def testAutomaticAssociatedClassDiscovery(self):
        class TestObjectFactory(Factory):
            pass

        self.assertTrue(isinstance(TestObjectFactory.build(), TestObject))

    def testStub(self):
        class TestFactory(StubFactory):
            pass

        self.assertEqual(TestFactory.default_strategy, STUB_STRATEGY)

    def testInheritanceWithStub(self):
        class TestObjectFactory(StubFactory):
            pass

        class TestFactory(TestObjectFactory):
            pass

        self.assertEqual(TestFactory.default_strategy, STUB_STRATEGY)

    def testCustomCreation(self):
        class TestModelFactory(Factory):
            @classmethod
            def _prepare(cls, create, **kwargs):
                kwargs['four'] = 4
                return super(TestModelFactory, cls)._prepare(create, **kwargs)

        b = TestModelFactory.build(one=1)
        self.assertEqual(1, b.one)
        self.assertEqual(4, b.four)
        self.assertEqual(None, b.id)

        c = TestModelFactory(one=1)
        self.assertEqual(1, c.one)
        self.assertEqual(4, c.four)
        self.assertEqual(1, c.id)

    # Errors

    def testNoAssociatedClassWithAutodiscovery(self):
        try:
            class TestFactory(Factory):
                pass
            self.fail()
        except Factory.AssociatedClassError as e:
            self.assertTrue('autodiscovery' in str(e))

    def testNoAssociatedClassWithoutAutodiscovery(self):
        try:
            class Test(Factory):
                pass
            self.fail()
        except Factory.AssociatedClassError as e:
            self.assertTrue('autodiscovery' not in str(e))

    def testInheritanceFromMoreThanOneFactory(self):
        class TestObjectFactory(StubFactory):
            pass

        class TestModelFactory(TestObjectFactory):
            pass

        try:
            class TestFactory(TestObjectFactory, TestModelFactory):
                pass
            self.fail()
        except RuntimeError as e:
            self.assertTrue('one Factory' in str(e))

if __name__ == '__main__':
    unittest.main()
