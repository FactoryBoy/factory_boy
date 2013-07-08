# -*- coding: utf-8 -*-
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
"""Tests for factory_boy/Django interactions."""

import os

import factory
import factory.django


try:
    import django
except ImportError:  # pragma: no cover
    django = None

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    # Try PIL alternate name
    try:
        import Image
    except ImportError:
        # OK, not installed
        Image = None


from .compat import is_python2, unittest
from . import testdata
from . import tools


if django is not None:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.djapp.settings')

    from django import test as django_test
    from django.conf import settings
    from django.db import models as django_models
    from django.test import simple as django_test_simple
    from django.test import utils as django_test_utils
    from .djapp import models
else:  # pragma: no cover
    django_test = unittest

    class Fake(object):
        pass

    models = Fake()
    models.StandardModel = Fake
    models.NonIntegerPk = Fake
    models.WithFile = Fake
    models.WithImage = Fake


test_state = {}


def setUpModule():
    if django is None:  # pragma: no cover
        return
    django_test_utils.setup_test_environment()
    runner = django_test_simple.DjangoTestSuiteRunner()
    runner_state = runner.setup_databases()
    test_state.update({
        'runner': runner,
        'runner_state': runner_state,
    })


def tearDownModule():
    if django is None:  # pragma: no cover
        return
    runner = test_state['runner']
    runner_state = test_state['runner_state']
    runner.teardown_databases(runner_state)
    django_test_utils.teardown_test_environment()


class StandardFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = models.StandardModel

    foo = factory.Sequence(lambda n: "foo%d" % n)


class NonIntegerPkFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = models.NonIntegerPk

    foo = factory.Sequence(lambda n: "foo%d" % n)
    bar = ''


class WithFileFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = models.WithFile

    if django is not None:
        afile = factory.django.FileField()


class WithImageFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = models.WithImage

    if django is not None:
        animage = factory.django.ImageField()


@unittest.skipIf(django is None, "Django not installed.")
class DjangoPkSequenceTestCase(django_test.TestCase):
    def setUp(self):
        super(DjangoPkSequenceTestCase, self).setUp()
        StandardFactory.reset_sequence()

    def test_pk_first(self):
        std = StandardFactory.build()
        self.assertEqual('foo1', std.foo)

    def test_pk_many(self):
        std1 = StandardFactory.build()
        std2 = StandardFactory.build()
        self.assertEqual('foo1', std1.foo)
        self.assertEqual('foo2', std2.foo)

    def test_pk_creation(self):
        std1 = StandardFactory.create()
        self.assertEqual('foo1', std1.foo)
        self.assertEqual(1, std1.pk)

        StandardFactory.reset_sequence()
        std2 = StandardFactory.create()
        self.assertEqual('foo2', std2.foo)
        self.assertEqual(2, std2.pk)

    def test_pk_force_value(self):
        std1 = StandardFactory.create(pk=10)
        self.assertEqual('foo1', std1.foo)  # sequence was set before pk
        self.assertEqual(10, std1.pk)

        StandardFactory.reset_sequence()
        std2 = StandardFactory.create()
        self.assertEqual('foo11', std2.foo)
        self.assertEqual(11, std2.pk)


@unittest.skipIf(django is None, "Django not installed.")
class DjangoNonIntegerPkTestCase(django_test.TestCase):
    def setUp(self):
        super(DjangoNonIntegerPkTestCase, self).setUp()
        NonIntegerPkFactory.reset_sequence()

    def test_first(self):
        nonint = NonIntegerPkFactory.build()
        self.assertEqual('foo1', nonint.foo)

    def test_many(self):
        nonint1 = NonIntegerPkFactory.build()
        nonint2 = NonIntegerPkFactory.build()

        self.assertEqual('foo1', nonint1.foo)
        self.assertEqual('foo2', nonint2.foo)

    def test_creation(self):
        nonint1 = NonIntegerPkFactory.create()
        self.assertEqual('foo1', nonint1.foo)
        self.assertEqual('foo1', nonint1.pk)

        NonIntegerPkFactory.reset_sequence()
        nonint2 = NonIntegerPkFactory.build()
        self.assertEqual('foo1', nonint2.foo)

    def test_force_pk(self):
        nonint1 = NonIntegerPkFactory.create(pk='foo10')
        self.assertEqual('foo10', nonint1.foo)
        self.assertEqual('foo10', nonint1.pk)

        NonIntegerPkFactory.reset_sequence()
        nonint2 = NonIntegerPkFactory.create()
        self.assertEqual('foo1', nonint2.foo)
        self.assertEqual('foo1', nonint2.pk)


