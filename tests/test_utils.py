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

from __future__ import unicode_literals


import itertools

from factory import utils

from .compat import is_python2, unittest


class ExtractDictTestCase(unittest.TestCase):
    def test_empty_dict(self):
        self.assertEqual({}, utils.extract_dict('foo', {}))

    def test_unused_key(self):
        self.assertEqual({}, utils.extract_dict('foo', {'bar__baz': 42}))

    def test_empty_key(self):
        self.assertEqual({}, utils.extract_dict('', {'foo': 13, 'bar__baz': 42}))
        d = {'foo': 13, 'bar__baz': 42, '__foo': 1}
        self.assertEqual({'foo': 1}, utils.extract_dict('', d))
        self.assertNotIn('__foo', d)

    def test_one_key(self):
        d = {'foo': 13, 'foo__baz': 42, '__foo': 1}
        self.assertEqual({'baz': 42}, utils.extract_dict('foo', d, pop=False))
        self.assertEqual(42, d['foo__baz'])

        self.assertEqual({'baz': 42}, utils.extract_dict('foo', d, pop=True))
        self.assertNotIn('foo__baz', d)

    def test_one_key_excluded(self):
        d = {'foo': 13, 'foo__baz': 42, '__foo': 1}
        self.assertEqual({},
            utils.extract_dict('foo', d, pop=False, exclude=('foo__baz',)))
        self.assertEqual(42, d['foo__baz'])

        self.assertEqual({},
            utils.extract_dict('foo', d, pop=True, exclude=('foo__baz',)))
        self.assertIn('foo__baz', d)

    def test_many_keys(self):
        d = {'foo': 13, 'foo__baz': 42, 'foo__foo__bar': 2, 'foo__bar': 3, '__foo': 1}
        self.assertEqual({'foo__bar': 2, 'bar': 3, 'baz': 42},
            utils.extract_dict('foo', d, pop=False))
        self.assertEqual(42, d['foo__baz'])
        self.assertEqual(3, d['foo__bar'])
        self.assertEqual(2, d['foo__foo__bar'])

        self.assertEqual({'foo__bar': 2, 'bar': 3, 'baz': 42},
            utils.extract_dict('foo', d, pop=True))
        self.assertNotIn('foo__baz', d)
        self.assertNotIn('foo__bar', d)
        self.assertNotIn('foo__foo__bar', d)

    def test_many_keys_excluded(self):
        d = {'foo': 13, 'foo__baz': 42, 'foo__foo__bar': 2, 'foo__bar': 3, '__foo': 1}
        self.assertEqual({'foo__bar': 2, 'baz': 42},
            utils.extract_dict('foo', d, pop=False, exclude=('foo__bar', 'bar')))
        self.assertEqual(42, d['foo__baz'])
        self.assertEqual(3, d['foo__bar'])
        self.assertEqual(2, d['foo__foo__bar'])

        self.assertEqual({'foo__bar': 2, 'baz': 42},
            utils.extract_dict('foo', d, pop=True, exclude=('foo__bar', 'bar')))
        self.assertNotIn('foo__baz', d)
        self.assertIn('foo__bar', d)
        self.assertNotIn('foo__foo__bar', d)


