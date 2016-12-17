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

from .base import (
    Factory,
    BaseDictFactory,
    DictFactory,
    BaseListFactory,
    ListFactory,
    StubFactory,

    BUILD_STRATEGY,
    CREATE_STRATEGY,
    STUB_STRATEGY,
    use_strategy,
)


from .errors import (
    FactoryError,
)

from .faker import Faker

from .declarations import (
    LazyFunction,
    LazyAttribute,
    Iterator,
    Sequence,
    LazyAttributeSequence,
    SelfAttribute,
    Trait,
    ContainerAttribute,
    SubFactory,
    Dict,
    List,
    PostGeneration,
    PostGenerationMethodCall,
    RelatedFactory,
)

from .helpers import (
    debug,

    build,
    create,
    stub,
    generate,
    simple_generate,
    make_factory,

    build_batch,
    create_batch,
    stub_batch,
    generate_batch,
    simple_generate_batch,

    lazy_attribute,
    iterator,
    sequence,
    lazy_attribute_sequence,
    container_attribute,
    post_generation,
)

# Backward compatibility; this should be removed soon.
from . import alchemy
from . import django
from . import mogo
from . import mongoengine


__version__ = '2.8.1'
__author__ = 'Raphaël Barrois <raphael.barrois+fboy@polytechnique.org>'


MogoFactory = mogo.MogoFactory
DjangoModelFactory = django.DjangoModelFactory
