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


"""Additional declarations for "fuzzy" attribute definitions."""


import random

from . import declarations


class BaseFuzzyAttribute(declarations.OrderedDeclaration):
    """Base class for fuzzy attributes.

    Custom fuzzers should override the `fuzz()` method.
    """

    def fuzz(self):
        raise NotImplementedError()

    def evaluate(self, sequence, obj, create, extra=None, containers=()):
        return self.fuzz()


class FuzzyAttribute(BaseFuzzyAttribute):
    """Similar to LazyAttribute, but yields random values.

    Attributes:
        function (callable): function taking no parameters and returning a
            random value.
    """

    def __init__(self, fuzzer, **kwargs):
        super(FuzzyAttribute, self).__init__(**kwargs)
        self.fuzzer = fuzzer

    def fuzz(self):
        return self.fuzzer()


class FuzzyChoice(BaseFuzzyAttribute):
    """Handles fuzzy choice of an attribute."""

    def __init__(self, choices, **kwargs):
        self.choices = list(choices)
        super(FuzzyChoice, self).__init__(**kwargs)

    def fuzz(self):
        return random.choice(self.choices)


class FuzzyInteger(BaseFuzzyAttribute):
    """Random integer within a given range."""

    def __init__(self, low, high=None, **kwargs):
        if high is None:
            high = low
            low = 0

        self.low = low
        self.high = high

        super(FuzzyInteger, self).__init__(**kwargs)

    def fuzz(self):
        return random.randint(self.low, self.high)