class MultiExtractDictTestCase(unittest.TestCase):
    def test_empty_dict(self):
        self.assertEqual({'foo': {}}, utils.multi_extract_dict(['foo'], {}))

    def test_unused_key(self):
        self.assertEqual({'foo': {}},
            utils.multi_extract_dict(['foo'], {'bar__baz': 42}))
        self.assertEqual({'foo': {}, 'baz': {}},
            utils.multi_extract_dict(['foo', 'baz'], {'bar__baz': 42}))

    def test_no_key(self):
        self.assertEqual({}, utils.multi_extract_dict([], {'bar__baz': 42}))

    def test_empty_key(self):
        self.assertEqual({'': {}},
            utils.multi_extract_dict([''], {'foo': 13, 'bar__baz': 42}))

        d = {'foo': 13, 'bar__baz': 42, '__foo': 1}
        self.assertEqual({'': {'foo': 1}},
            utils.multi_extract_dict([''], d))
        self.assertNotIn('__foo', d)

    def test_one_extracted(self):
        d = {'foo': 13, 'foo__baz': 42, '__foo': 1}
        self.assertEqual({'foo': {'baz': 42}},
            utils.multi_extract_dict(['foo'], d, pop=False))
        self.assertEqual(42, d['foo__baz'])

        self.assertEqual({'foo': {'baz': 42}},
            utils.multi_extract_dict(['foo'], d, pop=True))
        self.assertNotIn('foo__baz', d)

    def test_many_extracted(self):
        d = {'foo': 13, 'foo__baz': 42, 'foo__foo__bar': 2, 'foo__bar': 3, '__foo': 1}
        self.assertEqual({'foo': {'foo__bar': 2, 'bar': 3, 'baz': 42}},
            utils.multi_extract_dict(['foo'], d, pop=False))
        self.assertEqual(42, d['foo__baz'])
        self.assertEqual(3, d['foo__bar'])
        self.assertEqual(2, d['foo__foo__bar'])

        self.assertEqual({'foo': {'foo__bar': 2, 'bar': 3, 'baz': 42}},
            utils.multi_extract_dict(['foo'], d, pop=True))
        self.assertNotIn('foo__baz', d)
        self.assertNotIn('foo__bar', d)
        self.assertNotIn('foo__foo__bar', d)

    def test_many_keys_one_extracted(self):
        d = {'foo': 13, 'foo__baz': 42, '__foo': 1}
        self.assertEqual({'foo': {'baz': 42}, 'baz': {}},
            utils.multi_extract_dict(['foo', 'baz'], d, pop=False))
        self.assertEqual(42, d['foo__baz'])

        self.assertEqual({'foo': {'baz': 42}, 'baz': {}},
            utils.multi_extract_dict(['foo', 'baz'], d, pop=True))
        self.assertNotIn('foo__baz', d)

    def test_many_keys_many_extracted(self):
        d = {
            'foo': 13,
            'foo__baz': 42, 'foo__foo__bar': 2, 'foo__bar': 3,
            'bar__foo': 1, 'bar__bar__baz': 4,
        }

        self.assertEqual(
            {
                'foo': {'foo__bar': 2, 'bar': 3, 'baz': 42},
                'bar': {'foo': 1, 'bar__baz': 4},
                'baz': {}
            },
            utils.multi_extract_dict(['foo', 'bar', 'baz'], d, pop=False))
        self.assertEqual(42, d['foo__baz'])
        self.assertEqual(3, d['foo__bar'])
        self.assertEqual(2, d['foo__foo__bar'])
        self.assertEqual(1, d['bar__foo'])
        self.assertEqual(4, d['bar__bar__baz'])

        self.assertEqual(
            {
                'foo': {'foo__bar': 2, 'bar': 3, 'baz': 42},
                'bar': {'foo': 1, 'bar__baz': 4},
                'baz': {}
            },
            utils.multi_extract_dict(['foo', 'bar', 'baz'], d, pop=True))
        self.assertNotIn('foo__baz', d)
        self.assertNotIn('foo__bar', d)
        self.assertNotIn('foo__foo__bar', d)
        self.assertNotIn('bar__foo', d)
        self.assertNotIn('bar__bar__baz', d)

    def test_son_in_list(self):
        """Make sure that prefixes are used in decreasing match length order."""
        d = {
            'foo': 13,
            'foo__baz': 42, 'foo__foo__bar': 2, 'foo__bar': 3,
            'bar__foo': 1, 'bar__bar__baz': 4,
        }

        self.assertEqual(
            {
                'foo__foo': {'bar': 2},
                'foo': {'bar': 3, 'baz': 42},
                'bar__bar': {'baz': 4},
                'bar': {'foo': 1},
                'baz': {}
            },
            utils.multi_extract_dict(
                ['foo', 'bar', 'baz', 'foo__foo', 'bar__bar'], d, pop=False))
        self.assertEqual(42, d['foo__baz'])
        self.assertEqual(3, d['foo__bar'])
        self.assertEqual(2, d['foo__foo__bar'])
        self.assertEqual(1, d['bar__foo'])
        self.assertEqual(4, d['bar__bar__baz'])

        self.assertEqual(
            {
                'foo__foo': {'bar': 2},
                'foo': {'bar': 3, 'baz': 42},
                'bar__bar': {'baz': 4},
                'bar': {'foo': 1},
                'baz': {}
            },
            utils.multi_extract_dict(
                ['foo', 'bar', 'baz', 'foo__foo', 'bar__bar'], d, pop=True))
        self.assertNotIn('foo__baz', d)
        self.assertNotIn('foo__bar', d)
        self.assertNotIn('foo__foo__bar', d)
        self.assertNotIn('bar__foo', d)
        self.assertNotIn('bar__bar__baz', d)


class ImportObjectTestCase(unittest.TestCase):
    def test_datetime(self):
        imported = utils.import_object('datetime', 'date')
        import datetime
        d = datetime.date
        self.assertEqual(d, imported)

    def test_unknown_attribute(self):
        self.assertRaises(AttributeError, utils.import_object,
            'datetime', 'foo')

    def test_invalid_module(self):
        self.assertRaises(ImportError, utils.import_object,
            'this-is-an-invalid-module', '__name__')