@unittest.skipIf(django is None, "Django not installed.")
class DjangoFileFieldTestCase(unittest.TestCase):

    def tearDown(self):
        super(DjangoFileFieldTestCase, self).tearDown()
        for path in os.listdir(models.WITHFILE_UPLOAD_DIR):
            # Remove temporary files written during tests.
            os.unlink(os.path.join(models.WITHFILE_UPLOAD_DIR, path))

    def test_default_build(self):
        o = WithFileFactory.build()
        self.assertIsNone(o.pk)
        self.assertEqual(b'', o.afile.read())
        self.assertEqual('django/example.dat', o.afile.name)

    def test_default_create(self):
        o = WithFileFactory.create()
        self.assertIsNotNone(o.pk)
        self.assertEqual(b'', o.afile.read())
        self.assertEqual('django/example.dat', o.afile.name)

    def test_with_content(self):
        o = WithFileFactory.build(afile__data='foo')
        self.assertIsNone(o.pk)
        self.assertEqual(b'foo', o.afile.read())
        self.assertEqual('django/example.dat', o.afile.name)

    def test_with_file(self):
        with open(testdata.TESTFILE_PATH, 'rb') as f:
            o = WithFileFactory.build(afile__from_file=f)
        self.assertIsNone(o.pk)
        self.assertEqual(b'example_data\n', o.afile.read())
        self.assertEqual('django/example.data', o.afile.name)

    def test_with_path(self):
        o = WithFileFactory.build(afile__from_path=testdata.TESTFILE_PATH)
        self.assertIsNone(o.pk)
        self.assertEqual(b'example_data\n', o.afile.read())
        self.assertEqual('django/example.data', o.afile.name)

    def test_with_file_empty_path(self):
        with open(testdata.TESTFILE_PATH, 'rb') as f:
            o = WithFileFactory.build(
                afile__from_file=f,
                afile__from_path=''
            )
        self.assertIsNone(o.pk)
        self.assertEqual(b'example_data\n', o.afile.read())
        self.assertEqual('django/example.data', o.afile.name)

    def test_with_path_empty_file(self):
        o = WithFileFactory.build(
            afile__from_path=testdata.TESTFILE_PATH,
            afile__from_file=None,
        )
        self.assertIsNone(o.pk)
        self.assertEqual(b'example_data\n', o.afile.read())
        self.assertEqual('django/example.data', o.afile.name)

    def test_error_both_file_and_path(self):
        self.assertRaises(ValueError, WithFileFactory.build,
            afile__from_file='fakefile',
            afile__from_path=testdata.TESTFILE_PATH,
        )

    def test_override_filename_with_path(self):
        o = WithFileFactory.build(
            afile__from_path=testdata.TESTFILE_PATH,
            afile__filename='example.foo',
        )
        self.assertIsNone(o.pk)
        self.assertEqual(b'example_data\n', o.afile.read())
        self.assertEqual('django/example.foo', o.afile.name)

    def test_existing_file(self):
        o1 = WithFileFactory.build(afile__from_path=testdata.TESTFILE_PATH)

        o2 = WithFileFactory.build(afile=o1.afile)
        self.assertIsNone(o2.pk)
        self.assertEqual(b'example_data\n', o2.afile.read())
        self.assertEqual('django/example_1.data', o2.afile.name)

    def test_no_file(self):
        o = WithFileFactory.build(afile=None)
        self.assertIsNone(o.pk)
        self.assertFalse(o.afile)


