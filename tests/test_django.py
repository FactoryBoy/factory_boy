# -*- coding: utf-8 -*-
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
"""Tests for factory_boy/Django interactions."""

import os
from .compat import is_python2, unittest, mock


try:
    import django
except ImportError:  # pragma: no cover
    django = None

# Setup Django as soon as possible
if django is not None:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.djapp.settings')

    if django.VERSION >= (1, 7, 0):
        django.setup()
    from django import test as django_test
    from django.conf import settings
    from django.db import models as django_models
    if django.VERSION <= (1, 8, 0):
        from django.test.simple import DjangoTestSuiteRunner
    else:
        from django.test.runner import DiscoverRunner as DjangoTestSuiteRunner
    from django.test import utils as django_test_utils
    from django.db.models import signals
    from .djapp import models

else:
    django_test = unittest



try:
    from PIL import Image
except ImportError:  # pragma: no cover
    # Try PIL alternate name
    try:
        import Image
    except ImportError:
        # OK, not installed
        Image = None


import factory
import factory.django
from factory.compat import BytesIO

from . import testdata
from . import tools


test_state = {}


def setUpModule():
    if django is None:  # pragma: no cover
        raise unittest.SkipTest("Django not installed")
    django_test_utils.setup_test_environment()
    runner = DjangoTestSuiteRunner()
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


if django is not None:
    class StandardFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = models.StandardModel

        foo = factory.Sequence(lambda n: "foo%d" % n)


    class StandardFactoryWithPKField(factory.django.DjangoModelFactory):
        class Meta:
            model = models.StandardModel
            django_get_or_create = ('pk',)

        foo = factory.Sequence(lambda n: "foo%d" % n)
        pk = None


    class NonIntegerPkFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = models.NonIntegerPk

        foo = factory.Sequence(lambda n: "foo%d" % n)
        bar = ''


    class MultifieldModelFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = models.MultifieldModel
            django_get_or_create = ['slug']

        text = factory.Faker('text')


    class AbstractBaseFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = models.AbstractBase
            abstract = True

        foo = factory.Sequence(lambda n: "foo%d" % n)


    class ConcreteSonFactory(AbstractBaseFactory):
        class Meta:
            model = models.ConcreteSon


    class AbstractSonFactory(AbstractBaseFactory):
        class Meta:
            model = models.AbstractSon


    class ConcreteGrandSonFactory(AbstractBaseFactory):
        class Meta:
            model = models.ConcreteGrandSon


    class WithFileFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = models.WithFile

        if django is not None:
            afile = factory.django.FileField()


    class WithImageFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = models.WithImage

        if django is not None:
            animage = factory.django.ImageField()


    class WithSignalsFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = models.WithSignals


    class WithCustomManagerFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = models.WithCustomManager

        foo = factory.Sequence(lambda n: "foo%d" % n)


@unittest.skipIf(django is None, "Django not installed.")
class ModelTests(django_test.TestCase):
    def test_unset_model(self):
        class UnsetModelFactory(factory.django.DjangoModelFactory):
            pass

        self.assertRaises(factory.FactoryError, UnsetModelFactory.create)

    def test_cross_database(self):
        class OtherDBFactory(factory.django.DjangoModelFactory):
            class Meta:
                model = models.StandardModel
                database = 'replica'

        obj = OtherDBFactory()
        self.assertFalse(models.StandardModel.objects.exists())
        self.assertEqual(obj, models.StandardModel.objects.using('replica').get())


