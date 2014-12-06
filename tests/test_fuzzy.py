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
import decimal
import collections

from factory import compat
from factory import fuzzy
from factory import base
from factory import declarations

from .compat import mock, unittest
from . import utils


class FuzzyAttributeTestCase(unittest.TestCase):
    def test_simple_call(self):
        d = fuzzy.FuzzyAttribute(lambda: 10)

        res = d.evaluate(2, None, False)
        self.assertEqual(10, res)

        res = d.evaluate(2, None, False)
        self.assertEqual(10, res)


class FuzzyChoiceTestCase(unittest.TestCase):
    def test_unbiased(self):
        options = [1, 2, 3]
        d = fuzzy.FuzzyChoice(options)
        res = d.evaluate(2, None, False)
        self.assertIn(res, options)

    def test_mock(self):
        options = [1, 2, 3]
        fake_choice = lambda d: sum(d)

        d = fuzzy.FuzzyChoice(options)

        with mock.patch('random.choice', fake_choice):
            res = d.evaluate(2, None, False)

        self.assertEqual(6, res)

    def test_generator(self):
        def options():
            for i in range(3):
                yield i

        d = fuzzy.FuzzyChoice(options())

        res = d.evaluate(2, None, False)
        self.assertIn(res, [0, 1, 2])

        # And repeat
        res = d.evaluate(2, None, False)
        self.assertIn(res, [0, 1, 2])

    def test_lazy(self):
        options = [1, 2, 3]
        fake_choice = lambda d: sum(d)

        fuzz = fuzzy.FuzzyChoice(choices=declarations.SelfAttribute('choices'))

        class FooFactory(base.Factory):
            FACTORY_FOR = collections.namedtuple(
                'Foo', 'choices')

            choices = options

        with mock.patch('random.choice', fake_choice):
            res = fuzz.evaluate(2, FooFactory(), False)

        self.assertEqual(6, res)


class FuzzyIntegerTestCase(unittest.TestCase):
    def test_definition(self):
        """Tests all ways of defining a FuzzyInteger."""
        fuzz = fuzzy.FuzzyInteger(2, 3)
        for _i in range(20):
            res = fuzz.evaluate(2, None, False)
            self.assertIn(res, [2, 3])

        fuzz = fuzzy.FuzzyInteger(4)
        for _i in range(20):
            res = fuzz.evaluate(2, None, False)
            self.assertIn(res, [0, 1, 2, 3, 4])

    def test_biased(self):
        fake_randrange = lambda low, high, step: (low + high) * step

        fuzz = fuzzy.FuzzyInteger(2, 8)

        with mock.patch('random.randrange', fake_randrange):
            res = fuzz.evaluate(2, None, False)

        self.assertEqual((2 + 8 + 1) * 1, res)

    def test_biased_high_only(self):
        fake_randrange = lambda low, high, step: (low + high) * step

        fuzz = fuzzy.FuzzyInteger(8)

        with mock.patch('random.randrange', fake_randrange):
            res = fuzz.evaluate(2, None, False)

        self.assertEqual((0 + 8 + 1) * 1, res)

    def test_biased_with_step(self):
        fake_randrange = lambda low, high, step: (low + high) * step

        fuzz = fuzzy.FuzzyInteger(5, 8, 3)

        with mock.patch('random.randrange', fake_randrange):
            res = fuzz.evaluate(2, None, False)

        self.assertEqual((5 + 8 + 1) * 3, res)

    def test_lazy(self):
        fake_randrange = lambda low, high, step: (low + high) * step

        fuzz = fuzzy.FuzzyInteger(low=declarations.SelfAttribute('low'),
                                  high=declarations.SelfAttribute('high'),
                                  step=declarations.SelfAttribute('step'))

        class FooFactory(base.Factory):
            FACTORY_FOR = collections.namedtuple(
                'Foo', 'low high step')

            low = 5
            high = 8
            step = 3

        with mock.patch('random.randrange', fake_randrange):
            res = fuzz.evaluate(2, FooFactory(), False)

        self.assertEqual((5 + 8 + 1) * 3, res)


