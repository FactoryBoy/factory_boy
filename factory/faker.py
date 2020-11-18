# Copyright: See the LICENSE file.


"""Additional declarations for "faker" attributes.

Usage:

    class MyFactory(factory.Factory):
        class Meta:
            model = MyProfile

        first_name = factory.Faker('name')
"""


import contextlib

import faker as faker_lib
import faker.config as faker_lib_config

from . import declarations


class Faker(declarations.ParameteredDeclaration):
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
    def __init__(self, provider, **kwargs):
        locale = kwargs.pop('locale', None)
        self.provider = provider
        self.local_faker_instances = {}
        super().__init__(
            locale=locale,
            **kwargs)

    def generate(self, params):
        locale = params.pop('locale')
        unique = params.pop('unique', False)
        if unique:
            subfaker = self._get_local_faker(locale).unique
        else:
            subfaker = self._get_faker(locale)

        return subfaker.format(self.provider, **params)

    _FAKER_REGISTRY = {}
    _DEFAULT_LOCALE = faker_lib_config.DEFAULT_LOCALE

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
            subfaker = faker_lib.Faker(locale=locale)
            cls._FAKER_REGISTRY[locale] = subfaker

        return cls._FAKER_REGISTRY[locale]

    def _get_local_faker(self, locale):
        if locale is None:
            locale = self._DEFAULT_LOCALE

        local_instance = self.local_faker_instances.get(locale)
        if not local_instance:
            self.local_faker_instances[locale] = faker_lib.Faker(locale=locale)
        return self.local_faker_instances[locale]

    @classmethod
    def add_provider(cls, provider, locale=None):
        """Add a new Faker provider for the specified locale"""
        cls._get_faker(locale).add_provider(provider)
