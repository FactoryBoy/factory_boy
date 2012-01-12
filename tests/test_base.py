# -*- coding: utf-8 -*-
# Copyright (c) 2010 Mark Sandstrom
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

import unittest
import warnings

from factory import base
from factory import declarations

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
        self.assertRaises(RuntimeError, base.BaseFactory)


class FactoryTestCase(unittest.TestCase):
    def testDisplay(self):
        class TestObjectFactory(base.Factory):
            FACTORY_FOR = FakeDjangoModel

        self.assertIn('TestObjectFactory', str(TestObjectFactory))
        self.assertIn('FakeDjangoModel', str(TestObjectFactory))

    def testLazyAttributeNonExistentParam(self):
        class TestObjectFactory(base.Factory):
            one = declarations.LazyAttribute(lambda a: a.does_not_exist )

        self.assertRaises(AttributeError, TestObjectFactory)

    def testInheritanceWithSequence(self):
        """Tests that sequence IDs are shared between parent and son."""
        class TestObjectFactory(base.Factory):
            one = declarations.Sequence(lambda a: a)

        class TestSubFactory(TestObjectFactory):
            pass

        parent = TestObjectFactory.build()
        sub = TestSubFactory.build()
        alt_parent = TestObjectFactory.build()
        alt_sub = TestSubFactory.build()
        ones = set([x.one for x in (parent, alt_parent, sub, alt_sub)])
        self.assertEqual(4, len(ones))

class FactoryDefaultStrategyTestCase(unittest.TestCase):
    def setUp(self):
        self.default_strategy = base.Factory.default_strategy

    def tearDown(self):
        base.Factory.default_strategy = self.default_strategy

    def testBuildStrategy(self):
        base.Factory.default_strategy = base.BUILD_STRATEGY

        class TestModelFactory(base.Factory):
            one = 'one'

        test_model = TestModelFactory()
        self.assertEqual(test_model.one, 'one')
        self.assertFalse(test_model.id)

    def testCreateStrategy(self):
        # Default default_strategy

        class TestModelFactory(base.Factory):
            one = 'one'

        test_model = TestModelFactory()
        self.assertEqual(test_model.one, 'one')
        self.assertTrue(test_model.id)

    def testStubStrategy(self):
        base.Factory.default_strategy = base.STUB_STRATEGY

        class TestModelFactory(base.Factory):
            one = 'one'

        test_model = TestModelFactory()
        self.assertEqual(test_model.one, 'one')
        self.assertFalse(hasattr(test_model, 'id'))  # We should have a plain old object

    def testUnknownStrategy(self):
        base.Factory.default_strategy = 'unknown'

        class TestModelFactory(base.Factory):
            one = 'one'

        self.assertRaises(base.Factory.UnknownStrategy, TestModelFactory)

    def testStubWithNonStubStrategy(self):
        class TestModelFactory(base.StubFactory):
            one = 'one'

        TestModelFactory.default_strategy = base.CREATE_STRATEGY

        self.assertRaises(base.StubFactory.UnsupportedStrategy, TestModelFactory)

        TestModelFactory.default_strategy = base.BUILD_STRATEGY
        self.assertRaises(base.StubFactory.UnsupportedStrategy, TestModelFactory)

class FactoryCreationTestCase(unittest.TestCase):
    def testFactoryFor(self):
        class TestFactory(base.Factory):
            FACTORY_FOR = TestObject

        self.assertTrue(isinstance(TestFactory.build(), TestObject))

    def testAutomaticAssociatedClassDiscovery(self):
        class TestObjectFactory(base.Factory):
            pass

        self.assertTrue(isinstance(TestObjectFactory.build(), TestObject))

    def testDeprecationWarning(self):
        """Make sure the 'auto-discovery' deprecation warning is issued."""

        with warnings.catch_warnings(record=True) as w:
            # Clear the warning registry.
            if hasattr(base, '__warningregistry__'):
                base.__warningregistry__.clear()

            warnings.simplefilter('always')
            class TestObjectFactory(base.Factory):
                pass

            self.assertEqual(1, len(w))
            self.assertIn('deprecated', str(w[0].message))

    def testStub(self):
        class TestFactory(base.StubFactory):
            pass

        self.assertEqual(TestFactory.default_strategy, base.STUB_STRATEGY)

    def testInheritanceWithStub(self):
        class TestObjectFactory(base.StubFactory):
            pass

        class TestFactory(TestObjectFactory):
            pass

        self.assertEqual(TestFactory.default_strategy, base.STUB_STRATEGY)

    def testCustomCreation(self):
        class TestModelFactory(base.Factory):
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
            class TestFactory(base.Factory):
                pass
            self.fail()
        except base.Factory.AssociatedClassError as e:
            self.assertTrue('autodiscovery' in str(e))

    def testNoAssociatedClassWithoutAutodiscovery(self):
        try:
            class Test(base.Factory):
                pass
            self.fail()
        except base.Factory.AssociatedClassError as e:
            self.assertTrue('autodiscovery' not in str(e))


if __name__ == '__main__':
    unittest.main()
