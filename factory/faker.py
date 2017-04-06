# -*- coding: utf-8 -*-
# Copyright: See the LICENSE file.


"""Additional declarations for "faker" attributes.

Usage:

    class MyFactory(factory.Factory):
        class Meta:
            model = MyProfile

        first_name = factory.Faker('name')
"""


from __future__ import absolute_import
from __future__ import unicode_literals

import contextlib

import faker
import faker.config

from .random import get_random_state
from . import declarations


class Faker(declarations.OrderedDeclaration):
    """Wrapper for 'faker' values.

    Args:
        provider (str): the name of the Faker field
        locale (str): the locale to use for the faker

        All other kwargs will be passed to the underlying provider
        (e.g ``factory.Faker('ean', length=10)``
        calls ``faker.Faker.ean(length=10)``)

    Usage:
        >>> foo = factory.Faker('name')
    """
    def __init__(self, provider, locale=None, **kwargs):
        self.provider = provider
        self.provider_kwargs = kwargs
        self.locale = locale

    def generate(self, extra_kwargs):
        kwargs = {}
        kwargs.update(self.provider_kwargs)
        kwargs.update(extra_kwargs)
        subfaker = self._get_faker(self.locale)
        return subfaker.format(self.provider, **kwargs)

    def evaluate(self, sequence, obj, create, extra=None, containers=()):
        return self.generate(extra or {})

    _FAKER_REGISTRY = {}
    _DEFAULT_LOCALE = faker.config.DEFAULT_LOCALE

    @classmethod
    @contextlib.contextmanager
    def override_default_locale(cls, locale):
        old_locale = cls._DEFAULT_LOCALE
        cls._DEFAULT_LOCALE = locale
        try:
            yield
        finally:
            cls._DEFAULT_LOCALE = old_locale

    @classmethod
    def _get_faker(cls, locale=None):
        if locale is None:
            locale = cls._DEFAULT_LOCALE

        if locale not in cls._FAKER_REGISTRY:
            subfaker = faker.Faker(locale=locale)
            cls._FAKER_REGISTRY[locale] = subfaker

        cls._FAKER_REGISTRY[locale].random.setstate(get_random_state())
        return cls._FAKER_REGISTRY[locale]

    @classmethod
    def add_provider(cls, provider, locale=None):
        """Add a new Faker provider for the specified locale"""
        cls._get_faker(locale).add_provider(provider)
