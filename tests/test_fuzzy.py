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


from factory import fuzzy

from .compat import mock, unittest


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
        fake_randint = lambda low, high: low + high

        fuzz = fuzzy.FuzzyInteger(2, 8)

        with mock.patch('random.randint', fake_randint):
            res = fuzz.evaluate(2, None, False)

        self.assertEqual(10, res)

    def test_biased_high_only(self):
        fake_randint = lambda low, high: low + high

        fuzz = fuzzy.FuzzyInteger(8)

        with mock.patch('random.randint', fake_randint):
            res = fuzz.evaluate(2, None, False)

        self.assertEqual(8, res)
