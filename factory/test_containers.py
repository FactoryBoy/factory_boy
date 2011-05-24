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

from containers import DeclarationsHolder, OrderedDeclarationDict, ObjectParamsWrapper
import base
import declarations

class ObjectParamsWrapperTestCase(unittest.TestCase):
    def test_read(self):
        vals = {'one': 1, 'two': 2}
        wrapper = ObjectParamsWrapper(vals)

        self.assertEqual(1, wrapper.one)
        self.assertEqual(2, wrapper.two)
        self.assertRaises(AttributeError, getattr, wrapper, 'three')
        self.assertRaises(AttributeError, setattr, wrapper, 'one', 1)

    def test_standard_attributes(self):
        wrapper = ObjectParamsWrapper({})
        self.assertEqual(ObjectParamsWrapper, wrapper.__class__)


class OrderedDeclarationMock(object):
    def __init__(self, order):
        self.order = order


class OrderedDeclarationDictTestCase(unittest.TestCase):
    def test_basics(self):
        one = OrderedDeclarationMock(1)
        two = OrderedDeclarationMock(2)
        three = OrderedDeclarationMock(3)
        d = OrderedDeclarationDict(one=one, two=two, three=three)
        self.assertEqual(one, d['one'])
        self.assertEqual(two, d['two'])
        self.assertEqual(three, d['three'])

        self.assertTrue('one' in d)
        self.assertTrue('two' in d)
        self.assertTrue('three' in d)

        self.assertEqual(one, d.pop('one'))
        self.assertFalse('one' in d)

        d['one'] = one
        self.assertTrue('one' in d)
        self.assertEqual(one, d['one'])

        self.assertEqual(set(['one', 'two', 'three']),
                         set(d))

    def test_order(self):
        one = OrderedDeclarationMock(1)
        two = OrderedDeclarationMock(2)
        ten = OrderedDeclarationMock(10)
        d = OrderedDeclarationDict(one=one, two=two, ten=ten)

        self.assertEqual(['one', 'two', 'ten'], list(d))
        self.assertEqual([('one', one), ('two', two), ('ten', ten)],
                         d.items())
        self.assertEqual([('one', one), ('two', two), ('ten', ten)],
                         list(d.iteritems()))

    def test_insert(self):
        one = OrderedDeclarationMock(1)
        two = OrderedDeclarationMock(2)
        four = OrderedDeclarationMock(4)
        ten = OrderedDeclarationMock(10)
        d = OrderedDeclarationDict(one=one, two=two, ten=ten)

        self.assertEqual(['one', 'two', 'ten'], list(d))
        d['four'] = four
        self.assertEqual(['one', 'two', 'four', 'ten'], list(d))

    def test_replace(self):
        one = OrderedDeclarationMock(1)
        two = OrderedDeclarationMock(2)
        three = OrderedDeclarationMock(3)
        ten = OrderedDeclarationMock(10)
        d = OrderedDeclarationDict(one=one, two=two, ten=ten)

        self.assertEqual(['one', 'two', 'ten'], list(d))
        d['one'] = three

        self.assertEqual(three, d['one'])
        self.assertEqual(['two', 'one', 'ten'], list(d))


