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

from factory import base
from factory import containers
from factory import declarations

class LazyStubTestCase(unittest.TestCase):
    def test_basic(self):
        stub = containers.LazyStub({'one': 1, 'two': 2})

        self.assertEqual({'one': 1, 'two': 2}, stub.__fill__())

    def test_setting_values(self):
        stub = containers.LazyStub({'one': 1, 'two': 2})

        self.assertRaises(AttributeError, setattr, stub, 'one', 1)

    def test_reading_value(self):
        stub = containers.LazyStub({'one': 1, 'two': 2})
        self.assertEqual(1, stub.one)

        self.assertRaises(AttributeError, getattr, stub, 'three')

    def test_accessing_container(self):
        class LazyAttr(containers.LazyValue):
            def __init__(self, obj_attr, container_attr):
                self.obj_attr = obj_attr
                self.container_attr = container_attr

            def evaluate(self, obj, containers=()):
                if containers:
                    add = getattr(containers[0], self.container_attr)
                else:
                    add = 0
                return getattr(obj, self.obj_attr) + add

        class DummyContainer(object):
            three = 3

        stub = containers.LazyStub({'one': LazyAttr('two', 'three'), 'two': 2, 'three': 42},
            containers=(DummyContainer(),))

        self.assertEqual(5, stub.one)

        stub = containers.LazyStub({'one': LazyAttr('two', 'three'), 'two': 2, 'three': 42},
            containers=())
        self.assertEqual(2, stub.one)

    def test_cyclic_definition(self):
        class LazyAttr(containers.LazyValue):
            def __init__(self, attrname):
                self.attrname = attrname

            def evaluate(self, obj, container=None):
                return 1 + getattr(obj, self.attrname)

        stub = containers.LazyStub({'one': LazyAttr('two'), 'two': LazyAttr('one')})

        self.assertRaises(containers.CyclicDefinitionError, getattr, stub, 'one')

    def test_representation(self):
        class RandomObj(object):
            pass

        stub = containers.LazyStub({'one': 1, 'two': 2}, target_class=RandomObj)
        self.assertIn('RandomObj', repr(stub))
        self.assertIn('RandomObj', str(stub))
        self.assertIn('one', str(stub))


class OrderedDeclarationMock(declarations.OrderedDeclaration):
    pass


class DeclarationDictTestCase(unittest.TestCase):
    def test_basics(self):
        one = OrderedDeclarationMock()
        two = 2
        three = OrderedDeclarationMock()

        d = containers.DeclarationDict(dict(one=one, two=two, three=three))

        self.assertTrue('one' in d)
        self.assertTrue('two' in d)
        self.assertTrue('three' in d)

        self.assertEqual(one, d['one'])
        self.assertEqual(two, d['two'])
        self.assertEqual(three, d['three'])

        self.assertEqual(one, d.pop('one'))
        self.assertFalse('one' in d)

        d['one'] = one
        self.assertTrue('one' in d)
        self.assertEqual(one, d['one'])

        self.assertEqual(set(['one', 'two', 'three']),
                         set(d))

    def test_insert(self):
        one = OrderedDeclarationMock()
        two = 2
        three = OrderedDeclarationMock()
        four = OrderedDeclarationMock()

        d = containers.DeclarationDict(dict(one=one, two=two, four=four))

        self.assertEqual(set(['two', 'one', 'four']), set(d))

        d['three'] = three
        self.assertEqual(set(['two', 'one', 'three', 'four']), set(d))

    def test_replace(self):
        one = OrderedDeclarationMock()
        two = 2
        three = OrderedDeclarationMock()
        four = OrderedDeclarationMock()

        d = containers.DeclarationDict(dict(one=one, two=two, three=three))

        self.assertEqual(set(['two', 'one', 'three']), set(d))

        d['three'] = four
        self.assertEqual(set(['two', 'one', 'three']), set(d))
        self.assertEqual(set([two, one, four]), set(d.values()))

    def test_copy(self):
        one = OrderedDeclarationMock()
        two = 2
        three = OrderedDeclarationMock()
        four = OrderedDeclarationMock()

        d = containers.DeclarationDict(dict(one=one, two=two, three=three))
        d2 = d.copy({'five': 5})

        self.assertEqual(5, d2['five'])
        self.assertFalse('five' in d)

        d.pop('one')
        self.assertEqual(one, d2['one'])

        d2['two'] = four
        self.assertEqual(four, d2['two'])
        self.assertEqual(two, d['two'])

    def test_update_with_public(self):
        d = containers.DeclarationDict()
        d.update_with_public({
                'one': 1,
                '_two': 2,
                'three': 3,
                'classmethod': classmethod(lambda c: 1),
                'staticmethod': staticmethod(lambda: 1),
                })
        self.assertEqual(set(['one', 'three']), set(d))
        self.assertEqual(set([1, 3]), set(d.values()))


