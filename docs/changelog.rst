ChangeLog
=========


.. _v2.1.1:

2.1.1 (2013-07-02)
------------------

*Bugfix:*

    - Properly retrieve the ``color`` keyword argument passed to :class:`~factory.django.ImageField`

.. _v2.1.0:

2.1.0 (2013-06-26)
------------------

*New:*

    - Add :class:`~factory.fuzzy.FuzzyDate` thanks to `saulshanabrook <https://github.com/saulshanabrook>`_
    - Add :class:`~factory.fuzzy.FuzzyDateTime` and :class:`~factory.fuzzy.FuzzyNaiveDateTime`.
    - Add a :attr:`~factory.containers.LazyStub.factory_parent` attribute to the
      :class:`~factory.containers.LazyStub` passed to :class:`~factory.LazyAttribute`, in order to access
      fields defined in wrapping factories.
    - Move :class:`~factory.django.DjangoModelFactory` and :class:`~factory.mogo.MogoFactory`
      to their own modules (:mod:`factory.django` and :mod:`factory.mogo`)
    - Add the :meth:`~factory.Factory.reset_sequence` classmethod to :class:`~factory.Factory`
      to ease resetting the sequence counter for a given factory.
    - Add debug messages to ``factory`` logger.
    - Add a :meth:`~factory.Iterator.reset` method to :class:`~factory.Iterator` (:issue:`63`)
    - Add support for the SQLAlchemy ORM through :class:`~factory.alchemy.SQLAlchemyModelFactory`
      (:issue:`64`, thanks to `Romain Commandé <https://github.com/rcommande>`_)
    - Add :class:`factory.django.FileField` and :class:`factory.django.ImageField` hooks for
      related Django model fields (:issue:`52`)

*Bugfix*

    - Properly handle non-integer pks in :class:`~factory.django.DjangoModelFactory` (:issue:`57`).
    - Disable :class:`~factory.RelatedFactory` generation when a specific value was
      passed (:issue:`62`, thanks to `Gabe Koscky <https://github.com/dhekke>`_)

*Deprecation:*

    - Rename :class:`~factory.RelatedFactory`'s ``name`` argument to ``factory_related_name`` (See :issue:`58`)


.. _v2.0.2:

2.0.2 (2013-04-16)
------------------

*New:*

    - When :attr:`~factory.django.DjangoModelFactory.FACTORY_DJANGO_GET_OR_CREATE` is
      empty, use ``Model.objects.create()`` instead of ``Model.objects.get_or_create``.


.. _v2.0.1:

2.0.1 (2013-04-16)
------------------

*New:*

    - Don't push ``defaults`` to ``get_or_create`` when
      :attr:`~factory.django.DjangoModelFactory.FACTORY_DJANGO_GET_OR_CREATE` is not set.


.. _v2.0.0:

2.0.0 (2013-04-15)
------------------

*New:*

    - Allow overriding the base factory class for :func:`~factory.make_factory` and friends.
    - Add support for Python3 (Thanks to `kmike <https://github.com/kmike>`_ and `nkryptic <https://github.com/nkryptic>`_)
    - The default :attr:`~factory.Sequence.type` for :class:`~factory.Sequence` is now :obj:`int`
    - Fields listed in :attr:`~factory.Factory.FACTORY_HIDDEN_ARGS` won't be passed to
      the associated class' constructor
    - Add support for ``get_or_create`` in :class:`~factory.django.DjangoModelFactory`,
      through :attr:`~factory.django.DjangoModelFactory.FACTORY_DJANGO_GET_OR_CREATE`.
    - Add support for :mod:`~factory.fuzzy` attribute definitions.
    - The :class:`Sequence` counter can be overridden when calling a generating function
    - Add :class:`~factory.Dict` and :class:`~factory.List` declarations (Closes :issue:`18`).