class FuzzyDecimalTestCase(unittest.TestCase):
    def test_definition(self):
        """Tests all ways of defining a FuzzyDecimal."""
        fuzz = fuzzy.FuzzyDecimal(2.0, 3.0)
        for _i in range(20):
            res = fuzz.evaluate(2, None, False)
            self.assertTrue(decimal.Decimal('2.0') <= res <= decimal.Decimal('3.0'),
                    "value %d is not between 2.0 and 3.0" % res)

        fuzz = fuzzy.FuzzyDecimal(4.0)
        for _i in range(20):
            res = fuzz.evaluate(2, None, False)
            self.assertTrue(decimal.Decimal('0.0') <= res <= decimal.Decimal('4.0'),
                    "value %d is not between 0.0 and 4.0" % res)

        fuzz = fuzzy.FuzzyDecimal(1.0, 4.0, precision=5)
        for _i in range(20):
            res = fuzz.evaluate(2, None, False)
            self.assertTrue(decimal.Decimal('0.54') <= res <= decimal.Decimal('4.0'),
                    "value %d is not between 0.54 and 4.0" % res)
            self.assertTrue(res.as_tuple().exponent, -5)

    def test_biased(self):
        fake_uniform = lambda low, high: low + high

        fuzz = fuzzy.FuzzyDecimal(2.0, 8.0)

        with mock.patch('random.uniform', fake_uniform):
            res = fuzz.evaluate(2, None, False)

        self.assertEqual(decimal.Decimal('10.0'), res)

    def test_biased_high_only(self):
        fake_uniform = lambda low, high: low + high

        fuzz = fuzzy.FuzzyDecimal(8.0)

        with mock.patch('random.uniform', fake_uniform):
            res = fuzz.evaluate(2, None, False)

        self.assertEqual(decimal.Decimal('8.0'), res)

    def test_precision(self):
        fake_uniform = lambda low, high: low + high + 0.001

        fuzz = fuzzy.FuzzyDecimal(8.0, precision=3)

        with mock.patch('random.uniform', fake_uniform):
            res = fuzz.evaluate(2, None, False)

        self.assertEqual(decimal.Decimal('8.001').quantize(decimal.Decimal(10) ** -3), res)

    def test_lazy(self):
        fake_uniform = lambda low, high: low + high + 0.001

        fuzz = fuzzy.FuzzyDecimal(
            low=declarations.SelfAttribute('low'),
            high=declarations.SelfAttribute('high'),
            precision=declarations.SelfAttribute('precision'))

        class FooFactory(base.Factory):
            FACTORY_FOR = collections.namedtuple(
                'Foo', 'low high precision')

            low = 0.0
            high = 8.0
            precision = 3

        with mock.patch('random.uniform', fake_uniform):
            res = fuzz.evaluate(2, FooFactory(), False)

        self.assertEqual(decimal.Decimal('8.001').quantize(decimal.Decimal(10) ** -3), res)


class FuzzyDateTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Setup useful constants
        cls.jan1 = datetime.date(2013, 1, 1)
        cls.jan3 = datetime.date(2013, 1, 3)
        cls.jan31 = datetime.date(2013, 1, 31)

    def test_accurate_definition(self):
        """Tests all ways of defining a FuzzyDate."""
        fuzz = fuzzy.FuzzyDate(self.jan1, self.jan31)

        for _i in range(20):
            res = fuzz.evaluate(2, None, False)
            self.assertLessEqual(self.jan1, res)
            self.assertLessEqual(res, self.jan31)

    def test_partial_definition(self):
        """Test defining a FuzzyDate without passing an end date."""
        with utils.mocked_date_today(self.jan3, fuzzy):
            fuzz = fuzzy.FuzzyDate(self.jan1)

        for _i in range(20):
            res = fuzz.evaluate(2, None, False)
            self.assertLessEqual(self.jan1, res)
            self.assertLessEqual(res, self.jan3)

    def test_invalid_definition(self):
        fuzz = fuzzy.FuzzyDate(self.jan31, self.jan1)
        self.assertRaises(ValueError, fuzz.fuzz)

    def test_invalid_partial_definition(self):
        with utils.mocked_date_today(self.jan1, fuzzy):
            fuzz = fuzzy.FuzzyDate(self.jan31)
            self.assertRaises(ValueError, fuzz.fuzz)

    def test_biased(self):
        """Tests a FuzzyDate with a biased random.randint."""

        fake_randint = lambda low, high: (low + high) // 2
        fuzz = fuzzy.FuzzyDate(self.jan1, self.jan31)

        with mock.patch('random.randint', fake_randint):
            res = fuzz.evaluate(2, None, False)

        self.assertEqual(datetime.date(2013, 1, 16), res)

    def test_biased_partial(self):
        """Tests a FuzzyDate with a biased random and implicit upper bound."""
        with utils.mocked_date_today(self.jan3, fuzzy):
            fuzz = fuzzy.FuzzyDate(self.jan1)

        fake_randint = lambda low, high: (low + high) // 2
        with mock.patch('random.randint', fake_randint):
            res = fuzz.evaluate(2, None, False)

        self.assertEqual(datetime.date(2013, 1, 2), res)


class FuzzyNaiveDateTimeTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Setup useful constants
        cls.jan1 = datetime.datetime(2013, 1, 1)
        cls.jan3 = datetime.datetime(2013, 1, 3)
        cls.jan31 = datetime.datetime(2013, 1, 31)

    def test_accurate_definition(self):
        """Tests explicit definition of a FuzzyNaiveDateTime."""
        fuzz = fuzzy.FuzzyNaiveDateTime(self.jan1, self.jan31)

        for _i in range(20):
            res = fuzz.evaluate(2, None, False)
            self.assertLessEqual(self.jan1, res)
            self.assertLessEqual(res, self.jan31)

    def test_partial_definition(self):
        """Test defining a FuzzyNaiveDateTime without passing an end date."""
        with utils.mocked_datetime_now(self.jan3, fuzzy):
            fuzz = fuzzy.FuzzyNaiveDateTime(self.jan1)

        for _i in range(20):
            res = fuzz.evaluate(2, None, False)
            self.assertLessEqual(self.jan1, res)
            self.assertLessEqual(res, self.jan3)

    def test_aware_start(self):
        """Tests that a timezone-aware start datetime is rejected."""
        fuzz = fuzzy.FuzzyNaiveDateTime(
            self.jan1.replace(tzinfo=compat.UTC), self.jan31)
        self.assertRaises(ValueError, fuzz.fuzz)

    def test_aware_end(self):
        """Tests that a timezone-aware end datetime is rejected."""
        fuzz = fuzzy.FuzzyNaiveDateTime(
            self.jan1, self.jan31.replace(tzinfo=compat.UTC))
        self.assertRaises(ValueError, fuzz.fuzz)

    def test_force_year(self):
        fuzz = fuzzy.FuzzyNaiveDateTime(self.jan1, self.jan31, force_year=4)

        for _i in range(20):
            res = fuzz.evaluate(2, None, False)
            self.assertEqual(4, res.year)

    def test_force_month(self):
        fuzz = fuzzy.FuzzyNaiveDateTime(self.jan1, self.jan31, force_month=4)

        for _i in range(20):
            res = fuzz.evaluate(2, None, False)
            self.assertEqual(4, res.month)

    def test_force_day(self):
        fuzz = fuzzy.FuzzyNaiveDateTime(self.jan1, self.jan31, force_day=4)

        for _i in range(20):
            res = fuzz.evaluate(2, None, False)
            self.assertEqual(4, res.day)

    def test_force_hour(self):
        fuzz = fuzzy.FuzzyNaiveDateTime(self.jan1, self.jan31, force_hour=4)

        for _i in range(20):
            res = fuzz.evaluate(2, None, False)
            self.assertEqual(4, res.hour)

    def test_force_minute(self):
        fuzz = fuzzy.FuzzyNaiveDateTime(self.jan1, self.jan31, force_minute=4)

        for _i in range(20):
            res = fuzz.evaluate(2, None, False)
            self.assertEqual(4, res.minute)

    def test_force_second(self):
        fuzz = fuzzy.FuzzyNaiveDateTime(self.jan1, self.jan31, force_second=4)

        for _i in range(20):
            res = fuzz.evaluate(2, None, False)
            self.assertEqual(4, res.second)

    def test_force_microsecond(self):
        fuzz = fuzzy.FuzzyNaiveDateTime(self.jan1, self.jan31, force_microsecond=4)

        for _i in range(20):
            res = fuzz.evaluate(2, None, False)
            self.assertEqual(4, res.microsecond)

    def test_invalid_definition(self):
        fuzz = fuzzy.FuzzyNaiveDateTime(self.jan31, self.jan1)
        self.assertRaises(ValueError, fuzz.fuzz)

    def test_invalid_partial_definition(self):
        with utils.mocked_datetime_now(self.jan1, fuzzy):
            fuzz = fuzzy.FuzzyNaiveDateTime(self.jan31)
            self.assertRaises(ValueError, fuzz.fuzz)

    def test_biased(self):
        """Tests a FuzzyDate with a biased random.randint."""

        fake_randint = lambda low, high: (low + high) // 2
        fuzz = fuzzy.FuzzyNaiveDateTime(self.jan1, self.jan31)

        with mock.patch('random.randint', fake_randint):
            res = fuzz.evaluate(2, None, False)

        self.assertEqual(datetime.datetime(2013, 1, 16), res)

    def test_biased_partial(self):
        """Tests a FuzzyDate with a biased random and implicit upper bound."""
        with utils.mocked_datetime_now(self.jan3, fuzzy):
            fuzz = fuzzy.FuzzyNaiveDateTime(self.jan1)

        fake_randint = lambda low, high: (low + high) // 2
        with mock.patch('random.randint', fake_randint):
            res = fuzz.evaluate(2, None, False)

        self.assertEqual(datetime.datetime(2013, 1, 2), res)


class FuzzyDateTimeTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Setup useful constants
        cls.jan1 = datetime.datetime(2013, 1, 1, tzinfo=compat.UTC)
        cls.jan3 = datetime.datetime(2013, 1, 3, tzinfo=compat.UTC)
        cls.jan31 = datetime.datetime(2013, 1, 31, tzinfo=compat.UTC)

    def test_accurate_definition(self):
        """Tests explicit definition of a FuzzyDateTime."""
        fuzz = fuzzy.FuzzyDateTime(self.jan1, self.jan31)

        for _i in range(20):
            res = fuzz.evaluate(2, None, False)
            self.assertLessEqual(self.jan1, res)
            self.assertLessEqual(res, self.jan31)

    def test_partial_definition(self):
        """Test defining a FuzzyDateTime without passing an end date."""
        with utils.mocked_datetime_now(self.jan3, fuzzy):
            fuzz = fuzzy.FuzzyDateTime(self.jan1)

        for _i in range(20):
            res = fuzz.evaluate(2, None, False)
            self.assertLessEqual(self.jan1, res)
            self.assertLessEqual(res, self.jan3)

    def test_invalid_definition(self):
        fuzz = fuzzy.FuzzyDateTime(self.jan31, self.jan1)
        self.assertRaises(ValueError, fuzz.fuzz)

    def test_invalid_partial_definition(self):
        with utils.mocked_datetime_now(self.jan1, fuzzy):
            fuzz = fuzzy.FuzzyDateTime(self.jan31)
            self.assertRaises(ValueError, fuzz.fuzz)

    def test_naive_start(self):
        """Tests that a timezone-naive start datetime is rejected."""
        fuzz = fuzzy.FuzzyDateTime(self.jan1.replace(tzinfo=None), self.jan31)
        self.assertRaises(ValueError, fuzz.fuzz)

    def test_naive_end(self):
        """Tests that a timezone-naive end datetime is rejected."""
        fuzz = fuzzy.FuzzyDateTime(self.jan1, self.jan31.replace(tzinfo=None))
        self.assertRaises(ValueError, fuzz.fuzz)

    def test_force_year(self):
        fuzz = fuzzy.FuzzyDateTime(self.jan1, self.jan31, force_year=4)

        for _i in range(20):
            res = fuzz.evaluate(2, None, False)
            self.assertEqual(4, res.year)

    def test_force_month(self):
        fuzz = fuzzy.FuzzyDateTime(self.jan1, self.jan31, force_month=4)

        for _i in range(20):
            res = fuzz.evaluate(2, None, False)
            self.assertEqual(4, res.month)

    def test_force_day(self):
        fuzz = fuzzy.FuzzyDateTime(self.jan1, self.jan31, force_day=4)

        for _i in range(20):
            res = fuzz.evaluate(2, None, False)
            self.assertEqual(4, res.day)

    def test_force_hour(self):
        fuzz = fuzzy.FuzzyDateTime(self.jan1, self.jan31, force_hour=4)

        for _i in range(20):
            res = fuzz.evaluate(2, None, False)
            self.assertEqual(4, res.hour)

    def test_force_minute(self):
        fuzz = fuzzy.FuzzyDateTime(self.jan1, self.jan31, force_minute=4)

        for _i in range(20):
            res = fuzz.evaluate(2, None, False)
            self.assertEqual(4, res.minute)

    def test_force_second(self):
        fuzz = fuzzy.FuzzyDateTime(self.jan1, self.jan31, force_second=4)

        for _i in range(20):
            res = fuzz.evaluate(2, None, False)
            self.assertEqual(4, res.second)

    def test_force_microsecond(self):
        fuzz = fuzzy.FuzzyDateTime(self.jan1, self.jan31, force_microsecond=4)

        for _i in range(20):
            res = fuzz.evaluate(2, None, False)
            self.assertEqual(4, res.microsecond)

    def test_biased(self):
        """Tests a FuzzyDate with a biased random.randint."""

        fake_randint = lambda low, high: (low + high) // 2
        fuzz = fuzzy.FuzzyDateTime(self.jan1, self.jan31)

        with mock.patch('random.randint', fake_randint):
            res = fuzz.evaluate(2, None, False)

        self.assertEqual(datetime.datetime(2013, 1, 16, tzinfo=compat.UTC), res)

    def test_biased_partial(self):
        """Tests a FuzzyDate with a biased random and implicit upper bound."""
        with utils.mocked_datetime_now(self.jan3, fuzzy):
            fuzz = fuzzy.FuzzyDateTime(self.jan1)

        fake_randint = lambda low, high: (low + high) // 2
        with mock.patch('random.randint', fake_randint):
            res = fuzz.evaluate(2, None, False)

        self.assertEqual(datetime.datetime(2013, 1, 2, tzinfo=compat.UTC), res)

    def test_lazy(self):
        start_date = datetime.datetime(2013, 1, 1, tzinfo=compat.UTC)
        end_date = datetime.datetime(2013, 1, 10, tzinfo=compat.UTC)

        class FooFactory(base.Factory):
            FACTORY_FOR = collections.namedtuple(
                'Foo', 'start_dt end_dt force_year force_month force_day '
                       'force_hour force_minute force_second '
                       'force_microsecond')

            start_dt = start_date
            end_dt = end_date
            force_year = 2013
            force_month = 1
            force_day = 2
            force_hour = 11
            force_minute = 22
            force_second = 33
            force_microsecond = 44

        fuzz = fuzzy.FuzzyDateTime(
            start_dt=datetime.datetime.now(tz=compat.UTC),
            force_year=declarations.SelfAttribute('force_year'),
            force_month=declarations.SelfAttribute('force_month'),
            force_day=declarations.SelfAttribute('force_day'),
            force_hour=declarations.SelfAttribute('force_hour'),
            force_minute=declarations.SelfAttribute('force_minute'),
            force_second=declarations.SelfAttribute('force_second'),
            force_microsecond=declarations.SelfAttribute('force_microsecond'))

        res = fuzz.evaluate(2, FooFactory(), False)

        self.assertEqual(datetime.datetime(2013, 1, 2, 11, 22, 33, 44,
                                           tzinfo=compat.UTC), res)

        fuzz = fuzzy.FuzzyDateTime(
            start_dt=declarations.SelfAttribute('start_dt'),
            end_dt=declarations.SelfAttribute('end_dt'))

        res = fuzz.evaluate(2, FooFactory(), False)

        self.assertLessEqual(start_date, res)
        self.assertGreaterEqual(end_date, res)


