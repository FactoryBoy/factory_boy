# -*- coding: utf-8 -*-
# Copyright (c) 2010 Mark Sandstrom
# Copyright (c) 2011-2015 Raphaël Barrois
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

from factory import base
from factory import containers
from factory import declarations

from .compat import unittest

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

    def test_access_parent(self):
        """Test simple access to a stub' parent."""
        o1 = containers.LazyStub({'rank': 1})
        o2 = containers.LazyStub({'rank': 2}, (o1,))
        stub = containers.LazyStub({'rank': 3}, (o2, o1))

        self.assertEqual(3, stub.rank)
        self.assertEqual(2, stub.factory_parent.rank)
        self.assertEqual(1, stub.factory_parent.factory_parent.rank)

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

        stub = containers.LazyStub({'one': 1, 'two': 2}, model_class=RandomObj)
        self.assertIn('RandomObj', repr(stub))
        self.assertIn('RandomObj', str(stub))
        self.assertIn('one', str(stub))



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
        seq = declarations.Sequence(lambda n: 'xx%d' % n)

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
        seq = declarations.Sequence(lambda n: 'xx%d' % n)

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
        seq = declarations.Sequence(lambda n: 'xx%d' % n)
        seq2 = declarations.Sequence(lambda n: 'yy%d' % n)

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
                d = {'one': 1, 'two': la}
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

    def test_subfields(self):
        class FakeInnerFactory(object):
            pass

        sf = declarations.SubFactory(FakeInnerFactory)

        class FakeFactory(object):
            @classmethod
            def declarations(cls, extra):
                d = {'one': sf, 'two': 2}
                d.update(extra)
                return d

        ab = containers.AttributeBuilder(FakeFactory, {'one__blah': 1, 'two__bar': 2})
        self.assertTrue(ab.has_subfields(sf))
        self.assertEqual(['one'], list(ab._subfields.keys()))
        self.assertEqual(2, ab._attrs['two__bar'])

    def test_sub_factory(self):
        pass


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