@unittest.skipIf(django is None, "Django not installed.")
class DjangoPkSequenceTestCase(django_test.TestCase):
    def setUp(self):
        super(DjangoPkSequenceTestCase, self).setUp()
        StandardFactory.reset_sequence()

    def test_pk_first(self):
        std = StandardFactory.build()
        self.assertEqual('foo0', std.foo)

    def test_pk_many(self):
        std1 = StandardFactory.build()
        std2 = StandardFactory.build()
        self.assertEqual('foo0', std1.foo)
        self.assertEqual('foo1', std2.foo)

    def test_pk_creation(self):
        std1 = StandardFactory.create()
        self.assertEqual('foo0', std1.foo)
        self.assertEqual(1, std1.pk)

        StandardFactory.reset_sequence()
        std2 = StandardFactory.create()
        self.assertEqual('foo0', std2.foo)
        self.assertEqual(2, std2.pk)

    def test_pk_force_value(self):
        std1 = StandardFactory.create(pk=10)
        self.assertEqual('foo0', std1.foo)  # sequence is unrelated to pk
        self.assertEqual(10, std1.pk)

        StandardFactory.reset_sequence()
        std2 = StandardFactory.create()
        self.assertEqual('foo0', std2.foo)
        self.assertEqual(11, std2.pk)


@unittest.skipIf(django is None, "Django not installed.")
class DjangoGetOrCreateTests(django_test.TestCase):
    def test_simple_call(self):
        obj1 = MultifieldModelFactory(slug='slug1')
        obj2 = MultifieldModelFactory(slug='slug1')
        obj3 = MultifieldModelFactory(slug='alt')

        self.assertEqual(obj1, obj2)
        self.assertEqual(2, models.MultifieldModel.objects.count())

    def test_missing_arg(self):
        with self.assertRaises(factory.FactoryError):
            MultifieldModelFactory()

    def test_multicall(self):
        objs = MultifieldModelFactory.create_batch(6,
            slug=factory.Iterator(['main', 'alt']),
        )
        self.assertEqual(6, len(objs))
        self.assertEqual(2, len(set(objs)))
        self.assertEqual(2, models.MultifieldModel.objects.count())


@unittest.skipIf(django is None, "Django not installed.")
class DjangoPkForceTestCase(django_test.TestCase):
    def setUp(self):
        super(DjangoPkForceTestCase, self).setUp()
        StandardFactoryWithPKField.reset_sequence()

    def test_no_pk(self):
        std = StandardFactoryWithPKField()
        self.assertIsNotNone(std.pk)
        self.assertEqual('foo0', std.foo)

    def test_force_pk(self):
        std = StandardFactoryWithPKField(pk=42)
        self.assertIsNotNone(std.pk)
        self.assertEqual('foo0', std.foo)

    def test_reuse_pk(self):
        std1 = StandardFactoryWithPKField(foo='bar')
        self.assertIsNotNone(std1.pk)

        std2 = StandardFactoryWithPKField(pk=std1.pk, foo='blah')
        self.assertEqual(std1.pk, std2.pk)
        self.assertEqual('bar', std2.foo)


@unittest.skipIf(django is None, "Django not installed.")
class DjangoModelLoadingTestCase(django_test.TestCase):
    """Tests class Meta:
     model = 'app.Model' pattern."""

    def test_loading(self):
        class ExampleFactory(factory.DjangoModelFactory):
            class Meta:
                model = 'djapp.StandardModel'

        self.assertEqual(models.StandardModel, ExampleFactory._get_model_class())

    def test_building(self):
        class ExampleFactory(factory.DjangoModelFactory):
            class Meta:
                model = 'djapp.StandardModel'

        e = ExampleFactory.build()
        self.assertEqual(models.StandardModel, e.__class__)

    def test_inherited_loading(self):
        """Proper loading of a model within 'child' factories.

        See https://github.com/FactoryBoy/factory_boy/issues/109.
        """
        class ExampleFactory(factory.DjangoModelFactory):
            class Meta:
                model = 'djapp.StandardModel'

        class Example2Factory(ExampleFactory):
            pass

        e = Example2Factory.build()
        self.assertEqual(models.StandardModel, e.__class__)

    def test_inherited_loading_and_sequence(self):
        """Proper loading of a model within 'child' factories.

        See https://github.com/FactoryBoy/factory_boy/issues/109.
        """
        class ExampleFactory(factory.DjangoModelFactory):
            class Meta:
                model = 'djapp.StandardModel'

            foo = factory.Sequence(lambda n: n)

        class Example2Factory(ExampleFactory):
            class Meta:
                model = 'djapp.StandardSon'

        self.assertEqual(models.StandardSon, Example2Factory._get_model_class())

        e1 = ExampleFactory.build()
        e2 = Example2Factory.build()
        e3 = ExampleFactory.build()
        self.assertEqual(models.StandardModel, e1.__class__)
        self.assertEqual(models.StandardSon, e2.__class__)
        self.assertEqual(models.StandardModel, e3.__class__)
        self.assertEqual(0, e1.foo)
        self.assertEqual(1, e2.foo)
        self.assertEqual(2, e3.foo)


