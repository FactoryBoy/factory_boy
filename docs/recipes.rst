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


Simple ManyToMany
-----------------

Building the adequate link between two models depends heavily on the use case;
factory_boy doesn't provide a "all in one tools" as for :class:`~factory.SubFactory`
or :class:`~factory.RelatedFactory`, users will have to craft their own depending
on the model.

The base building block for this feature is the :class:`~factory.post_generation`
hook:

.. code-block:: python

    # models.py
    class Group(models.Model):
        name = models.CharField()

    class User(models.Model):
        name = models.CharField()
        groups = models.ManyToMany(Group)


    # factories.py
    class GroupFactory(factory.DjangoModelFactory):
        FACTORY_FOR = models.Group

        name = factory.Sequence(lambda n: "Group #%s" % n)

    class UserFactory(factory.DjangoModelFactory):
        FACTORY_FOR = models.User

        name = "John Doe"

        @factory.post_generation
        def groups(self, create, extracted, **kwargs):
            if not create:
                # Simple build, do nothing.
                return

            if extracted:
                # A list of groups were passed in, use them
                for group in extracted:
                    self.groups.add(group)

.. OHAI_VIM**

When calling ``UserFactory()`` or ``UserFactory.build()``, no group binding
will be created.

But when ``UserFactory.create(groups=(group1, group2, group3))`` is called,
the ``groups`` declaration will add passed in groups to the set of groups for the
user.


ManyToMany with a 'through'
---------------------------


If only one link is required, this can be simply performed with a :class:`RelatedFactory`.
If more links are needed, simply add more :class:`RelatedFactory` declarations:

.. code-block:: python

    # models.py
    class User(models.Model):
        name = models.CharField()

    class Group(models.Model):
        name = models.CharField()
        members = models.ManyToMany(User, through='GroupLevel')

    class GroupLevel(models.Model):
        user = models.ForeignKey(User)
        group = models.ForeignKey(Group)
        rank = models.IntegerField()


    # factories.py
    class UserFactory(factory.DjangoModelFactory):
        FACTORY_FOR = models.User

        name = "John Doe"

    class GroupFactory(factory.DjangoModelFactory):
        FACTORY_FOR = models.Group

        name = "Admins"

    class GroupLevelFactory(factory.DjangoModelFactory):
        FACTORY_FOR = models.GroupLevel

        user = factory.SubFactory(UserFactory)
        group = factory.SubFactory(GroupFactory)
        rank = 1

    class UserWithGroupFactory(UserFactory):
        membership = factory.RelatedFactory(GroupLevelFactory, 'user')

    class UserWith2GroupsFactory(UserFactory):
        membership1 = factory.RelatedFactory(GroupLevelFactory, 'user', group__name='Group1')
        membership2 = factory.RelatedFactory(GroupLevelFactory, 'user', group__name='Group2')


Whenever the ``UserWithGroupFactory`` is called, it will, as a post-generation hook,
call the ``GroupLevelFactory``, passing the generated user as a ``user`` field:

1. ``UserWithGroupFactory()`` generates a ``User`` instance, ``obj``
2. It calls ``GroupLevelFactory(user=obj)``
3. It returns ``obj``


When using the ``UserWith2GroupsFactory``, that behavior becomes:

1. ``UserWith2GroupsFactory()`` generates a ``User`` instance, ``obj``
2. It calls ``GroupLevelFactory(user=obj, group__name='Group1')``
3. It calls ``GroupLevelFactory(user=obj, group__name='Group2')``
4. It returns ``obj``


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
        owner = factory.SubFactory(UserFactory, country=factory.SelfAttribute('..country'))
