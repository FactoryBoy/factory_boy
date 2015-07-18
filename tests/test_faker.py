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


import unittest

import faker.providers

import factory


class MockFaker(object):
    def __init__(self, expected):
        self.expected = expected

    def format(self, provider, **kwargs):
        return self.expected[provider]


class FakerTests(unittest.TestCase):
    def setUp(self):
        self._real_fakers = factory.Faker._FAKER_REGISTRY
        factory.Faker._FAKER_REGISTRY = {}

    def tearDown(self):
        factory.Faker._FAKER_REGISTRY = self._real_fakers

    def _setup_mock_faker(self, locale=None, **definitions):
        if locale is None:
            locale = factory.Faker._DEFAULT_LOCALE
        factory.Faker._FAKER_REGISTRY[locale] = MockFaker(definitions)

    def test_simple_biased(self):
        self._setup_mock_faker(name="John Doe")
        faker_field = factory.Faker('name')
        self.assertEqual("John Doe", faker_field.generate({}))

    def test_full_factory(self):
        class Profile(object):
            def __init__(self, first_name, last_name, email):
                self.first_name = first_name
                self.last_name = last_name
                self.email = email

        class ProfileFactory(factory.Factory):
            class Meta:
                model = Profile
            first_name = factory.Faker('first_name')
            last_name = factory.Faker('last_name', locale='fr_FR')
            email = factory.Faker('email')

        self._setup_mock_faker(first_name="John", last_name="Doe", email="john.doe@example.org")
        self._setup_mock_faker(first_name="Jean", last_name="Valjean", email="jvaljean@exemple.fr", locale='fr_FR')

        profile = ProfileFactory()
        self.assertEqual("John", profile.first_name)
        self.assertEqual("Valjean", profile.last_name)
        self.assertEqual('john.doe@example.org', profile.email)

    def test_override_locale(self):
        class Profile(object):
            def __init__(self, first_name, last_name):
                self.first_name = first_name
                self.last_name = last_name

        class ProfileFactory(factory.Factory):
            class Meta:
                model = Profile

            first_name = factory.Faker('first_name')
            last_name = factory.Faker('last_name', locale='fr_FR')

        self._setup_mock_faker(first_name="John", last_name="Doe")
        self._setup_mock_faker(first_name="Jean", last_name="Valjean", locale='fr_FR')
        self._setup_mock_faker(first_name="Johannes", last_name="Brahms", locale='de_DE')

        profile = ProfileFactory()
        self.assertEqual("John", profile.first_name)
        self.assertEqual("Valjean", profile.last_name)

        with factory.Faker.override_default_locale('de_DE'):
            profile = ProfileFactory()
            self.assertEqual("Johannes", profile.first_name)
            self.assertEqual("Valjean", profile.last_name)

        profile = ProfileFactory()
        self.assertEqual("John", profile.first_name)
        self.assertEqual("Valjean", profile.last_name)

    def test_add_provider(self):
        class Face(object):
            def __init__(self, smiley, french_smiley):
                self.smiley = smiley
                self.french_smiley = french_smiley

        class FaceFactory(factory.Factory):
            class Meta:
                model = Face

            smiley = factory.Faker('smiley')
            french_smiley = factory.Faker('smiley', locale='fr_FR')

        class SmileyProvider(faker.providers.BaseProvider):
            def smiley(self):
                return ':)'

        class FrenchSmileyProvider(faker.providers.BaseProvider):
            def smiley(self):
                return '(:'

        factory.Faker.add_provider(SmileyProvider)
        factory.Faker.add_provider(FrenchSmileyProvider, 'fr_FR')

        face = FaceFactory()
        self.assertEqual(":)", face.smiley)
        self.assertEqual("(:", face.french_smiley)
