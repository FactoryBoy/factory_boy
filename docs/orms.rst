Using factory_boy with ORMs
===========================

.. currentmodule:: factory


factory_boy provides custom :class:`Factory` subclasses for various ORMs,
adding dedicated features.


Django
------

.. currentmodule:: factory.django


The first versions of factory_boy were designed specifically for Django,
but the library has now evolved to be framework-independant.

Most features should thus feel quite familiar to Django users.

The :class:`DjangoModelFactory` subclass
"""""""""""""""""""""""""""""""""""""""""

All factories for a Django :class:`~django.db.models.Model` should use the
:class:`DjangoModelFactory` base class.


.. class:: DjangoModelFactory(factory.Factory)

    Dedicated class for Django :class:`~django.db.models.Model` factories.

    This class provides the following features:

    * :func:`~factory.Factory.create()` uses :meth:`Model.objects.create() <django.db.models.query.QuerySet.create>`
    * :func:`~factory.Factory._setup_next_sequence()` selects the next unused primary key value
    * When using :class:`~factory.RelatedFactory` or :class:`~factory.PostGeneration`
      attributes, the base object will be :meth:`saved <django.db.models.Model.save>`
      once all post-generation hooks have run.

    .. attribute:: FACTORY_DJANGO_GET_OR_CREATE

        Fields whose name are passed in this list will be used to perform a
        :meth:`Model.objects.get_or_create() <django.db.models.query.QuerySet.get_or_create>`
        instead of the usual :meth:`Model.objects.create() <django.db.models.query.QuerySet.create>`:

        .. code-block:: python

            class UserFactory(factory.django.DjangoModelFactory):
                FACTORY_FOR = models.User
                FACTORY_DJANGO_GET_OR_CREATE = ('username',)

                username = 'john'

        .. code-block:: pycon

            >>> User.objects.all()
            []
            >>> UserFactory()                   # Creates a new user
            <User: john>
            >>> User.objects.all()
            [<User: john>]

            >>> UserFactory()                   # Fetches the existing user
            <User: john>
            >>> User.objects.all()              # No new user!
            [<User: john>]

            >>> UserFactory(username='jack')    # Creates another user
            <User: jack>
            >>> User.objects.all()
            [<User: john>, <User: jack>]


Mogo
----

.. currentmodule:: factory.mogo

factory_boy supports `Mogo`_-style models, through the :class:`MogoFactory` class.

`Mogo`_ is a wrapper around the ``pymongo`` library for MongoDB.

.. _Mogo: https://github.com/joshmarshall/mogo

.. class:: MogoFactory(factory.Factory)

    Dedicated class for `Mogo`_ models.

    This class provides the following features:

    * :func:`~factory.Factory.build()` calls a model's ``new()`` method
    * :func:`~factory.Factory.create()` builds an instance through ``new()`` then
      saves it.
