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

import datetime
import itertools

from factory import base
from factory import declarations
from factory import helpers

from .compat import mock, unittest
from . import tools


class OrderedDeclarationTestCase(unittest.TestCase):
    def test_errors(self):
        decl = declarations.OrderedDeclaration()
        self.assertRaises(NotImplementedError, decl.evaluate, None, {}, False)


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


class IteratorTestCase(unittest.TestCase):
    def test_cycle(self):
        it = declarations.Iterator([1, 2])
        self.assertEqual(1, it.evaluate(0, None, False))
        self.assertEqual(2, it.evaluate(1, None, False))
        self.assertEqual(1, it.evaluate(2, None, False))
        self.assertEqual(2, it.evaluate(3, None, False))

    def test_no_cycling(self):
        it = declarations.Iterator([1, 2], cycle=False)
        self.assertEqual(1, it.evaluate(0, None, False))
        self.assertEqual(2, it.evaluate(1, None, False))
        self.assertRaises(StopIteration, it.evaluate, 2, None, False)

    def test_reset_cycle(self):
        it = declarations.Iterator([1, 2])
        self.assertEqual(1, it.evaluate(0, None, False))
        self.assertEqual(2, it.evaluate(1, None, False))
        self.assertEqual(1, it.evaluate(2, None, False))
        self.assertEqual(2, it.evaluate(3, None, False))
        self.assertEqual(1, it.evaluate(4, None, False))
        it.reset()
        self.assertEqual(1, it.evaluate(5, None, False))
        self.assertEqual(2, it.evaluate(6, None, False))

    def test_reset_no_cycling(self):
        it = declarations.Iterator([1, 2], cycle=False)
        self.assertEqual(1, it.evaluate(0, None, False))
        self.assertEqual(2, it.evaluate(1, None, False))
        self.assertRaises(StopIteration, it.evaluate, 2, None, False)
        it.reset()
        self.assertEqual(1, it.evaluate(0, None, False))
        self.assertEqual(2, it.evaluate(1, None, False))
        self.assertRaises(StopIteration, it.evaluate, 2, None, False)

    def test_getter(self):
        it = declarations.Iterator([(1, 2), (1, 3)], getter=lambda p: p[1])
        self.assertEqual(2, it.evaluate(0, None, False))
        self.assertEqual(3, it.evaluate(1, None, False))
        self.assertEqual(2, it.evaluate(2, None, False))
        self.assertEqual(3, it.evaluate(3, None, False))


class PostGenerationDeclarationTestCase(unittest.TestCase):
    def test_extract_no_prefix(self):
        decl = declarations.PostGenerationDeclaration()

        context = decl.extract('foo',
                {'foo': 13, 'foo__bar': 42})
        self.assertTrue(context.did_extract)
        self.assertEqual(context.value, 13)
        self.assertEqual(context.extra, {'bar': 42})

    def test_decorator_simple(self):
        call_params = []
        @helpers.post_generation
        def foo(*args, **kwargs):
            call_params.append(args)
            call_params.append(kwargs)

        context = foo.extract('foo',
            {'foo': 13, 'foo__bar': 42, 'blah': 42, 'blah__baz': 1})
        self.assertTrue(context.did_extract)
        self.assertEqual(13, context.value)
        self.assertEqual({'bar': 42}, context.extra)

        # No value returned.
        foo.call(None, False, context)
        self.assertEqual(2, len(call_params))
        self.assertEqual((None, False, 13), call_params[0])
        self.assertEqual({'bar': 42}, call_params[1])


class FactoryWrapperTestCase(unittest.TestCase):
    def test_invalid_path(self):
        self.assertRaises(ValueError, declarations._FactoryWrapper, 'UnqualifiedSymbol')
        self.assertRaises(ValueError, declarations._FactoryWrapper, 42)

    def test_class(self):
        w = declarations._FactoryWrapper(datetime.date)
        self.assertEqual(datetime.date, w.get())

    def test_path(self):
        w = declarations._FactoryWrapper('datetime.date')
        self.assertEqual(datetime.date, w.get())

    def test_lazyness(self):
        f = declarations._FactoryWrapper('factory.declarations.Sequence')
        self.assertEqual(None, f.factory)

        factory_class = f.get()
        self.assertEqual(declarations.Sequence, factory_class)

    def test_cache(self):
        """Ensure that _FactoryWrapper tries to import only once."""
        orig_date = datetime.date
        w = declarations._FactoryWrapper('datetime.date')
        self.assertEqual(None, w.factory)

        factory_class = w.get()
        self.assertEqual(orig_date, factory_class)

        try:
            # Modify original value
            datetime.date = None
            # Repeat import
            factory_class = w.get()
            self.assertEqual(orig_date, factory_class)

        finally:
            # IMPORTANT: restore attribute.
            datetime.date = orig_date


