# Copyright: See the LICENSE file.

import dataclasses
import unittest

import factory


@dataclasses.dataclass
class User:
    name: str
    email: str
    id: int


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
