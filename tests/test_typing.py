# Copyright: See the LICENSE file.

# This module (with test_typing_unannotated.py) is type-checked twice by ``make test``:
# - ``mypy tests/test_typing.py``, which also checks factory's own annotations;
# - ``mypy --strict --follow-imports=silent tests/test_typing.py``, which sees
#   factory the way a downstream project in strict mode does.
# Under ``--strict``, ``warn_unused_ignores`` turns each ``type: ignore`` below
# into an assertion: it fails if the annotation stops rejecting the call.

import dataclasses
import typing as T
import unittest

import factory


@dataclasses.dataclass
class User:
    name: str
    email: str
    id: int


@dataclasses.dataclass
class Company:
    name: str
    owner: User
    tags: T.List[str]
    country: str
    slug: str
    active: bool


class TypingTests(unittest.TestCase):

    def test_simple_factory(self) -> None:

        class UserFactory(factory.Factory[User]):
            name = "John Doe"
            email = "john.doe@example.org"
            id = 42

            class Meta:
                model = User

        result: User
        result = UserFactory.build()
        result = UserFactory.create()
        self.assertEqual(result.name, "John Doe")

    def test_declarations(self) -> None:

        class UserFactory(factory.Factory[User]):
            name = factory.Sequence(lambda n: f"user{n}")
            email = factory.LazyAttribute(lambda o: f"{o.name}@example.org")
            id = factory.LazyFunction(lambda: 42)

            class Meta:
                model = User

        def record(company: Company, create: bool, extracted: T.Any, **kwargs: T.Any) -> None:
            company.tags.append("post")

        class CompanyFactory(factory.Factory[Company]):
            name = factory.LazyAttributeSequence(lambda o, n: f"{o.country}-{n}")
            owner = factory.SubFactory(UserFactory, name="owner")
            tags = factory.List([factory.Iterator(["a", "b"])])
            country = factory.SelfAttribute("owner.name", default="?")
            slug = factory.Transformer("ACME", transform=str.lower)
            active = factory.Maybe("enabled", yes_declaration=True, no_declaration=False)
            recorded = factory.PostGeneration(record)

            class Meta:
                model = Company
                exclude = ("enabled",)

            class Params:
                enabled = factory.Trait(country="FR")

        company: Company = CompanyFactory.build(enabled=True)
        self.assertEqual("owner", company.owner.name)
        self.assertEqual(["a", "post"], company.tags)
        self.assertEqual("FR", company.country)
        self.assertEqual("acme", company.slug)
        self.assertTrue(company.active)

        users: T.List[User] = UserFactory.simple_generate_batch(False, 2)
        self.assertEqual(2, len(users))
        UserFactory.reset_sequence()

    def test_decorators(self) -> None:

        class UserFactory(factory.Factory[User]):
            class Meta:
                model = User

            @factory.sequence
            def id(n: int) -> int:
                return n + 100

            @factory.lazy_attribute
            def name(o: T.Any) -> str:
                return f"user{o.id}"

            @factory.lazy_attribute_sequence
            def email(o: T.Any, n: int) -> str:
                return f"{o.name}+{n}@example.org"

        user: User = UserFactory.build()
        self.assertEqual(f"user{user.id}", user.name)
        self.assertEqual(f"user{user.id}+{user.id - 100}@example.org", user.email)

    def test_helpers(self) -> None:
        user: User = factory.build(User, name="John", email="john@example.org", id=1)
        users: T.List[User] = factory.build_batch(User, 2, name="J", email="j@example.org", id=2)
        self.assertEqual("John", user.name)
        self.assertEqual(2, len(users))

    def test_rejected_arguments(self) -> None:
        # Each call is wrong at runtime too; only the declarations are built here.
        factory.Sequence(lambda: "no sequence number")  # type: ignore[arg-type,misc]
        factory.LazyFunction(lambda o: o)  # type: ignore[arg-type,misc]
        factory.SubFactory(User)  # type: ignore[arg-type]
        factory.RelatedFactoryList("tests.Factory", size="2")  # type: ignore[arg-type]
