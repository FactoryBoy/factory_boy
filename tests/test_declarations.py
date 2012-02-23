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

from factory.declarations import dig, OrderedDeclaration, Sequence

class OrderedDeclarationTestCase(unittest.TestCase):
    def test_errors(self):
        decl = OrderedDeclaration()
        self.assertRaises(NotImplementedError, decl.evaluate, None, {})


class DigTestCase(unittest.TestCase):
    class MyObj(object):
        def __init__(self, n):
            self.n = n

    def test_parentattr(self):
        obj = self.MyObj(1)
        obj.a__b__c = self.MyObj(2)
        obj.a = self.MyObj(3)
        obj.a.b = self.MyObj(4)
        obj.a.b.c = self.MyObj(5)

        self.assertEqual(2, dig(obj, 'a__b__c').n)

    def test_private(self):
        obj = self.MyObj(1)
        self.assertEqual(obj.__class__, dig(obj, '__class__'))

    def test_chaining(self):
        obj = self.MyObj(1)
        obj.a = self.MyObj(2)
        obj.a__c = self.MyObj(3)
        obj.a.b = self.MyObj(4)
        obj.a.b.c = self.MyObj(5)

        self.assertEqual(2, dig(obj, 'a').n)
        self.assertRaises(AttributeError, dig, obj, 'b')
        self.assertEqual(2, dig(obj, 'a__n'))
        self.assertEqual(3, dig(obj, 'a__c').n)
        self.assertRaises(AttributeError, dig, obj, 'a__c__n')
        self.assertRaises(AttributeError, dig, obj, 'a__d')
        self.assertEqual(4, dig(obj, 'a__b').n)
        self.assertEqual(4, dig(obj, 'a__b__n'))
        self.assertEqual(5, dig(obj, 'a__b__c').n)
        self.assertEqual(5, dig(obj, 'a__b__c__n'))



if __name__ == '__main__':
    unittest.main()
