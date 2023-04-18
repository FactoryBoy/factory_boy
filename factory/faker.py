# Copyright: See the LICENSE file.


"""Additional declarations for "faker" attributes.

Usage:

    class MyFactory(factory.Factory):
        class Meta:
            model = MyProfile

        first_name = factory.Faker('name')
"""


import contextlib

import faker
import faker.config

from . import declarations


class Faker(declarations.BaseDeclaration):
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
        super().__init__(
            locale=locale,
            **kwargs)

    def evaluate(self, instance, step, extra):
        locale = extra.pop('locale')
        subfaker = self._get_faker(locale)
        return subfaker.format(self.provider, **extra)

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

        return cls._FAKER_REGISTRY[locale]

    @classmethod
    def add_provider(cls, provider, locale=None):
        """Add a new Faker provider for the specified locale"""
        cls._get_faker(locale).add_provider(provider)