class DeclarationsHolderTestCase(unittest.TestCase):
    def test_empty(self):
        holder = DeclarationsHolder()
        self.assertRaises(KeyError, holder.__getitem__, 'one')
        holder.update_base({'one': 1})
        self.assertEqual(1, holder['one'])

    def test_simple(self):
        """Tests a simple use case without OrderedDeclaration."""
        class ExampleFactory(object):
            @classmethod
            def _generate_next_sequence(cls):
                return 42

        holder = DeclarationsHolder({'one': 1, 'two': 2})
        self.assertTrue('one' in holder)
        self.assertTrue('two' in holder)
        holder.update_base({'two': 3, 'three': 3})
        self.assertEqual(1, holder['one'])
        self.assertEqual(3, holder['two'])
        self.assertEqual(3, holder['three'])

        attrs = holder.build_attributes(ExampleFactory)
        self.assertEqual(1, attrs['one'])
        self.assertEqual(3, attrs['two'])
        self.assertEqual(3, attrs['three'])
        self.assertEqual(42, ExampleFactory.sequence)

        self.assertEqual(set([('one', 1), ('two', 3), ('three', 3)]),
                         set(holder.items()))

        attrs = holder.build_attributes(ExampleFactory, False, {'two': 2})
        self.assertEqual(1, attrs['one'])
        self.assertEqual(2, attrs['two'])
        self.assertEqual(3, attrs['three'])

    def test_skip_specials(self):
        """Makes sure that attributes starting with _ are skipped."""
        holder = DeclarationsHolder({'one': 1, '_two': 2})
        self.assertTrue('one' in holder)
        self.assertFalse('_two' in holder)

        remains = holder.update_base({'_two': 2, 'three': 3})
        self.assertTrue('three' in holder)
        self.assertFalse('_two' in holder)
        self.assertEqual({'_two': 2}, remains)

    def test_ordered(self):
        """Tests the handling of OrderedDeclaration."""
        class ExampleFactory(object):
            @classmethod
            def _generate_next_sequence(cls):
                return 42

        two = declarations.LazyAttribute(lambda o: 2 * o.one)
        three = declarations.LazyAttribute(lambda o: o.one + o.two)
        holder = DeclarationsHolder({'one': 1, 'two': two, 'three': three})

        self.assertEqual([('one', 1), ('two', two), ('three', three)],
                         holder.items())

        self.assertEqual(two, holder['two'])

        attrs = holder.build_attributes(ExampleFactory)
        self.assertEqual(1, attrs['one'])
        self.assertEqual(2, attrs['two'])
        self.assertEqual(3, attrs['three'])

        attrs = holder.build_attributes(ExampleFactory, False, {'one': 4})
        self.assertEqual(4, attrs['one'])
        self.assertEqual(8, attrs['two'])
        self.assertEqual(12, attrs['three'])

        attrs = holder.build_attributes(ExampleFactory, False, {'one': 4, 'two': 2})
        self.assertEqual(4, attrs['one'])
        self.assertEqual(2, attrs['two'])
        self.assertEqual(6, attrs['three'])

    def test_sub_factory(self):
        """Tests the behaviour of sub-factories."""
        class TestObject(object):
            def __init__(self, one=None, two=None, three=None, four=None, five=None):
                self.one = one
                self.two = two
                self.three = three
                self.four = four
                self.five = five

        class TestObjectFactory(base.Factory):
            FACTORY_FOR = TestObject
            two = 2
            five = declarations.Sequence(lambda n: n+1, type=int)

            @classmethod
            def _generate_next_sequence(cls):
                return 42

        class ExampleFactory(object):
            @classmethod
            def _generate_next_sequence(cls):
                return 42

        sub = declarations.SubFactory(TestObjectFactory,
                                      three=3,
                                      four=declarations.LazyAttribute(
                                          lambda o: 2 * o.two))

        holder = DeclarationsHolder(defaults={'sub': sub, 'one': 1})
        self.assertEqual(sub, holder['sub'])
        self.assertTrue('sub' in holder)

        attrs = holder.build_attributes(ExampleFactory)
        self.assertEqual(1, attrs['one'])
        self.assertEqual(2, attrs['sub'].two)
        self.assertEqual(3, attrs['sub'].three)
        self.assertEqual(4, attrs['sub'].four)

        attrs = holder.build_attributes(ExampleFactory, False, {'sub__two': 8, 'three__four': 4})
        self.assertEqual(1, attrs['one'])
        self.assertEqual(4, attrs['three__four'])
        self.assertEqual(8, attrs['sub'].two)
        self.assertEqual(3, attrs['sub'].three)
        self.assertEqual(16, attrs['sub'].four)


if __name__ == '__main__':
    unittest.main()
