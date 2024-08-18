Examples
========

Here are some real-world examples of using FactoryBoy.


Objects
-------

First, let's define a couple of objects:


.. code-block:: python

    class Account:
        def __init__(self, username, email, date_joined):
            self.username = username
            self.email = email
            self.date_joined = date_joined

        def __str__(self):
            return '%s (%s)' % (self.username, self.email)


    class Profile:

        GENDER_MALE = 'm'
        GENDER_FEMALE = 'f'
        GENDER_UNKNOWN = 'u'  # If the user refused to give it

        def __init__(self, account, gender, firstname, lastname, planet='Earth'):
            self.account = account
            self.gender = gender
            self.firstname = firstname
            self.lastname = lastname
            self.planet = planet

        def __str__(self):
            return '%s %s (%s)' % (
                self.firstname,
                self.lastname,
                self.account.username,
            )

Factories
---------

And now, we'll define the related factories:


.. code-block:: python

    import datetime
    import factory

    from . import objects


    class AccountFactory(factory.Factory):
        class Meta:
            model = objects.Account

        username = factory.Sequence(lambda n: 'john%s' % n)
        email = factory.LazyAttribute(lambda o: '%s@example.org' % o.username)
        date_joined = factory.LazyFunction(datetime.datetime.now)


    class ProfileFactory(factory.Factory):
        class Meta:
            model = objects.Profile

        account = factory.SubFactory(AccountFactory)
        gender = factory.Iterator([objects.Profile.GENDER_MALE, objects.Profile.GENDER_FEMALE])
        firstname = 'John'
        lastname = 'Doe'



We have now defined basic factories for our ``Account`` and ``Profile`` classes.

If we commonly use a specific variant of our objects, we can refine a factory accordingly:


.. code-block:: python

    class FemaleProfileFactory(ProfileFactory):
        gender = objects.Profile.GENDER_FEMALE
        firstname = 'Jane'
        account__username = factory.Sequence(lambda n: 'jane%s' % n)



Using the factories
-------------------

We can now use our factories, for tests:


.. code-block:: python

    import unittest

    from . import business_logic
    from . import factories
    from . import objects


    class MyTestCase(unittest.TestCase):

        def test_send_mail(self):
            account = factories.AccountFactory()
            email = business_logic.prepare_email(account, subject='Foo', text='Bar')

            self.assertEqual(email.to, account.email)

        def test_get_profile_stats(self):
            profiles = []

            profiles.extend(factories.ProfileFactory.create_batch(4))
            profiles.extend(factories.FemaleProfileFactory.create_batch(2))
            profiles.extend(factories.ProfileFactory.create_batch(2, planet="Tatooine"))

            stats = business_logic.profile_stats(profiles)
            self.assertEqual({'Earth': 6, 'Mars': 2}, stats.planets)
            self.assertLess(stats.genders[objects.Profile.GENDER_FEMALE], 2)


Or for fixtures:

.. code-block:: python

    from . import factories

    def make_objects():
        factories.ProfileFactory.create_batch(size=50)

        # Let's create a few, known objects.
        factories.ProfileFactory(
            gender=objects.Profile.GENDER_MALE,
            firstname='Luke',
            lastname='Skywalker',
            planet='Tatooine',
        )

        factories.ProfileFactory(
            gender=objects.Profile.GENDER_FEMALE,
            firstname='Leia',
            lastname='Organa',
            planet='Alderaan',
        )