@unittest.skipIf(django is None, "Django not installed.")
class DjangoNonIntegerPkTestCase(django_test.TestCase):
    def setUp(self):
        super(DjangoNonIntegerPkTestCase, self).setUp()
        NonIntegerPkFactory.reset_sequence()

    def test_first(self):
        nonint = NonIntegerPkFactory.build()
        self.assertEqual('foo0', nonint.foo)

    def test_many(self):
        nonint1 = NonIntegerPkFactory.build()
        nonint2 = NonIntegerPkFactory.build()

        self.assertEqual('foo0', nonint1.foo)
        self.assertEqual('foo1', nonint2.foo)

    def test_creation(self):
        nonint1 = NonIntegerPkFactory.create()
        self.assertEqual('foo0', nonint1.foo)
        self.assertEqual('foo0', nonint1.pk)

        NonIntegerPkFactory.reset_sequence()
        nonint2 = NonIntegerPkFactory.build()
        self.assertEqual('foo0', nonint2.foo)

    def test_force_pk(self):
        nonint1 = NonIntegerPkFactory.create(pk='foo10')
        self.assertEqual('foo10', nonint1.foo)
        self.assertEqual('foo10', nonint1.pk)

        NonIntegerPkFactory.reset_sequence()
        nonint2 = NonIntegerPkFactory.create()
        self.assertEqual('foo0', nonint2.foo)
        self.assertEqual('foo0', nonint2.pk)


@unittest.skipIf(django is None, "Django not installed.")
class DjangoAbstractBaseSequenceTestCase(django_test.TestCase):
    def test_auto_sequence(self):
        """The sequence of the concrete son of an abstract model should be autonomous."""
        obj = ConcreteSonFactory()
        self.assertEqual(1, obj.pk)

    def test_auto_sequence(self):
        """The sequence of the concrete grandson of an abstract model should be autonomous."""
        obj = ConcreteGrandSonFactory()
        self.assertEqual(1, obj.pk)

    def test_optional_abstract(self):
        """Users need not describe the factory for an abstract model as abstract."""
        class AbstractBaseFactory(factory.django.DjangoModelFactory):
            class Meta:
                model = models.AbstractBase

            foo = factory.Sequence(lambda n: "foo%d" % n)

        class ConcreteSonFactory(AbstractBaseFactory):
            class Meta:
                model = models.ConcreteSon

        obj = ConcreteSonFactory()
        self.assertEqual(1, obj.pk)
        self.assertEqual("foo0", obj.foo)


