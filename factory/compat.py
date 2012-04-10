# -*- coding: utf-8 -*-
import sys
PY3 = sys.version_info[0] == 3

try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    _xrange = xrange
except NameError: # python 3
    _xrange = range

try:
    advance_iterator = next
except NameError:
    def advance_iterator(it):
        return it.next()
next = advance_iterator