*Removed:*

    - Remove associated class discovery
    - Remove :class:`~factory.InfiniteIterator` and :func:`~factory.infinite_iterator`
    - Remove :class:`~factory.CircularSubFactory`
    - Remove ``extract_prefix`` kwarg to post-generation hooks.
    - Stop defaulting to Django's ``Foo.objects.create()`` when "creating" instances
    - Remove STRATEGY_*
    - Remove :meth:`~factory.Factory.set_building_function` / :meth:`~factory.Factory.set_creation_function`


.. _v1.3.0:

1.3.0 (2013-03-11)
------------------

.. warning:: This version deprecates many magic or unexplicit features that will be
             removed in v2.0.0.

             Please read the :ref:`changelog-1-3-0-upgrading` section, then run your
             tests with ``python -W default`` to see all remaining warnings.

New
"""

- **Global:**
    - Rewrite the whole documentation
    - Provide a dedicated :class:`~factory.mogo.MogoFactory` subclass of :class:`~factory.Factory`

- **The Factory class:**
    - Better creation/building customization hooks at :meth:`factory.Factory._build` and :meth:`factory.Factory.create`
    - Add support for passing non-kwarg parameters to a :class:`~factory.Factory`
      wrapped class through :attr:`~factory.Factory.FACTORY_ARG_PARAMETERS`.
    - Keep the :attr:`~factory.Factory.FACTORY_FOR` attribute in :class:`~factory.Factory` classes

- **Declarations:**
    - Allow :class:`~factory.SubFactory` to solve circular dependencies between factories
    - Enhance :class:`~factory.SelfAttribute` to handle "container" attribute fetching
    - Add a :attr:`~factory.Iterator.getter` to :class:`~factory.Iterator`
      declarations
    - A :class:`~factory.Iterator` may be prevented from cycling by setting
      its :attr:`~factory.Iterator.cycle` argument to ``False``
    - Allow overriding default arguments in a :class:`~factory.PostGenerationMethodCall`
      when generating an instance of the factory
    - An object created by a :class:`~factory.django.DjangoModelFactory` will be saved
      again after :class:`~factory.PostGeneration` hooks execution


Pending deprecation
"""""""""""""""""""

The following features have been deprecated and will be removed in an upcoming release.

- **Declarations:**
    - :class:`~factory.InfiniteIterator` is deprecated in favor of :class:`~factory.Iterator`
    - :class:`~factory.CircularSubFactory` is deprecated in favor of :class:`~factory.SubFactory`
    - The ``extract_prefix`` argument to :meth:`~factory.post_generation` is now deprecated

- **Factory:**
    - Usage of :meth:`~factory.Factory.set_creation_function` and :meth:`~factory.Factory.set_building_function`
      are now deprecated
    - Implicit associated class discovery is no longer supported, you must set the :attr:`~factory.Factory.FACTORY_FOR`
      attribute on all :class:`~factory.Factory` subclasses


.. _changelog-1-3-0-upgrading:

Upgrading
"""""""""

This version deprecates a few magic or undocumented features.
All warnings will turn into errors starting from v2.0.0.

In order to upgrade client code, apply the following rules:

- Add a ``FACTORY_FOR`` attribute pointing to the target class to each
  :class:`~factory.Factory`, instead of relying on automagic associated class
  discovery
- When using factory_boy for Django models, have each factory inherit from
  :class:`~factory.django.DjangoModelFactory`
- Replace ``factory.CircularSubFactory('some.module', 'Symbol')`` with
  ``factory.SubFactory('some.module.Symbol')``
- Replace ``factory.InfiniteIterator(iterable)`` with ``factory.Iterator(iterable)``
- Replace ``@factory.post_generation()`` with ``@factory.post_generation``
- Replace ``factory.set_building_function(SomeFactory, building_function)`` with
  an override of the :meth:`~factory.Factory._build` method of ``SomeFactory``
- Replace ``factory.set_creation_function(SomeFactory, creation_function)`` with
  an override of the :meth:`~factory.Factory._create` method of ``SomeFactory``



.. _v1.2.0:

1.2.0 (2012-09-08)
------------------

*New:*

    - Add :class:`~factory.CircularSubFactory` to solve circular dependencies between factories


