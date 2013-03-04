Using factory_boy with ORMs
===========================

.. currentmodule:: factory


factory_boy provides custom :class:`Factory` subclasses for various ORMs,
adding dedicated features.


Django
------


The first versions of factory_boy were designed specifically for Django,
but the library has now evolved to be framework-independant.

Most features should thus feel quite familiar to Django users.

The :class:`DjangoModelFactory` subclass
"""""""""""""""""""""""""""""""""""""""""

All factories for a Django :class:`~django.db.models.Model` should use the
:class:`DjangoModelFactory` base class.


.. class:: DjangoModelFactory(Factory)

    Dedicated class for Django :class:`~django.db.models.Model` factories.

    This class provides the following features:

    * :func:`~Factory.create()` uses :meth:`Model.objects.create() <django.db.models.query.QuerySet.create>`
    * :func:`~Factory._setup_next_sequence()` selects the next unused primary key value
    * When using :class:`~factory.RelatedFactory` or :class:`~factory.PostGeneration`
      attributes, the base object will be :meth:`saved <django.db.models.Model.save>`
      once all post-generation hooks have run.
