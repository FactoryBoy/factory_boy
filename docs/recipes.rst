Common recipes
==============


.. note:: Most recipes below take on Django model examples, but can also be used on their own.


Dependent objects (ForeignKey)
------------------------------

When one attribute is actually a complex field
(e.g a :class:`~django.db.models.ForeignKey` to another :class:`~django.db.models.Model`),
use the :class:`~factory.SubFactory` declaration:


.. code-block:: python

    # models.py
    class User(models.Model):
        first_name = models.CharField()
        group = models.ForeignKey(Group)


    # factories.py
    import factory
    from . import models

    class UserFactory(factory.DjangoModelFactory):
        FACTORY_FOR = models.User

        first_name = factory.Sequence(lambda n: "Agent %03d" % n)
        group = factory.SubFactory(GroupFactory)


Reverse dependencies (reverse ForeignKey)
-----------------------------------------

When a related object should be created upon object creation
(e.g a reverse :class:`~django.db.models.ForeignKey` from another :class:`~django.db.models.Model`),
use a :class:`~factory.RelatedFactory` declaration:


.. code-block:: python

    # models.py
    class User(models.Model):
        pass

    class UserLog(models.Model):
        user = models.ForeignKey(User)
        action = models.CharField()


    # factories.py
    class UserFactory(factory.DjangoModelFactory):
        FACTORY_FOR = models.User

        log = factory.RelatedFactory(UserLogFactory, 'user', action=models.UserLog.ACTION_CREATE)


When a :class:`UserFactory` is instantiated, factory_boy will call
``UserLogFactory(user=that_user, action=...)`` just before returning the created ``User``.


Copying fields to a SubFactory
------------------------------

When a field of a related class should match one of the container:


.. code-block:: python

    # models.py
    class Country(models.Model):
        name = models.CharField()
        lang = models.CharField()

    class User(models.Model):
        name = models.CharField()
        lang = models.CharField()
        country = models.ForeignKey(Country)

    class Company(models.Model):
        name = models.CharField()
        owner = models.ForeignKey(User)
        country = models.ForeignKey(Country)


Here, we want:

- The User to have the lang of its country (``factory.SelfAttribute('country.lang')``)
- The Company owner to live in the country of the company (``factory.SelfAttribute('..country')``)

.. code-block:: python

    # factories.py
    class CountryFactory(factory.DjangoModelFactory):
        FACTORY_FOR = models.Country

        name = factory.Iterator(["France", "Italy", "Spain"])
        lang = factory.Iterator(['fr', 'it', 'es'])

    class UserFactory(factory.DjangoModelFactory):
        FACTORY_FOR = models.User

        name = "John"
        lang = factory.SelfAttribute('country.lang')
        country = factory.SubFactory(CountryFactory)

    class CompanyFactory(factory.DjangoModelFactory):
        FACTORY_FOR = models.Company

        name = "ACME, Inc."
        country = factory.SubFactory(CountryFactory)
        owner = factory.SubFactory(UserFactory, country=factory.SelfAttribute('..country))