class AttributeBuilderTestCase(unittest.TestCase):
    def test_empty(self):
        """Tests building attributes from an empty definition."""

        class FakeFactory(object):
            @classmethod
            def declarations(cls, extra):
                return extra

            @classmethod
            def _generate_next_sequence(cls):
                return 1

        ab = containers.AttributeBuilder(FakeFactory)

        self.assertEqual({}, ab.build(create=False))

    def test_factory_defined(self):
        class FakeFactory(object):
            @classmethod
            def declarations(cls, extra):
                d = {'one': 1}
                d.update(extra)
                return d

            @classmethod
            def _generate_next_sequence(cls):
                return 1

        ab = containers.AttributeBuilder(FakeFactory)
        self.assertEqual({'one': 1}, ab.build(create=False))

    def test_extended(self):
        class FakeFactory(object):
            @classmethod
            def declarations(cls, extra):
                d = {'one': 1}
                d.update(extra)
                return d

            @classmethod
            def _generate_next_sequence(cls):
                return 1

        ab = containers.AttributeBuilder(FakeFactory, {'two': 2})
        self.assertEqual({'one': 1, 'two': 2}, ab.build(create=False))

    def test_overridden(self):
        class FakeFactory(object):
            @classmethod
            def declarations(cls, extra):
                d = {'one': 1}
                d.update(extra)
                return d

            @classmethod
            def _generate_next_sequence(cls):
                return 1

        ab = containers.AttributeBuilder(FakeFactory, {'one': 2})
        self.assertEqual({'one': 2}, ab.build(create=False))

    def test_factory_defined_sequence(self):
        seq = declarations.Sequence(lambda n: 'xx' + n)

        class FakeFactory(object):
            @classmethod
            def declarations(cls, extra):
                d = {'one': seq}
                d.update(extra)
                return d

            @classmethod
            def _generate_next_sequence(cls):
                return 1

        ab = containers.AttributeBuilder(FakeFactory)
        self.assertEqual({'one': 'xx1'}, ab.build(create=False))

    def test_additionnal_sequence(self):
        seq = declarations.Sequence(lambda n: 'xx' + n)

        class FakeFactory(object):
            @classmethod
            def declarations(cls, extra):
                d = {'one': 1}
                d.update(extra)
                return d

            @classmethod
            def _generate_next_sequence(cls):
                return 1

        ab = containers.AttributeBuilder(FakeFactory, extra={'two': seq})
        self.assertEqual({'one': 1, 'two': 'xx1'}, ab.build(create=False))

    def test_replaced_sequence(self):
        seq = declarations.Sequence(lambda n: 'xx' + n)
        seq2 = declarations.Sequence(lambda n: 'yy' + n)

        class FakeFactory(object):
            @classmethod
            def declarations(cls, extra):
                d = {'one': seq}
                d.update(extra)
                return d

            @classmethod
            def _generate_next_sequence(cls):
                return 1

        ab = containers.AttributeBuilder(FakeFactory, extra={'one': seq2})
        self.assertEqual({'one': 'yy1'}, ab.build(create=False))

    def test_lazy_attribute(self):
        la = declarations.LazyAttribute(lambda a: a.one * 2)

        class FakeFactory(object):
            @classmethod
            def declarations(cls, extra):
                d = containers.DeclarationDict({'one': 1, 'two': la})
                d.update(extra)
                return d

            @classmethod
            def _generate_next_sequence(cls):
                return 1

        ab = containers.AttributeBuilder(FakeFactory)
        self.assertEqual({'one': 1, 'two': 2}, ab.build(create=False))

        ab = containers.AttributeBuilder(FakeFactory, {'one': 4})
        self.assertEqual({'one': 4, 'two': 8}, ab.build(create=False))

        ab = containers.AttributeBuilder(FakeFactory, {'one': 4, 'three': la})
        self.assertEqual({'one': 4, 'two': 8, 'three': 8}, ab.build(create=False))

    def test_sub_factory(self):
        pass


if __name__ == '__main__':
    unittest.main()
