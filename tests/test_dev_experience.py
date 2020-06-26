# Copyright: See the LICENSE file.

"""Tests about developer experience: help messages, errors, etc."""

import collections
import unittest

import factory
import factory.errors

Country = collections.namedtuple('Country', ['name', 'continent', 'capital_city'])
City = collections.namedtuple('City', ['name', 'population'])


class DeclarationTests(unittest.TestCase):
    def test_subfactory_to_model(self):
        """A helpful error message occurs when pointing a subfactory to a model."""
        class CountryFactory(factory.Factory):
            class Meta:
                model = Country

            name = factory.Faker('country')
            continent = "Antarctica"

            # Error here: pointing the SubFactory to a model, not a factory.
            capital_city = factory.SubFactory(City)

        with self.assertRaises(factory.errors.AssociatedClassError) as raised:
            CountryFactory()

        self.assertIn('City', str(raised.exception))
        self.assertIn('Country', str(raised.exception))

    def test_subfactory_to_factorylike_model(self):
        """A helpful error message occurs when pointing a subfactory to a model.

        This time with a model that looks more like a factory (ie has a `._meta`)."""

        class CityModel:
            _meta = None
            name = "Coruscant"
            population = 0

        class CountryFactory(factory.Factory):
            class Meta:
                model = Country

            name = factory.Faker('country')
            continent = "Antarctica"

            # Error here: pointing the SubFactory to a model, not a factory.
            capital_city = factory.SubFactory(CityModel)

        with self.assertRaises(factory.errors.AssociatedClassError) as raised:
            CountryFactory()

        self.assertIn('CityModel', str(raised.exception))
        self.assertIn('Country', str(raised.exception))