@unittest.skipIf(django is None, "Django not installed.")
@unittest.skipIf(Image is None, "PIL not installed.")
class DjangoImageFieldTestCase(unittest.TestCase):

    def tearDown(self):
        super(DjangoImageFieldTestCase, self).tearDown()
        for path in os.listdir(models.WITHFILE_UPLOAD_DIR):
            # Remove temporary files written during tests.
            os.unlink(os.path.join(models.WITHFILE_UPLOAD_DIR, path))

    def test_default_build(self):
        o = WithImageFactory.build()
        self.assertIsNone(o.pk)
        self.assertEqual(100, o.animage.width)
        self.assertEqual(100, o.animage.height)
        self.assertEqual('django/example.jpg', o.animage.name)

    def test_default_create(self):
        o = WithImageFactory.create()
        self.assertIsNotNone(o.pk)
        self.assertEqual(100, o.animage.width)
        self.assertEqual(100, o.animage.height)
        self.assertEqual('django/example.jpg', o.animage.name)

    def test_with_content(self):
        o = WithImageFactory.build(animage__width=13, animage__color='red')
        self.assertIsNone(o.pk)
        self.assertEqual(13, o.animage.width)
        self.assertEqual(13, o.animage.height)
        self.assertEqual('django/example.jpg', o.animage.name)

        i = Image.open(os.path.join(settings.MEDIA_ROOT, o.animage.name))
        colors = i.getcolors()
        # 169 pixels with rgb(254, 0, 0)
        self.assertEqual([(169, (254, 0, 0))], colors)
        self.assertEqual('JPEG', i.format)

    def test_gif(self):
        o = WithImageFactory.build(animage__width=13, animage__color='blue', animage__format='GIF')
        self.assertIsNone(o.pk)
        self.assertEqual(13, o.animage.width)
        self.assertEqual(13, o.animage.height)
        self.assertEqual('django/example.jpg', o.animage.name)

        i = Image.open(os.path.join(settings.MEDIA_ROOT, o.animage.name))
        colors = i.getcolors()
        # 169 pixels with color 190 from the GIF palette
        self.assertEqual([(169, 190)], colors)
        self.assertEqual('GIF', i.format)

    def test_with_file(self):
        with open(testdata.TESTIMAGE_PATH, 'rb') as f:
            o = WithImageFactory.build(animage__from_file=f)
        self.assertIsNone(o.pk)
        # Image file for a 42x42 green jpeg: 301 bytes long.
        self.assertEqual(301, len(o.animage.read()))
        self.assertEqual('django/example.jpeg', o.animage.name)

    def test_with_path(self):
        o = WithImageFactory.build(animage__from_path=testdata.TESTIMAGE_PATH)
        self.assertIsNone(o.pk)
        # Image file for a 42x42 green jpeg: 301 bytes long.
        self.assertEqual(301, len(o.animage.read()))
        self.assertEqual('django/example.jpeg', o.animage.name)

    def test_with_file_empty_path(self):
        with open(testdata.TESTIMAGE_PATH, 'rb') as f:
            o = WithImageFactory.build(
                animage__from_file=f,
                animage__from_path=''
            )
        self.assertIsNone(o.pk)
        # Image file for a 42x42 green jpeg: 301 bytes long.
        self.assertEqual(301, len(o.animage.read()))
        self.assertEqual('django/example.jpeg', o.animage.name)

    def test_with_path_empty_file(self):
        o = WithImageFactory.build(
            animage__from_path=testdata.TESTIMAGE_PATH,
            animage__from_file=None,
        )
        self.assertIsNone(o.pk)
        # Image file for a 42x42 green jpeg: 301 bytes long.
        self.assertEqual(301, len(o.animage.read()))
        self.assertEqual('django/example.jpeg', o.animage.name)

    def test_error_both_file_and_path(self):
        self.assertRaises(ValueError, WithImageFactory.build,
            animage__from_file='fakefile',
            animage__from_path=testdata.TESTIMAGE_PATH,
        )

    def test_override_filename_with_path(self):
        o = WithImageFactory.build(
            animage__from_path=testdata.TESTIMAGE_PATH,
            animage__filename='example.foo',
        )
        self.assertIsNone(o.pk)
        # Image file for a 42x42 green jpeg: 301 bytes long.
        self.assertEqual(301, len(o.animage.read()))
        self.assertEqual('django/example.foo', o.animage.name)

    def test_existing_file(self):
        o1 = WithImageFactory.build(animage__from_path=testdata.TESTIMAGE_PATH)

        o2 = WithImageFactory.build(animage=o1.animage)
        self.assertIsNone(o2.pk)
        # Image file for a 42x42 green jpeg: 301 bytes long.
        self.assertEqual(301, len(o2.animage.read()))
        self.assertEqual('django/example_1.jpeg', o2.animage.name)

    def test_no_file(self):
        o = WithImageFactory.build(animage=None)
        self.assertIsNone(o.pk)
        self.assertFalse(o.animage)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
