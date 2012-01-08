Examples
========

Here are some real-world examples of using FactoryBoy.


Objects
-------

First, let's define a couple of objects::

    class Account(object):
        def __init__(self, username, email):
            self.username = username
            self.email = email

        def __str__(self):
            return '%s (%s)' % (self.username, self.email)


    class Profile(object):

        GENDER_MALE = 'm'
        GENDER_FEMALE = 'f'
        GENDER_UNKNOWN = 'u'  # If the user refused to give it

        def __init__(self, account, gender, firstname, lastname, planet='Earth'):
            self.account = account
            self.gender = gender
            self.firstname = firstname
            self.lastname = lastname
            self.planet = planet

        def __unicode__(self):
            return u'%s %s (%s)' % (
                unicode(self.firstname),
                unicode(self.lastname),
                unicode(self.account.accountname),
            )

Factories
---------

And now, we'll define the related factories::

    import factory
    import random

    from . import objects


    class AccountFactory(factory.Factory):
        FACTORY_FOR = objects.Account

        username = factory.Sequence(lambda n: 'john%s' % n)
        email = factory.LazyAttribute(lambda o: '%s@example.org' % o.username)


    class ProfileFactory(factory.Factory):
        FACTORY_FOR = objects.Profile

        account = factory.SubFactory(AccountFactory)
        gender = random.choice([objects.Profile.GENDER_MALE, objects.Profile.GENDER_FEMALE])
        firstname = u'John'
        lastname = u'Doe'



We have now defined basic factories for our :py:class:`~Account` and :py:class:`~Profile` classes.

If we commonly use a specific variant of our objects, we can refine a factory accordingly::

    class FemaleProfileFactory(ProfileFactory):
        gender = objects.Profile.GENDER_FEMALE
        firstname = u'Jane'
        user__username = factory.Sequence(lambda n: 'jane%s' % n)



Using the factories
-------------------

We can now use our factories, for tests::

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

            for _ in xrange(4):
                profiles.append(factories.ProfileFactory())
            for _ in xrange(2):
                profiles.append(factories.FemaleProfileFactory())
            for _ in xrange(2):
                profiles.append(factories.ProfileFactory(planet='Tatooine'))

            stats = business_logic.profile_stats(profiles)
            self.assertEqual({'Earth': 6, 'Mars': 2}, stats.planets)
            self.assertLess(stats.genders[objects.Profile.GENDER_FEMALE], 2)


Or for fixtures::

    from . import factories

    def make_objects():
        for _ in xrange(50):
            factories.ProfileFactory()

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
