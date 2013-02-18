# -*- coding: utf-8 -*-
# Copyright (c) 2010 Mark Sandstrom
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

import datetime

from factory import declarations

from .compat import unittest

class OrderedDeclarationTestCase(unittest.TestCase):
    def test_errors(self):
        decl = declarations.OrderedDeclaration()
        self.assertRaises(NotImplementedError, decl.evaluate, None, {})


class DigTestCase(unittest.TestCase):
    class MyObj(object):
        def __init__(self, n):
            self.n = n

    def test_chaining(self):
        obj = self.MyObj(1)
        obj.a = self.MyObj(2)
        obj.a.b = self.MyObj(3)
        obj.a.b.c = self.MyObj(4)

        self.assertEqual(2, declarations.deepgetattr(obj, 'a').n)
        self.assertRaises(AttributeError, declarations.deepgetattr, obj, 'b')
        self.assertEqual(2, declarations.deepgetattr(obj, 'a.n'))
        self.assertEqual(3, declarations.deepgetattr(obj, 'a.c', 3))
        self.assertRaises(AttributeError, declarations.deepgetattr, obj, 'a.c.n')
        self.assertRaises(AttributeError, declarations.deepgetattr, obj, 'a.d')
        self.assertEqual(3, declarations.deepgetattr(obj, 'a.b').n)
        self.assertEqual(3, declarations.deepgetattr(obj, 'a.b.n'))
        self.assertEqual(4, declarations.deepgetattr(obj, 'a.b.c').n)
        self.assertEqual(4, declarations.deepgetattr(obj, 'a.b.c.n'))
        self.assertEqual(42, declarations.deepgetattr(obj, 'a.b.c.n.x', 42))


class SelfAttributeTestCase(unittest.TestCase):
    def test_standard(self):
        a = declarations.SelfAttribute('foo.bar.baz')
        self.assertEqual(0, a.depth)
        self.assertEqual('foo.bar.baz', a.attribute_name)
        self.assertEqual(declarations._UNSPECIFIED, a.default)

    def test_dot(self):
        a = declarations.SelfAttribute('.bar.baz')
        self.assertEqual(1, a.depth)
        self.assertEqual('bar.baz', a.attribute_name)
        self.assertEqual(declarations._UNSPECIFIED, a.default)

    def test_default(self):
        a = declarations.SelfAttribute('bar.baz', 42)
        self.assertEqual(0, a.depth)
        self.assertEqual('bar.baz', a.attribute_name)
        self.assertEqual(42, a.default)

    def test_parent(self):
        a = declarations.SelfAttribute('..bar.baz')
        self.assertEqual(2, a.depth)
        self.assertEqual('bar.baz', a.attribute_name)
        self.assertEqual(declarations._UNSPECIFIED, a.default)

    def test_grandparent(self):
        a = declarations.SelfAttribute('...bar.baz')
        self.assertEqual(3, a.depth)
        self.assertEqual('bar.baz', a.attribute_name)
        self.assertEqual(declarations._UNSPECIFIED, a.default)


class PostGenerationDeclarationTestCase(unittest.TestCase):
    def test_extract_no_prefix(self):
        decl = declarations.PostGenerationDeclaration()

        extracted, kwargs = decl.extract('foo', {'foo': 13, 'foo__bar': 42})
        self.assertEqual(extracted, 13)
        self.assertEqual(kwargs, {'bar': 42})

    def test_extract_with_prefix(self):
        decl = declarations.PostGenerationDeclaration(extract_prefix='blah')

        extracted, kwargs = decl.extract('foo',
            {'foo': 13, 'foo__bar': 42, 'blah': 42, 'blah__baz': 1})
        self.assertEqual(extracted, 42)
        self.assertEqual(kwargs, {'baz': 1})


class CircularSubFactoryTestCase(unittest.TestCase):
    def test_lazyness(self):
        f = declarations.CircularSubFactory('factory.declarations', 'Sequence', x=3)
        self.assertEqual(None, f.factory)

        self.assertEqual({'x': 3}, f.defaults)

        factory_class = f.get_factory()
        self.assertEqual(declarations.Sequence, factory_class)

    def test_cache(self):
        orig_date = datetime.date
        f = declarations.CircularSubFactory('datetime', 'date')
        self.assertEqual(None, f.factory)

        factory_class = f.get_factory()
        self.assertEqual(orig_date, factory_class)

        try:
            # Modify original value
            datetime.date = None
            # Repeat import
            factory_class = f.get_factory()
            self.assertEqual(orig_date, factory_class)

        finally:
            # IMPORTANT: restore attribute.
            datetime.date = orig_date


class FuzzyAttributeTestCase(unittest.TestCase):
    def test_lookup_by_name(self):
        choices = ('Bill', 'Jim', 'Tom',)
        f = declarations.FuzzyAttribute('choice', choices)
        self.assertIn(f.evaluate(0, None), choices)

    def test_pass_in_callable(self):
        import random
        value_range = (1, 10,)
        f = declarations.FuzzyAttribute(random.randint, *value_range)
        self.assertIn(f.evaluate(0, None), range(11))


if __name__ == '__main__':
    unittest.main()
