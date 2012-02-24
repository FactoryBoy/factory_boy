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

from factory.declarations import deepgetattr, OrderedDeclaration, Sequence

class OrderedDeclarationTestCase(unittest.TestCase):
    def test_errors(self):
        decl = OrderedDeclaration()
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

        self.assertEqual(2, deepgetattr(obj, 'a').n)
        self.assertRaises(AttributeError, deepgetattr, obj, 'b')
        self.assertEqual(2, deepgetattr(obj, 'a.n'))
        self.assertEqual(3, deepgetattr(obj, 'a.c', 3))
        self.assertRaises(AttributeError, deepgetattr, obj, 'a.c.n')
        self.assertRaises(AttributeError, deepgetattr, obj, 'a.d')
        self.assertEqual(3, deepgetattr(obj, 'a.b').n)
        self.assertEqual(3, deepgetattr(obj, 'a.b.n'))
        self.assertEqual(4, deepgetattr(obj, 'a.b.c').n)
        self.assertEqual(4, deepgetattr(obj, 'a.b.c.n'))
        self.assertEqual(42, deepgetattr(obj, 'a.b.c.n.x', 42))



if __name__ == '__main__':
    unittest.main()
