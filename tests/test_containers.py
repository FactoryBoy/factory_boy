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
from factory import errors

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

    class LazyAttr(containers.LazyValue):
        def __init__(self, attrname):
            self.attrname = attrname

        def evaluate(self, obj, container=None):
            return 1 + getattr(obj, self.attrname)

    def test_cyclic_definition(self):
        stub = containers.LazyStub({
            'one': self.LazyAttr('two'),
            'two': self.LazyAttr('one'),
        })

        self.assertRaises(errors.CyclicDefinitionError, getattr, stub, 'one')

    def test_cyclic_definition_rescue(self):
        class LazyAttrDefault(self.LazyAttr):
            def __init__(self, attname, defvalue):
                super(LazyAttrDefault, self).__init__(attname)
                self.defvalue = defvalue
            def evaluate(self, obj, container=None):
                try:
                    return super(LazyAttrDefault, self).evaluate(obj, container)
                except errors.CyclicDefinitionError:
                    return self.defvalue

        stub = containers.LazyStub({
            'one': LazyAttrDefault('two', 10),
            'two': self.LazyAttr('one'),
        })

        self.assertEqual(10, stub.one)
        self.assertEqual(11, stub.two)

    def test_representation(self):
        class RandomObj(object):
            pass

        stub = containers.LazyStub({'one': 1, 'two': 2}, model_class=RandomObj)
        self.assertIn('RandomObj', repr(stub))
        self.assertIn('RandomObj', str(stub))
        self.assertIn('one', str(stub))



class AttributeBuilderTestCase(unittest.TestCase):

    def make_fake_factory(self, decls):
        class Meta:
            declarations = decls
            parameters = {}
            parameters_dependencies = {}

        class FakeFactory(object):
            _meta = Meta

            @classmethod
            def _generate_next_sequence(cls):
                return 1

        return FakeFactory

    def test_empty(self):
        """Tests building attributes from an empty definition."""

        FakeFactory = self.make_fake_factory({})
        ab = containers.AttributeBuilder(FakeFactory)

        self.assertEqual({}, ab.build(create=False))

    def test_factory_defined(self):
        FakeFactory = self.make_fake_factory({'one': 1})
        ab = containers.AttributeBuilder(FakeFactory)

        self.assertEqual({'one': 1}, ab.build(create=False))

    def test_extended(self):
        FakeFactory = self.make_fake_factory({'one': 1})
        ab = containers.AttributeBuilder(FakeFactory, {'two': 2})
        self.assertEqual({'one': 1, 'two': 2}, ab.build(create=False))

    def test_overridden(self):
        FakeFactory = self.make_fake_factory({'one': 1})
        ab = containers.AttributeBuilder(FakeFactory, {'one': 2})
        self.assertEqual({'one': 2}, ab.build(create=False))

    def test_factory_defined_sequence(self):
        seq = declarations.Sequence(lambda n: 'xx%d' % n)
        FakeFactory = self.make_fake_factory({'one': seq})

        ab = containers.AttributeBuilder(FakeFactory)
        self.assertEqual({'one': 'xx1'}, ab.build(create=False))

    def test_additionnal_sequence(self):
        seq = declarations.Sequence(lambda n: 'xx%d' % n)
        FakeFactory = self.make_fake_factory({'one': 1})

        ab = containers.AttributeBuilder(FakeFactory, extra={'two': seq})
        self.assertEqual({'one': 1, 'two': 'xx1'}, ab.build(create=False))

    def test_replaced_sequence(self):
        seq = declarations.Sequence(lambda n: 'xx%d' % n)
        seq2 = declarations.Sequence(lambda n: 'yy%d' % n)
        FakeFactory = self.make_fake_factory({'one': seq})

        ab = containers.AttributeBuilder(FakeFactory, extra={'one': seq2})
        self.assertEqual({'one': 'yy1'}, ab.build(create=False))

    def test_lazy_function(self):
        lf = declarations.LazyFunction(int)
        FakeFactory = self.make_fake_factory({'one': 1, 'two': lf})

        ab = containers.AttributeBuilder(FakeFactory)
        self.assertEqual({'one': 1, 'two': 0}, ab.build(create=False))

        ab = containers.AttributeBuilder(FakeFactory, {'one': 4})
        self.assertEqual({'one': 4, 'two': 0}, ab.build(create=False))

        ab = containers.AttributeBuilder(FakeFactory, {'one': 4, 'three': lf})
        self.assertEqual({'one': 4, 'two': 0, 'three': 0}, ab.build(create=False))

    def test_lazy_attribute(self):
        la = declarations.LazyAttribute(lambda a: a.one * 2)
        FakeFactory = self.make_fake_factory({'one': 1, 'two': la})

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
        FakeFactory = self.make_fake_factory({'one': sf, 'two': 2})

        ab = containers.AttributeBuilder(FakeFactory, {'one__blah': 1, 'two__bar': 2})
        self.assertTrue(ab.has_subfields(sf))
        self.assertEqual(['one'], list(ab._subfields.keys()))
        self.assertEqual(2, ab._declarations['two__bar'])

    def test_sub_factory(self):
        pass


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
