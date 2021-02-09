# Copyright: See the LICENSE file.


"""Regression tests related to issues found with the project"""

import datetime
import typing as T
import unittest

import factory
from factory.alchemy import SQLAlchemyModelFactory

from .alchemyapp import models

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


class NameConflictTests(unittest.TestCase):
    def test_name_conflict_issue(self):
        """Regression test for `TypeError: _save() got multiple values for argument 'x'`

        See #775.
        """
        class SpecialFieldModel(models.Base):
            __tablename__ = 'SpecialFieldModelTable'

            id = models.Column(models.Integer(), primary_key=True)
            session = models.Column(models.Unicode(20))
            model_class = models.Column(models.Unicode(20))

        class ChildFactory(SQLAlchemyModelFactory):
            class Meta:
                model = SpecialFieldModel
                sqlalchemy_session = models.session

            id = factory.Sequence(lambda n: n)
            session = ''

        child = ChildFactory()
        self.assertIsNotNone(child.session)
