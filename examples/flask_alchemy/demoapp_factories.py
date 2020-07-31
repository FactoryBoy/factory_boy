import demoapp

import factory.alchemy
import factory.fuzzy


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = demoapp.db.session


class UserFactory(BaseFactory):
    class Meta:
        model = demoapp.User

    username = factory.fuzzy.FuzzyText()
    email = factory.fuzzy.FuzzyText()


class UserLogFactory(BaseFactory):
    class Meta:
        model = demoapp.UserLog

    message = factory.fuzzy.FuzzyText()
    user = factory.SubFactory(UserFactory)
