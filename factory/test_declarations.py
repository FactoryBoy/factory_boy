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

from declarations import GlobalCounter, OrderedDeclaration, Sequence

class GlobalCounterTestCase(unittest.TestCase):
    def test_incr(self):
        init = GlobalCounter.step()
        mid = GlobalCounter.step()
        last = GlobalCounter.step()
        self.assertEqual(2, last - init)
        self.assertEqual(1, mid - init)


class OrderedDeclarationTestCase(unittest.TestCase):
    def test_errors(self):
        decl = OrderedDeclaration()
        self.assertRaises(NotImplementedError, decl.evaluate, None, {})

    def test_order(self):
        decl1 = OrderedDeclaration()
        decl2 = OrderedDeclaration()
        decl3 = Sequence(lambda n: 3 * n)
        self.assertTrue(decl1.order < decl2.order)
        self.assertTrue(decl2.order < decl3.order)

if __name__ == '__main__':
    unittest.main()