@unittest.skipIf(django is None, "Django not installed.")
class DjangoRelatedFieldTestCase(django_test.TestCase):

    @classmethod
    def setUpClass(cls):
        super(DjangoRelatedFieldTestCase, cls).setUpClass()
        class PointedFactory(factory.django.DjangoModelFactory):
            class Meta:
                model = models.PointedModel
            foo = 'ahah'

        class PointerFactory(factory.django.DjangoModelFactory):
            class Meta:
                model = models.PointingModel
            pointed = factory.SubFactory(PointedFactory, foo='hihi')
            foo = 'bar'

        cls.PointedFactory = PointedFactory
        cls.PointerFactory = PointerFactory

    def test_direct_related_create(self):
        ptr = self.PointerFactory()
        self.assertEqual('hihi', ptr.pointed.foo)
        self.assertEqual(ptr.pointed, models.PointedModel.objects.get())


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
        self.assertEqual('example.dat', o.afile.name)

        o.save()
        self.assertEqual('django/example.dat', o.afile.name)

    def test_default_create(self):
        o = WithFileFactory.create()
        self.assertIsNotNone(o.pk)
        self.assertEqual(b'', o.afile.read())
        self.assertEqual('django/example.dat', o.afile.name)

    def test_with_content(self):
        o = WithFileFactory.build(afile__data='foo')
        self.assertIsNone(o.pk)

        # Django only allocates the full path on save()
        o.save()
        self.assertEqual(b'foo', o.afile.read())
        self.assertEqual('django/example.dat', o.afile.name)

    def test_with_file(self):
        with open(testdata.TESTFILE_PATH, 'rb') as f:
            o = WithFileFactory.build(afile__from_file=f)
            o.save()

        self.assertEqual(b'example_data\n', o.afile.read())
        self.assertEqual('django/example.data', o.afile.name)

    def test_with_path(self):
        o = WithFileFactory.build(afile__from_path=testdata.TESTFILE_PATH)
        self.assertIsNone(o.pk)

        # Django only allocates the full path on save()
        o.save()
        self.assertEqual(b'example_data\n', o.afile.read())
        self.assertEqual('django/example.data', o.afile.name)

    def test_with_file_empty_path(self):
        with open(testdata.TESTFILE_PATH, 'rb') as f:
            o = WithFileFactory.build(
                afile__from_file=f,
                afile__from_path=''
            )
            # Django only allocates the full path on save()
            o.save()

        self.assertEqual(b'example_data\n', o.afile.read())
        self.assertEqual('django/example.data', o.afile.name)

    def test_with_path_empty_file(self):
        o = WithFileFactory.build(
            afile__from_path=testdata.TESTFILE_PATH,
            afile__from_file=None,
        )
        self.assertIsNone(o.pk)

        # Django only allocates the full path on save()
        o.save()
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

        # Django only allocates the full path on save()
        o.save()
        self.assertEqual(b'example_data\n', o.afile.read())
        self.assertEqual('django/example.foo', o.afile.name)

    def test_existing_file(self):
        o1 = WithFileFactory.build(afile__from_path=testdata.TESTFILE_PATH)
        o1.save()
        self.assertEqual('django/example.data', o1.afile.name)

        o2 = WithFileFactory.build(afile__from_file=o1.afile)
        self.assertIsNone(o2.pk)
        o2.save()

        self.assertEqual(b'example_data\n', o2.afile.read())
        self.assertNotEqual('django/example.data', o2.afile.name)
        self.assertRegexpMatches(o2.afile.name, r'django/example_\w+.data')

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
        o.save()

        self.assertEqual(100, o.animage.width)
        self.assertEqual(100, o.animage.height)
        self.assertEqual('django/example.jpg', o.animage.name)

    def test_default_create(self):
        o = WithImageFactory.create()
        self.assertIsNotNone(o.pk)
        o.save()

        self.assertEqual(100, o.animage.width)
        self.assertEqual(100, o.animage.height)
        self.assertEqual('django/example.jpg', o.animage.name)

    def test_complex_create(self):
        o = WithImageFactory.create(
            size=10,
            animage__filename=factory.Sequence(lambda n: 'img%d.jpg' % n),
            __sequence=42,
            animage__width=factory.SelfAttribute('..size'),
            animage__height=factory.SelfAttribute('width'),
        )
        self.assertIsNotNone(o.pk)
        self.assertEqual('django/img42.jpg', o.animage.name)

    def test_with_content(self):
        o = WithImageFactory.build(animage__width=13, animage__color='red')
        self.assertIsNone(o.pk)
        o.save()

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
        o.save()

        self.assertEqual(13, o.animage.width)
        self.assertEqual(13, o.animage.height)
        self.assertEqual('django/example.jpg', o.animage.name)

        i = Image.open(os.path.join(settings.MEDIA_ROOT, o.animage.name))
        colors = i.convert('RGB').getcolors()
        # 169 pixels with rgb(0, 0, 255)
        self.assertEqual([(169, (0, 0, 255))], colors)
        self.assertEqual('GIF', i.format)

    def test_with_file(self):
        with open(testdata.TESTIMAGE_PATH, 'rb') as f:
            o = WithImageFactory.build(animage__from_file=f)
            o.save()

        # Image file for a 42x42 green jpeg: 301 bytes long.
        self.assertEqual(301, len(o.animage.read()))
        self.assertEqual('django/example.jpeg', o.animage.name)

    def test_with_path(self):
        o = WithImageFactory.build(animage__from_path=testdata.TESTIMAGE_PATH)
        self.assertIsNone(o.pk)
        o.save()

        # Image file for a 42x42 green jpeg: 301 bytes long.
        self.assertEqual(301, len(o.animage.read()))
        self.assertEqual('django/example.jpeg', o.animage.name)

    def test_with_file_empty_path(self):
        with open(testdata.TESTIMAGE_PATH, 'rb') as f:
            o = WithImageFactory.build(
                animage__from_file=f,
                animage__from_path=''
            )
            o.save()

        # Image file for a 42x42 green jpeg: 301 bytes long.
        self.assertEqual(301, len(o.animage.read()))
        self.assertEqual('django/example.jpeg', o.animage.name)

    def test_with_path_empty_file(self):
        o = WithImageFactory.build(
            animage__from_path=testdata.TESTIMAGE_PATH,
            animage__from_file=None,
        )
        self.assertIsNone(o.pk)
        o.save()

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
        o.save()

        # Image file for a 42x42 green jpeg: 301 bytes long.
        self.assertEqual(301, len(o.animage.read()))
        self.assertEqual('django/example.foo', o.animage.name)

    def test_existing_file(self):
        o1 = WithImageFactory.build(animage__from_path=testdata.TESTIMAGE_PATH)
        o1.save()

        o2 = WithImageFactory.build(animage__from_file=o1.animage)
        self.assertIsNone(o2.pk)
        o2.save()

        # Image file for a 42x42 green jpeg: 301 bytes long.
        self.assertEqual(301, len(o2.animage.read()))
        self.assertNotEqual('django/example.jpeg', o2.animage.name)
        self.assertRegexpMatches(o2.animage.name, r'django/example_\w+.jpeg')

    def test_no_file(self):
        o = WithImageFactory.build(animage=None)
        self.assertIsNone(o.pk)
        self.assertFalse(o.animage)

    def _img_test_func(self):
        img = Image.new('RGB', (32,32), 'blue')
        img_io = BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)
        return img_io

    def test_with_func(self):
        o = WithImageFactory.build(animage__from_func=self._img_test_func)
        self.assertIsNone(o.pk)
        i = Image.open(o.animage.file)
        self.assertEqual('JPEG', i.format)
        self.assertEqual(32, i.width)
        self.assertEqual(32, i.height)


@unittest.skipIf(django is None, "Django not installed.")
class PreventSignalsTestCase(unittest.TestCase):
    def setUp(self):
        self.handlers = mock.MagicMock()

        signals.pre_init.connect(self.handlers.pre_init)
        signals.pre_save.connect(self.handlers.pre_save)
        signals.post_save.connect(self.handlers.post_save)

    def tearDown(self):
        signals.pre_init.disconnect(self.handlers.pre_init)
        signals.pre_save.disconnect(self.handlers.pre_save)
        signals.post_save.disconnect(self.handlers.post_save)

    def assertSignalsReactivated(self):
        WithSignalsFactory()

        self.assertEqual(self.handlers.pre_save.call_count, 1)
        self.assertEqual(self.handlers.post_save.call_count, 1)

    def test_context_manager(self):
        with factory.django.mute_signals(signals.pre_save, signals.post_save):
            WithSignalsFactory()

        self.assertEqual(self.handlers.pre_init.call_count, 1)
        self.assertFalse(self.handlers.pre_save.called)
        self.assertFalse(self.handlers.post_save.called)

        self.assertSignalsReactivated()

    def test_signal_cache(self):
        with factory.django.mute_signals(signals.pre_save, signals.post_save):
            signals.post_save.connect(self.handlers.mute_block_receiver)
            WithSignalsFactory()

        self.assertTrue(self.handlers.mute_block_receiver.call_count, 1)
        self.assertEqual(self.handlers.pre_init.call_count, 1)
        self.assertFalse(self.handlers.pre_save.called)
        self.assertFalse(self.handlers.post_save.called)

        self.assertSignalsReactivated()
        self.assertTrue(self.handlers.mute_block_receiver.call_count, 1)

    def test_class_decorator(self):
        @factory.django.mute_signals(signals.pre_save, signals.post_save)
        class WithSignalsDecoratedFactory(factory.django.DjangoModelFactory):
            class Meta:
                model = models.WithSignals

        WithSignalsDecoratedFactory()

        self.assertEqual(self.handlers.pre_init.call_count, 1)
        self.assertFalse(self.handlers.pre_save.called)
        self.assertFalse(self.handlers.post_save.called)

        self.assertSignalsReactivated()

    def test_class_decorator_with_subfactory(self):
        @factory.django.mute_signals(signals.pre_save, signals.post_save)
        class WithSignalsDecoratedFactory(factory.django.DjangoModelFactory):
            class Meta:
                model = models.WithSignals

            @factory.post_generation
            def post(obj, create, extracted, **kwargs):
                if not extracted:
                    WithSignalsDecoratedFactory.create(post=42)

        # This will disable the signals (twice), create two objects,
        # and reactivate the signals.
        WithSignalsDecoratedFactory()

        self.assertEqual(self.handlers.pre_init.call_count, 2)
        self.assertFalse(self.handlers.pre_save.called)
        self.assertFalse(self.handlers.post_save.called)

        self.assertSignalsReactivated()

    def test_class_decorator_build(self):
        @factory.django.mute_signals(signals.pre_save, signals.post_save)
        class WithSignalsDecoratedFactory(factory.django.DjangoModelFactory):
            class Meta:
                model = models.WithSignals

        WithSignalsDecoratedFactory.build()

        self.assertEqual(self.handlers.pre_init.call_count, 1)
        self.assertFalse(self.handlers.pre_save.called)
        self.assertFalse(self.handlers.post_save.called)

        self.assertSignalsReactivated()

    def test_function_decorator(self):
        @factory.django.mute_signals(signals.pre_save, signals.post_save)
        def foo():
            WithSignalsFactory()

        foo()

        self.assertEqual(self.handlers.pre_init.call_count, 1)
        self.assertFalse(self.handlers.pre_save.called)
        self.assertFalse(self.handlers.post_save.called)

        self.assertSignalsReactivated()

    def test_classmethod_decorator(self):
        class Foo(object):
            @classmethod
            @factory.django.mute_signals(signals.pre_save, signals.post_save)
            def generate(cls):
                WithSignalsFactory()

        Foo.generate()

        self.assertEqual(self.handlers.pre_init.call_count, 1)
        self.assertFalse(self.handlers.pre_save.called)
        self.assertFalse(self.handlers.post_save.called)

        self.assertSignalsReactivated()


@unittest.skipIf(django is None, "Django not installed.")
class DjangoCustomManagerTestCase(unittest.TestCase):

    def test_extra_args(self):
        # Our CustomManager will remove the 'arg=' argument.
        model = WithCustomManagerFactory(arg='foo')

    def test_with_manager_on_abstract(self):
        class ObjFactory(factory.django.DjangoModelFactory):
            class Meta:
                model = models.FromAbstractWithCustomManager

        # Our CustomManager will remove the 'arg=' argument,
        # invalid for the actual model.
        ObjFactory.create(arg='invalid')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
