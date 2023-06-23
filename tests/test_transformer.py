# Copyright: See the LICENSE file.

from unittest import TestCase

import factory


class TransformCounter:
    calls_count = 0

    @classmethod
    def __call__(cls, x):
        cls.calls_count += 1
        return x.upper()

    @classmethod
    def reset(cls):
        cls.calls_count = 0


transform = TransformCounter()


class Upper:
    def __init__(self, name, **extra):
        self.name = name
        self.extra = extra


class UpperFactory(factory.Factory):
    name = factory.Transformer("value", transform=transform)

    class Meta:
        model = Upper


class TransformerTest(TestCase):
    def setUp(self):
        transform.reset()

    def test_transform_count(self):
        self.assertEqual("VALUE", UpperFactory().name)
        self.assertEqual(transform.calls_count, 1)

    def test_transform_kwarg(self):
        self.assertEqual("TEST", UpperFactory(name="test").name)
        self.assertEqual(transform.calls_count, 1)
        self.assertEqual("VALUE", UpperFactory().name)
        self.assertEqual(transform.calls_count, 2)

    def test_transform_faker(self):
        value = UpperFactory(name=factory.Faker("first_name_female", locale="fr")).name
        self.assertIs(value.isupper(), True)

    def test_transform_linked(self):
        value = UpperFactory(
            name=factory.LazyAttribute(lambda o: o.username.replace(".", " ")),
            username="john.doe",
        ).name
        self.assertEqual(value, "JOHN DOE")

    def test_force_value(self):
        value = UpperFactory(name=factory.Transformer.Force("Mia")).name
        self.assertEqual(value, "Mia")

    def test_force_value_declaration(self):
        """Pretty unlikely use case, but easy enough to cover."""
        value = UpperFactory(
            name=factory.Transformer.Force(
                factory.LazyFunction(lambda: "infinity")
            )
        ).name
        self.assertEqual(value, "infinity")

    def test_force_value_declaration_context(self):
        """Ensure "forced" values run at the right level."""
        value = UpperFactory(
            name=factory.Transformer.Force(
                factory.LazyAttribute(lambda o: o.username.replace(".", " ")),
            ),
            username="john.doe",
        ).name
        self.assertEqual(value, "john doe")


class TestObject:
    def __init__(self, one=None, two=None, three=None):
        self.one = one
        self.two = two
        self.three = three


class TransformDeclarationFactory(factory.Factory):
    class Meta:
        model = TestObject
    one = factory.Transformer("", transform=str.upper)
    two = factory.Transformer(factory.Sequence(int), transform=lambda n: n ** 2)


class TransformerSequenceTest(TestCase):
    def test_on_sequence(self):
        instance = TransformDeclarationFactory(__sequence=2)
        self.assertEqual(instance.one, "")
        self.assertEqual(instance.two, 4)
        self.assertIsNone(instance.three)

    def test_on_user_supplied(self):
        """A transformer can wrap a call-time declaration"""
        instance = TransformDeclarationFactory(
            one=factory.Sequence(str),
            two=2,
            __sequence=2,
        )
        self.assertEqual(instance.one, "2")
        self.assertEqual(instance.two, 4)
        self.assertIsNone(instance.three)


class WithMaybeFactory(factory.Factory):
    class Meta:
        model = TestObject

    one = True
    two = factory.Maybe(
        'one',
        yes_declaration=factory.Transformer("yes", transform=str.upper),
        no_declaration=factory.Transformer("no", transform=str.upper),
    )
    three = factory.Maybe('one', no_declaration=factory.Transformer("three", transform=str.upper))


class TransformerMaybeTest(TestCase):
    def test_default_transform(self):
        instance = WithMaybeFactory()
        self.assertIs(instance.one, True)
        self.assertEqual(instance.two, "YES")
        self.assertIsNone(instance.three)

    def test_yes_transform(self):
        instance = WithMaybeFactory(one=True)
        self.assertIs(instance.one, True)
        self.assertEqual(instance.two, "YES")
        self.assertIsNone(instance.three)

    def test_no_transform(self):
        instance = WithMaybeFactory(one=False)
        self.assertIs(instance.one, False)
        self.assertEqual(instance.two, "NO")
        self.assertEqual(instance.three, "THREE")

    def test_override(self):
        instance = WithMaybeFactory(one=True, two="NI")
        self.assertIs(instance.one, True)
        self.assertEqual(instance.two, "NI")
        self.assertIsNone(instance.three)


class RelatedTest(TestCase):
    def test_default_transform(self):
        cities = []

        class City:
            def __init__(self, capital_of, name):
                self.capital_of = capital_of
                self.name = name
                cities.append(self)

        class Country:
            def __init__(self, name):
                self.name = name

        class CityFactory(factory.Factory):
            class Meta:
                model = City

            name = "Rennes"

        class CountryFactory(factory.Factory):
            class Meta:
                model = Country

            name = "France"
            capital_city = factory.RelatedFactory(
                CityFactory,
                factory_related_name="capital_of",
                name=factory.Transformer("Paris", transform=str.upper),
            )

        instance = CountryFactory()
        self.assertEqual(instance.name, "France")
        [city] = cities
        self.assertEqual(city.capital_of, instance)
        self.assertEqual(city.name, "PARIS")


class WithTraitFactory(factory.Factory):
    class Meta:
        model = TestObject

    class Params:
        upper_two = factory.Trait(
            two=factory.Transformer("two", transform=str.upper)
        )
        odds = factory.Trait(
            one="one",
            three="three",
        )
    one = factory.Transformer("one", transform=str.upper)


class TransformerTraitTest(TestCase):
    def test_traits_off(self):
        instance = WithTraitFactory()
        self.assertEqual(instance.one, "ONE")
        self.assertIsNone(instance.two)
        self.assertIsNone(instance.three)

    def test_trait_transform_applies(self):
        """A trait-provided transformer should apply to existing values"""
        instance = WithTraitFactory(upper_two=True)
        self.assertEqual(instance.one, "ONE")
        self.assertEqual(instance.two, "TWO")
        self.assertIsNone(instance.three)

    def test_trait_transform_applies_supplied(self):
        """A trait-provided transformer should be overridden by caller-provided values"""
        instance = WithTraitFactory(upper_two=True, two="two")
        self.assertEqual(instance.one, "ONE")
        self.assertEqual(instance.two, "two")
        self.assertIsNone(instance.three)