.. _v1.1.5:

1.1.5 (2012-07-09)
------------------

*Bugfix:*

    - Fix :class:`~factory.PostGenerationDeclaration` and derived classes.


.. _v1.1.4:

1.1.4 (2012-06-19)
------------------

*New:*

    - Add :meth:`~factory.use_strategy` decorator to override a
      :class:`~factory.Factory`'s default strategy
    - Improve test running (tox, python2.6/2.7)
    - Introduce :class:`~factory.PostGeneration` and
      :class:`~factory.RelatedFactory`


.. _v1.1.3:

1.1.3 (2012-03-09)
------------------

*Bugfix:*

  - Fix packaging rules


.. _v1.1.2:

1.1.2 (2012-02-25)
------------------

*New:*

  - Add :class:`~factory.Iterator` and :class:`~factory.InfiniteIterator` for :class:`~factory.Factory` attribute declarations.
  - Provide :func:`~factory.Factory.generate` and :func:`~factory.Factory.simple_generate`, that allow specifying the instantiation strategy directly.
    Also provides :func:`~factory.Factory.generate_batch` and :func:`~factory.Factory.simple_generate_batch`.


.. _v1.1.1:

1.1.1 (2012-02-24)
------------------

*New:*

  - Add :func:`~factory.Factory.build_batch`, :func:`~factory.Factory.create_batch` and :func:`~factory.Factory.stub_batch`, to instantiate factories in batch


.. _v1.1.0:

1.1.0 (2012-02-24)
------------------

*New:*

  - Improve the :class:`~factory.SelfAttribute` syntax to fetch sub-attributes using the ``foo.bar`` syntax;
  - Add :class:`~factory.ContainerAttribute` to fetch attributes from the container of a :class:`~factory.SubFactory`.
  - Provide the :func:`~factory.make_factory` helper: ``MyClassFactory = make_factory(MyClass, x=3, y=4)``
  - Add :func:`~factory.build`, :func:`~factory.create`, :func:`~factory.stub` helpers

*Bugfix:*

  - Allow classmethod/staticmethod on factories

*Deprecation:*

  - Auto-discovery of :attr:`~factory.Factory.FACTORY_FOR` based on class name is now deprecated


.. _v1.0.4:

1.0.4 (2011-12-21)
------------------

*New:*

  - Improve the algorithm for populating a :class:`~factory.Factory` attributes dict
  - Add ``python setup.py test`` command to run the test suite
  - Allow custom build functions
  - Introduce :data:`~factory.MOGO_BUILD` build function
  - Add support for inheriting from multiple :class:`~factory.Factory`
  - Base :class:`~factory.Factory` classes can now be declared :attr:`abstract <factory.Factory.ABSTRACT_FACTORY>`.
  - Provide :class:`~factory.django.DjangoModelFactory`, whose :class:`~factory.Sequence` counter starts at the next free database id
  - Introduce :class:`~factory.SelfAttribute`, a shortcut for ``factory.LazyAttribute(lambda o: o.foo.bar.baz``.

*Bugfix:*

  - Handle nested :class:`~factory.SubFactory`
  - Share sequence counter between parent and subclasses
  - Fix :class:`~factory.SubFactory` / :class:`~factory.Sequence` interferences


.. _v1.0.2:

1.0.2 (2011-05-16)
------------------

*New:*

  - Introduce :class:`~factory.SubFactory`


.. _v1.0.1:

1.0.1 (2011-05-13)
------------------

*New:*

  - Allow :class:`~factory.Factory` inheritance
  - Improve handling of custom build/create functions

*Bugfix:*

  - Fix concurrency between :class:`~factory.LazyAttribute` and :class:`~factory.Sequence`


.. _v1.0.0:

1.0.0 (2010-08-22)
------------------

*New:*

  - First version of factory_boy


Credits
-------

* Initial version by Mark Sandstrom (2010)
* Developed by Raphaël Barrois since 2011


.. vim:et:ts=4:sw=4:tw=119:ft=rst:
