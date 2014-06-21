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


from __future__ import absolute_import
from __future__ import unicode_literals

import os
import types
import logging
import functools

"""factory_boy extensions for use with the Django framework."""

try:
    from django.core import files as django_files
except ImportError as e:  # pragma: no cover
    django_files = None
    import_failure = e


from . import base
from . import declarations
from .compat import BytesIO, is_string

logger = logging.getLogger('factory.generate')



def require_django():
    """Simple helper to ensure Django is available."""
    if django_files is None:  # pragma: no cover
        raise import_failure


class DjangoOptions(base.FactoryOptions):
    def _build_default_options(self):
        return super(DjangoOptions, self)._build_default_options() + [
            base.OptionDefault('django_get_or_create', (), inherit=True),
        ]

    def _get_counter_reference(self):
        counter_reference = super(DjangoOptions, self)._get_counter_reference()
        if (counter_reference == self.base_factory
                and self.base_factory._meta.model is not None
                and self.base_factory._meta.model._meta.abstract
                and self.model is not None
                and not self.model._meta.abstract):
            # Target factory is for an abstract model, yet we're for another,
            # concrete subclass => don't reuse the counter.
            return self.factory
        return counter_reference


class DjangoModelFactory(base.Factory):
    """Factory for Django models.

    This makes sure that the 'sequence' field of created objects is a new id.

    Possible improvement: define a new 'attribute' type, AutoField, which would
    handle those for non-numerical primary keys.
    """

    _options_class = DjangoOptions
    class Meta:
        abstract = True  # Optional, but explicit.

    _OLDSTYLE_ATTRIBUTES = base.Factory._OLDSTYLE_ATTRIBUTES.copy()
    _OLDSTYLE_ATTRIBUTES.update({
        'FACTORY_DJANGO_GET_OR_CREATE': 'django_get_or_create',
    })

    @classmethod
    def _load_model_class(cls, definition):

        if is_string(definition) and '.' in definition:
            app, model = definition.split('.', 1)
            from django.db.models import loading as django_loading
            return django_loading.get_model(app, model)

        return definition

    @classmethod
    def _get_manager(cls, model_class):
        if model_class is None:
            raise base.AssociatedClassError("No model set on %s.%s.Meta"
                    % (cls.__module__, cls.__name__))
        try:
            return model_class._default_manager   # pylint: disable=W0212
        except AttributeError:
            return model_class.objects

    @classmethod
    def _setup_next_sequence(cls):
        """Compute the next available PK, based on the 'pk' database field."""

        model = cls._get_model_class()  # pylint: disable=E1101
        manager = cls._get_manager(model)

        try:
            return 1 + manager.values_list('pk', flat=True
                ).order_by('-pk')[0]
        except (IndexError, TypeError):
            # IndexError: No instance exist yet
            # TypeError: pk isn't an integer type
            return 1

    @classmethod
    def _get_or_create(cls, model_class, *args, **kwargs):
        """Create an instance of the model through objects.get_or_create."""
        manager = cls._get_manager(model_class)

        assert 'defaults' not in cls._meta.django_get_or_create, (
            "'defaults' is a reserved keyword for get_or_create "
            "(in %s._meta.django_get_or_create=%r)"
            % (cls, cls._meta.django_get_or_create))

        key_fields = {}
        for field in cls._meta.django_get_or_create:
            key_fields[field] = kwargs.pop(field)
        key_fields['defaults'] = kwargs

        obj, _created = manager.get_or_create(*args, **key_fields)
        return obj

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Create an instance of the model, and save it to the database."""
        manager = cls._get_manager(model_class)

        if cls._meta.django_get_or_create:
            return cls._get_or_create(model_class, *args, **kwargs)

        return manager.create(*args, **kwargs)

    @classmethod
    def _after_postgeneration(cls, obj, create, results=None):
        """Save again the instance if creating and at least one hook ran."""
        if create and results:
            # Some post-generation hooks ran, and may have modified us.
            obj.save()


class FileField(declarations.PostGenerationDeclaration):
    """Helper to fill in django.db.models.FileField from a Factory."""

    DEFAULT_FILENAME = 'example.dat'

    def __init__(self, **defaults):
        require_django()
        self.defaults = defaults
        super(FileField, self).__init__()

    def _make_data(self, params):
        """Create data for the field."""
        return params.get('data', b'')

    def _make_content(self, extraction_context):
        path = ''
        params = dict(self.defaults)
        params.update(extraction_context.extra)

        if params.get('from_path') and params.get('from_file'):
            raise ValueError(
                "At most one argument from 'from_file' and 'from_path' should "
                "be non-empty when calling factory.django.FileField."
            )

        if extraction_context.did_extract:
            # Should be a django.core.files.File
            content = extraction_context.value
            path = content.name

        elif params.get('from_path'):
            path = params['from_path']
            f = open(path, 'rb')
            content = django_files.File(f, name=path)

        elif params.get('from_file'):
            f = params['from_file']
            content = django_files.File(f)
            path = content.name

        else:
            data = self._make_data(params)
            content = django_files.base.ContentFile(data)

        if path:
            default_filename = os.path.basename(path)
        else:
            default_filename = self.DEFAULT_FILENAME

        filename = params.get('filename', default_filename)
        return filename, content

    def call(self, obj, create, extraction_context):
        """Fill in the field."""
        if extraction_context.did_extract and extraction_context.value is None:
            # User passed an empty value, don't fill
            return

        filename, content = self._make_content(extraction_context)
        field_file = getattr(obj, extraction_context.for_field)
        try:
            field_file.save(filename, content, save=create)
        finally:
            content.file.close()
        return field_file


class ImageField(FileField):
    DEFAULT_FILENAME = 'example.jpg'

    def _make_data(self, params):
        # ImageField (both django's and factory_boy's) require PIL.
        # Try to import it along one of its known installation paths.
        try:
            from PIL import Image
        except ImportError:
            import Image

        width = params.get('width', 100)
        height = params.get('height', width)
        color = params.get('color', 'blue')
        image_format = params.get('format', 'JPEG')

        thumb = Image.new('RGB', (width, height), color)
        thumb_io = BytesIO()
        thumb.save(thumb_io, format=image_format)
        return thumb_io.getvalue()


class mute_signals(object):
    """Temporarily disables and then restores any django signals.

    Args:
        *signals (django.dispatch.dispatcher.Signal): any django signals

    Examples:
        with mute_signals(pre_init):
            user = UserFactory.build()
            ...

        @mute_signals(pre_save, post_save)
        class UserFactory(factory.Factory):
            ...

        @mute_signals(post_save)
        def generate_users():
            UserFactory.create_batch(10)
    """

    def __init__(self, *signals):
        self.signals = signals
        self.paused = {}

    def __enter__(self):
        for signal in self.signals:
            logger.debug('mute_signals: Disabling signal handlers %r',
                         signal.receivers)

            self.paused[signal] = signal.receivers
            signal.receivers = []

    def __exit__(self, exc_type, exc_value, traceback):
        for signal, receivers in self.paused.items():
            logger.debug('mute_signals: Restoring signal handlers %r',
                         receivers)

            signal.receivers = receivers
        self.paused = {}

    def __call__(self, callable_obj):
        if isinstance(callable_obj, base.FactoryMetaClass):
            # Retrieve __func__, the *actual* callable object.
            generate_method = callable_obj._generate.__func__

            @classmethod
            @functools.wraps(generate_method)
            def wrapped_generate(*args, **kwargs):
                with self:
                    return generate_method(*args, **kwargs)

            callable_obj._generate = wrapped_generate
            return callable_obj

        else:
            @functools.wraps(callable_obj)
            def wrapper(*args, **kwargs):
                with self:
                    return callable_obj(*args, **kwargs)
            return wrapper

