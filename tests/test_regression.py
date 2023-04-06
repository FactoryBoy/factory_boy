# Copyright: See the LICENSE file.


"""Regression tests related to issues found with the project"""

import datetime
import typing as T
import unittest

import factory

# Example objects
# ===============


class Author(T.NamedTuple):
    fullname: str
    pseudonym: T.Optional[str] = None


class Book(T.NamedTuple):
    title: str
    author: Author


class PublishedBook(T.NamedTuple):
    book: Book
    published_on: datetime.date
    countries: T.List[str]


class FakerRegressionTests(unittest.TestCase):
    def test_locale_issue(self):
        """Regression test for `KeyError: 'locale'`

        See #785 #786 #787 #788 #790 #796.
        """
        class AuthorFactory(factory.Factory):
            class Meta:
                model = Author

            class Params:
                unknown = factory.Trait(
                    fullname="",
                )

            fullname = factory.Faker("name")

        public_author = AuthorFactory(unknown=False)
        self.assertIsNone(public_author.pseudonym)

        unknown_author = AuthorFactory(unknown=True)
        self.assertEqual("", unknown_author.fullname)

    def test_evaluated_without_locale(self):
        """Regression test for `KeyError: 'locale'` raised in `evaluate`.

        See #965

        """
        class AuthorFactory(factory.Factory):
            fullname = factory.Faker("name")
            pseudonym = factory.Maybe(
                decider=factory.Faker("pybool"),
                yes_declaration="yes",
                no_declaration="no",
            )

            class Meta:
                model = Author

        author = AuthorFactory()

        self.assertIn(author.pseudonym, ["yes", "no"])
