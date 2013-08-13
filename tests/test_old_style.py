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

from factory import base
from .compat import unittest


class TestObject(object):
    def __init__(self, one=None, two=None, three=None, four=None):
        self.one = one
        self.two = two
        self.three = three
        self.four = four


class TestOtherObject(object):
    pass


class TestObjectFactory(base.Factory):
    FACTORY_FOR = TestObject
    ABSTRACT_FACTORY = True
    FACTORY_STRATEGY = 'strategy'
    FACTORY_HIDDEN_ARGS = ()
    FACTORY_ARG_PARAMETERS = ()
    FACTORY_DJANGO_GET_OR_CREATE = False
    FACTORY_SESSION = 'session'


class TestNewObjectFactory(base.Factory):
    FACTORY_FOR = TestObject
    ABSTRACT_FACTORY = True
    FACTORY_STRATEGY = 'strategy'
    FACTORY_HIDDEN_ARGS = ()
    FACTORY_ARG_PARAMETERS = ()
    FACTORY_DJANGO_GET_OR_CREATE = False
    FACTORY_SESSION = 'session'

    # These should all be ignored
    class Meta:
        model = TestOtherObject
        abstract = False
        strategy = 'other'
        hide = ('hide',)
        force_args = ('forced',)
        django_get_or_create = True
        session = 'another'


class FactoryOldStyleTestCase(unittest.TestCase):
    def test_old_style_options_are_put_into_private_meta(self):
        self.assertEqual(TestObjectFactory._meta.model, TestObject)
        self.assertEqual(TestObjectFactory._meta.abstract, True)
        self.assertEqual(TestObjectFactory._meta.strategy, 'strategy')
        self.assertEqual(TestObjectFactory._meta.hide, ())
        self.assertEqual(TestObjectFactory._meta.force_args, ())
        self.assertEqual(TestObjectFactory._meta.django_get_or_create, False)
        self.assertEqual(TestObjectFactory._meta.session, 'session')

    def test_old_style_options_take_precendence(self):
        self.assertEqual(TestNewObjectFactory._meta.model, TestObject)
        self.assertEqual(TestNewObjectFactory._meta.abstract, True)
        self.assertEqual(TestNewObjectFactory._meta.strategy, 'strategy')
        self.assertEqual(TestNewObjectFactory._meta.hide, ())
        self.assertEqual(TestNewObjectFactory._meta.force_args, ())
        self.assertEqual(TestNewObjectFactory._meta.django_get_or_create, False)
        self.assertEqual(TestNewObjectFactory._meta.session, 'session')

    def test_old_style_options_are_still_removed(self):
        self.assertFalse(hasattr(TestObjectFactory, 'FACTORY_FOR'))
        self.assertFalse(hasattr(TestObjectFactory, 'ABSTRACT_FACTORY'))
        self.assertFalse(hasattr(TestObjectFactory, 'FACTORY_STRATEGY'))
        self.assertFalse(hasattr(TestObjectFactory, 'FACTORY_HIDDEN_ARGS'))
        self.assertFalse(hasattr(TestObjectFactory, 'FACTORY_ARG_PARAMETERS'))
        self.assertFalse(hasattr(TestObjectFactory, 'FACTORY_DJANGO_GET_OR_CREATE'))
        self.assertFalse(hasattr(TestObjectFactory, 'FACTORY_SESSION'))


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