class LogPPrintTestCase(unittest.TestCase):
    def test_nothing(self):
        txt = str(utils.log_pprint())
        self.assertEqual('', txt)

    def test_only_args(self):
        txt = str(utils.log_pprint((1, 2, 3)))
        self.assertEqual('1, 2, 3', txt)

    def test_only_kwargs(self):
        txt = str(utils.log_pprint(kwargs={'a': 1, 'b': 2}))
        self.assertIn(txt, ['a=1, b=2', 'b=2, a=1'])

    def test_bytes_args(self):
        txt = str(utils.log_pprint((b'\xe1\xe2',)))
        expected = "b'\\xe1\\xe2'"
        if is_python2:
            expected = expected.lstrip('b')
        self.assertEqual(expected, txt)

    def test_text_args(self):
        txt = str(utils.log_pprint(('ŧêßŧ',)))
        expected = "'ŧêßŧ'"
        if is_python2:
            expected = "u'\\u0167\\xea\\xdf\\u0167'"
        self.assertEqual(expected, txt)

    def test_bytes_kwargs(self):
        txt = str(utils.log_pprint(kwargs={'x': b'\xe1\xe2', 'y': b'\xe2\xe1'}))
        expected1 = "x=b'\\xe1\\xe2', y=b'\\xe2\\xe1'"
        expected2 = "y=b'\\xe2\\xe1', x=b'\\xe1\\xe2'"
        if is_python2:
            expected1 = expected1.replace('b', '')
            expected2 = expected2.replace('b', '')
        self.assertIn(txt, (expected1, expected2))

    def test_text_kwargs(self):
        txt = str(utils.log_pprint(kwargs={'x': 'ŧêßŧ', 'y': 'ŧßêŧ'}))
        expected1 = "x='ŧêßŧ', y='ŧßêŧ'"
        expected2 = "y='ŧßêŧ', x='ŧêßŧ'"
        if is_python2:
            expected1 = "x=u'\\u0167\\xea\\xdf\\u0167', y=u'\\u0167\\xdf\\xea\\u0167'"
            expected2 = "y=u'\\u0167\\xdf\\xea\\u0167', x=u'\\u0167\\xea\\xdf\\u0167'"
        self.assertIn(txt, (expected1, expected2))


class ResetableIteratorTestCase(unittest.TestCase):
    def test_no_reset(self):
        i = utils.ResetableIterator([1, 2, 3])
        self.assertEqual([1, 2, 3], list(i))

    def test_no_reset_new_iterator(self):
        i = utils.ResetableIterator([1, 2, 3])
        iterator = iter(i)
        self.assertEqual(1, next(iterator))
        self.assertEqual(2, next(iterator))

        iterator2 = iter(i)
        self.assertEqual(3, next(iterator2))

    def test_infinite(self):
        i = utils.ResetableIterator(itertools.cycle([1, 2, 3]))
        iterator = iter(i)
        values = [next(iterator) for _i in range(10)]
        self.assertEqual([1, 2, 3, 1, 2, 3, 1, 2, 3, 1], values)

    def test_reset_simple(self):
        i = utils.ResetableIterator([1, 2, 3])
        iterator = iter(i)
        self.assertEqual(1, next(iterator))
        self.assertEqual(2, next(iterator))

        i.reset()
        self.assertEqual(1, next(iterator))
        self.assertEqual(2, next(iterator))
        self.assertEqual(3, next(iterator))

    def test_reset_at_begin(self):
        i = utils.ResetableIterator([1, 2, 3])
        iterator = iter(i)
        i.reset()
        i.reset()
        self.assertEqual(1, next(iterator))
        self.assertEqual(2, next(iterator))
        self.assertEqual(3, next(iterator))

    def test_reset_at_end(self):
        i = utils.ResetableIterator([1, 2, 3])
        iterator = iter(i)
        self.assertEqual(1, next(iterator))
        self.assertEqual(2, next(iterator))
        self.assertEqual(3, next(iterator))

        i.reset()
        self.assertEqual(1, next(iterator))
        self.assertEqual(2, next(iterator))
        self.assertEqual(3, next(iterator))

    def test_reset_after_end(self):
        i = utils.ResetableIterator([1, 2, 3])
        iterator = iter(i)
        self.assertEqual(1, next(iterator))
        self.assertEqual(2, next(iterator))
        self.assertEqual(3, next(iterator))
        self.assertRaises(StopIteration, next, iterator)

        i.reset()
        # Previous iter() has stopped
        iterator = iter(i)
        self.assertEqual(1, next(iterator))
        self.assertEqual(2, next(iterator))
        self.assertEqual(3, next(iterator))

    def test_reset_twice(self):
        i = utils.ResetableIterator([1, 2, 3, 4, 5])
        iterator = iter(i)
        self.assertEqual(1, next(iterator))
        self.assertEqual(2, next(iterator))

        i.reset()
        self.assertEqual(1, next(iterator))
        self.assertEqual(2, next(iterator))
        self.assertEqual(3, next(iterator))
        self.assertEqual(4, next(iterator))

        i.reset()
        self.assertEqual(1, next(iterator))
        self.assertEqual(2, next(iterator))
        self.assertEqual(3, next(iterator))
        self.assertEqual(4, next(iterator))

    def test_reset_shorter(self):
        i = utils.ResetableIterator([1, 2, 3, 4, 5])
        iterator = iter(i)
        self.assertEqual(1, next(iterator))
        self.assertEqual(2, next(iterator))
        self.assertEqual(3, next(iterator))
        self.assertEqual(4, next(iterator))

        i.reset()
        self.assertEqual(1, next(iterator))
        self.assertEqual(2, next(iterator))

        i.reset()
        self.assertEqual(1, next(iterator))
        self.assertEqual(2, next(iterator))
        self.assertEqual(3, next(iterator))
        self.assertEqual(4, next(iterator))