class PostGenerationMethodCallTestCase(unittest.TestCase):
    def setUp(self):
        self.obj = mock.MagicMock()

    def ctx(self, value=None, force_value=False, extra=None):
        return declarations.ExtractionContext(
            value,
            bool(value) or force_value,
            extra,
        )

    def test_simplest_setup_and_call(self):
        decl = declarations.PostGenerationMethodCall('method')
        decl.call(self.obj, False, self.ctx())
        self.obj.method.assert_called_once_with()

    def test_call_with_method_args(self):
        decl = declarations.PostGenerationMethodCall(
                'method', 'data')
        decl.call(self.obj, False, self.ctx())
        self.obj.method.assert_called_once_with('data')

    def test_call_with_passed_extracted_string(self):
        decl = declarations.PostGenerationMethodCall(
                'method')
        decl.call(self.obj, False, self.ctx('data'))
        self.obj.method.assert_called_once_with('data')

    def test_call_with_passed_extracted_int(self):
        decl = declarations.PostGenerationMethodCall('method')
        decl.call(self.obj, False, self.ctx(1))
        self.obj.method.assert_called_once_with(1)

    def test_call_with_passed_extracted_iterable(self):
        decl = declarations.PostGenerationMethodCall('method')
        decl.call(self.obj, False, self.ctx((1, 2, 3)))
        self.obj.method.assert_called_once_with((1, 2, 3))

    def test_call_with_method_kwargs(self):
        decl = declarations.PostGenerationMethodCall(
                'method', data='data')
        decl.call(self.obj, False, self.ctx())
        self.obj.method.assert_called_once_with(data='data')

    def test_call_with_passed_kwargs(self):
        decl = declarations.PostGenerationMethodCall('method')
        decl.call(self.obj, False, self.ctx(extra={'data': 'other'}))
        self.obj.method.assert_called_once_with(data='other')

    def test_multi_call_with_multi_method_args(self):
        decl = declarations.PostGenerationMethodCall(
                'method', 'arg1', 'arg2')
        decl.call(self.obj, False, self.ctx())
        self.obj.method.assert_called_once_with('arg1', 'arg2')

    def test_multi_call_with_passed_multiple_args(self):
        decl = declarations.PostGenerationMethodCall(
                'method', 'arg1', 'arg2')
        decl.call(self.obj, False, self.ctx(('param1', 'param2', 'param3')))
        self.obj.method.assert_called_once_with('param1', 'param2', 'param3')

    def test_multi_call_with_passed_tuple(self):
        decl = declarations.PostGenerationMethodCall(
                'method', 'arg1', 'arg2')
        decl.call(self.obj, False, self.ctx((('param1', 'param2'),)))
        self.obj.method.assert_called_once_with(('param1', 'param2'))

    def test_multi_call_with_kwargs(self):
        decl = declarations.PostGenerationMethodCall(
                'method', 'arg1', 'arg2')
        decl.call(self.obj, False, self.ctx(extra={'x': 2}))
        self.obj.method.assert_called_once_with('arg1', 'arg2', x=2)


class PostGenerationOrdering(unittest.TestCase):

    def test_post_generation_declaration_order(self):
        postgen_results = []

        class Related(base.Factory):
            class Meta:
                model = mock.MagicMock()

        class Ordered(base.Factory):
            class Meta:
                model = mock.MagicMock()

            a = declarations.RelatedFactory(Related)
            z = declarations.RelatedFactory(Related)

            @helpers.post_generation
            def a1(*args, **kwargs):
                postgen_results.append('a1')

            @helpers.post_generation
            def zz(*args, **kwargs):
                postgen_results.append('zz')

            @helpers.post_generation
            def aa(*args, **kwargs):
                postgen_results.append('aa')

        postgen_names = [
            k for k, v in Ordered._meta.sorted_postgen_declarations
        ]
        self.assertEqual(postgen_names, ['a', 'z', 'a1', 'zz', 'aa'])

        # Test generation happens in desired order
        Ordered()
        self.assertEqual(postgen_results, ['a1', 'zz', 'aa'])


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