class FuzzyTextTestCase(unittest.TestCase):

    def test_unbiased(self):
        chars = ['a', 'b', 'c']
        fuzz = fuzzy.FuzzyText(prefix='pre', suffix='post', chars=chars, length=12)
        res = fuzz.evaluate(2, None, False)

        self.assertEqual('pre', res[:3])
        self.assertEqual('post', res[-4:])
        self.assertEqual(3 + 12 + 4, len(res))

        for char in res[3:-4]:
            self.assertIn(char, chars)

    def test_mock(self):
        fake_choice = lambda chars: chars[0]

        chars = ['a', 'b', 'c']
        fuzz = fuzzy.FuzzyText(prefix='pre', suffix='post', chars=chars, length=4)
        with mock.patch('random.choice', fake_choice):
            res = fuzz.evaluate(2, None, False)

        self.assertEqual('preaaaapost', res)

    def test_generator(self):
        def options():
            yield 'a'
            yield 'b'
            yield 'c'

        fuzz = fuzzy.FuzzyText(chars=options(), length=12)
        res = fuzz.evaluate(2, None, False)

        self.assertEqual(12, len(res))

        for char in res:
            self.assertIn(char, ['a', 'b', 'c'])

    def test_lazy(self):
        chars = ['a', 'b', 'c']

        fuzz = fuzzy.FuzzyText(prefix=declarations.SelfAttribute('prefix'),
                               suffix=declarations.SelfAttribute('suffix'),
                               chars=declarations.SelfAttribute('chars_'),
                               length=declarations.SelfAttribute('length'))

        class FooFactory(base.Factory):
            FACTORY_FOR = collections.namedtuple(
                'Foo', 'prefix suffix chars_ length')

            prefix = 'pre'
            suffix = 'post'
            chars_ = chars
            length = 12

        res = fuzz.evaluate(2, FooFactory(), False)

        self.assertEqual('pre', res[:3])
        self.assertEqual('post', res[-4:])
        self.assertEqual(3 + 12 + 4, len(res))

        for char in res[3:-4]:
            self.assertIn(char, chars)


