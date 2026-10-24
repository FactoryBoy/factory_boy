# Copyright: See the LICENSE file.
# mypy: allow-untyped-defs, allow-incomplete-defs, no-check-untyped-defs

# A factory written the way the documentation shows it, without annotations.
# Type-checked by ``make test`` alongside ``test_typing.py``: the library's
# annotations must not turn documented, unannotated code into type errors.
# (mypy types the first parameter of these methods as the factory class.)

import dataclasses
import typing as T
import unittest

import factory


@dataclasses.dataclass
class User:
    id: int
    name: str
    email: str
    parents: T.Tuple[T.Any, ...]
    tags: T.List[str]


class UserFactory(factory.Factory[User]):
    class Meta:
        model = User

    @factory.sequence
    def id(n):
        return n

    @factory.lazy_attribute
    def name(self):
        return f"user{self.id}"

    @factory.lazy_attribute_sequence
    def email(self, n):
        return f"{self.name}+{n}@example.org"

    @factory.container_attribute
    def parents(self, containers):
        return containers

    tags = factory.LazyFunction(list)

    @factory.post_generation
    def tagged(self, create, extracted, **kwargs):
        self.tags.append("post")


class UnannotatedTypingTests(unittest.TestCase):

    def test_documented_decorators(self):
        user = UserFactory.build()
        self.assertEqual(f"user{user.id}", user.name)
        self.assertEqual((), user.parents)
        self.assertEqual(["post"], user.tags)
