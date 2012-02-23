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

__version__ = '1.1.0'  # Remember to change in setup.py as well!
__author__ = 'Raphaël Barrois <raphael.barrois@polytechnique.org>'

from base import (
    Factory,
    StubFactory,
    DjangoModelFactory,

    build,
    create,
    stub,
    make_factory,

    BUILD_STRATEGY,
    CREATE_STRATEGY,
    STUB_STRATEGY,

    DJANGO_CREATION,
    NAIVE_BUILD,
    MOGO_BUILD,
)

from declarations import (
    LazyAttribute,
    Sequence,
    LazyAttributeSequence,
    SelfAttribute,
    ContainerAttribute,
    SubFactory,

    lazy_attribute,
    sequence,
    lazy_attribute_sequence,
    container_attribute,
)