class LazyArgumentTestCase(unittest.TestCase):
    def setUp(self):
        class Foo(object):
            param1 = fuzzy.LazyArgument()
            param2 = fuzzy.LazyArgument()
            const1 = 'constant'

        self.foo1 = Foo()
        self.foo2 = Foo()

    def test_literal(self):
        self.foo1.param1 = 123
        self.foo1.param2 = 'param2 for foo1'
        self.foo2.param1 = {"val": 1}
        self.foo2.param2 = 'param2 for foo2'

        self.assertEqual(self.foo1.param1, 123)
        self.assertEqual(self.foo1.param2, 'param2 for foo1')
        self.assertEqual(self.foo1.const1, 'constant')
        self.assertEqual(self.foo2.param1, {"val": 1})
        self.assertEqual(self.foo2.param2, 'param2 for foo2')
        self.assertEqual(self.foo2.const1, 'constant')

    def test_evaluate(self):
        self.foo1.param1 = declarations.SelfAttribute('foo1param1')
        self.foo1.param2 = declarations.SelfAttribute('foo1param2')
        self.foo2.param1 = declarations.SelfAttribute('foo2param1')
        self.foo2.param2 = declarations.SelfAttribute('foo2param2')

        Bar = collections.namedtuple(
            'Bar', 'foo1param1 foo1param2 foo2param1 foo2param2')

        with fuzzy.LazyArgument.evaluate(2, Bar('val1', 14, [1, 2], None), False):
            self.assertEqual(self.foo1.param1, 'val1')
            self.assertEqual(self.foo1.param2, 14)
            self.assertEqual(self.foo1.const1, 'constant')
            self.assertEqual(self.foo2.param1, [1, 2])
            self.assertEqual(self.foo2.param2, None)
            self.assertEqual(self.foo2.const1, 'constant')

        self.assertIsInstance(self.foo1.param1, declarations.SelfAttribute)
        self.assertIsInstance(self.foo1.param2, declarations.SelfAttribute)
        self.assertEqual(self.foo1.const1, 'constant')
        self.assertIsInstance(self.foo2.param1, declarations.SelfAttribute)
        self.assertIsInstance(self.foo2.param2, declarations.SelfAttribute)
        self.assertEqual(self.foo2.const1, 'constant')

        with fuzzy.LazyArgument.evaluate(2, Bar(1.1, {"a": 2}, '1', False), False):
            self.assertEqual(self.foo1.param1, 1.1)
            self.assertEqual(self.foo1.param2, {"a": 2})
            self.assertEqual(self.foo1.const1, 'constant')
            self.assertEqual(self.foo2.param1, '1')
            self.assertEqual(self.foo2.param2, False)
            self.assertEqual(self.foo2.const1, 'constant')

    def test_factory(self):
        Bar = collections.namedtuple(
            'Bar', 'start_date end_date lower_limit upper_limit value')

        class BarFactory(base.Factory):
            FACTORY_FOR = Bar

            start_date = fuzzy.FuzzyDate(datetime.date(2014, 1, 1))
            end_date = fuzzy.FuzzyDate(
                declarations.SelfAttribute('start_date'))

            lower_limit = fuzzy.FuzzyInteger(100)
            upper_limit = fuzzy.FuzzyInteger(
                declarations.SelfAttribute('lower_limit'), 200)
            value = fuzzy.FuzzyInteger(
                declarations.SelfAttribute('lower_limit'),
                declarations.SelfAttribute('upper_limit'))


        bar = BarFactory()

        self.assertGreaterEqual(bar.end_date, bar.start_date)
        self.assertGreaterEqual(bar.upper_limit, bar.lower_limit)
        self.assertGreaterEqual(bar.value, bar.lower_limit)
        self.assertLessEqual(bar.value, bar.upper_limit)
