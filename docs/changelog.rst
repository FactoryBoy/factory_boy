ChangeLog
=========

2.9.1 (2017-08-02)
------------------

*Bugfix:*

    - Fix packaging issues (see https://github.com/zestsoftware/zest.releaser/issues/212)
    - Don't crash when debugging PostGenerationDeclaration


2.9.0 (2017-07-30)
------------------

This version brings massive changes to the core engine, thus reducing the number of
corner cases and weird behaviourrs.

*New:*

    - :issue:`275`: `factory.fuzzy` and `factory.faker` now use the same random seed.
    - Add :class:`factory.Maybe`, which chooses among two possible declarations based
      on another field's value (powers the :class:`~factory.Trait` feature).
    - :class:`~factory.PostGenerationMethodCall` only allows to pass one positional argument; use keyword arguments for
      extra parameters.

*Deprecation:*

    - `factory.fuzzy.get_random_state` is deprecated, `factory.random.get_random_state` should be used instead.
    - `factory.fuzzy.set_random_state` is deprecated, `factory.random.set_random_state` should be used instead.
    - `factory.fuzzy.reseed_random` is deprecated, `factory.random.reseed_random` should be used instead.

.. _v2.8.1:

2.8.1 (2016-12-17)
------------------

*Bugfix:*

    - Fix packaging issues.


.. _v2.8.0:

2.8.0 (2016-12-17)
------------------

*New:*

    - :issue:`240`: Call post-generation declarations in the order they were declared,
      thanks to `Oleg Pidsadnyi <https://github.com/olegpidsadnyi>`_.
    - :issue:`309`: Provide new options for SQLAlchemy session persistence

*Bugfix:*

    - :issue:`334`: Adjust for the package change in ``faker``


.. _v2.7.0:

2.7.0 (2016-04-19)
------------------

*New:*

    - :issue:`267`: Add :class:`factory.LazyFunction` to remove unneeded lambda parameters,
      thanks to `Hervé Cauwelier <https://github.com/bors-ltd>`_.
    - :issue:`251`: Add :ref:`parameterized factories <parameters>` and :class:`traits <factory.Trait>`
    - :issue:`256`, :issue:`292`: Improve error messages in corner cases

*Removed:*

    - :issue:`278`: Formally drop support for Python2.6

.. _v2.6.1:

2.6.1 (2016-02-10)
------------------

*New:*

    - :issue:`262`: Allow optional forced flush on SQLAlchemy, courtesy of `Minjung <https://github.com/Minjung>`_.

.. _v2.6.0:

2.6.0 (2015-10-20)
------------------

*New:*

    - Add :attr:`factory.FactoryOptions.rename` to help handle conflicting names (:issue:`206`)
    - Add support for random-yet-realistic values through `fake-factory <https://pypi.python.org/pypi/fake-factory>`_,
      through the :class:`factory.Faker` class.
    - :class:`factory.Iterator` no longer begins iteration of its argument at import time,
      thus allowing to pass in a lazy iterator such as a Django queryset
      (i.e ``factory.Iterator(models.MyThingy.objects.all())``).
    - Simplify imports for ORM layers, now available through a simple ``factory`` import,
      at ``factory.alchemy.SQLAlchemyModelFactory`` / ``factory.django.DjangoModelFactory`` / ``factory.mongoengine.MongoEngineFactory``.

*Bugfix:*

    - :issue:`201`: Properly handle custom Django managers when dealing with abstract Django models.
    - :issue:`212`: Fix :meth:`factory.django.mute_signals` to handle Django's signal caching
    - :issue:`228`: Don't load :func:`django.apps.apps.get_model()` until required
    - :issue:`219`: Stop using :meth:`mogo.model.Model.new()`, deprecated 4 years ago.

.. _v2.5.2:

2.5.2 (2015-04-21)
------------------

*Bugfix:*

    - Add support for Django 1.7/1.8
    - Add support for mongoengine>=0.9.0 / pymongo>=2.1

.. _v2.5.1:

2.5.1 (2015-03-27)
------------------

*Bugfix:*

    - Respect custom managers in :class:`~factory.django.DjangoModelFactory` (see :issue:`192`)
    - Allow passing declarations (e.g :class:`~factory.Sequence`) as parameters to :class:`~factory.django.FileField`
      and :class:`~factory.django.ImageField`.

.. _v2.5.0:

2.5.0 (2015-03-26)
------------------

*New:*

    - Add support for getting/setting :mod:`factory.fuzzy`'s random state (see :issue:`175`, :issue:`185`).
    - Support lazy evaluation of iterables in :class:`factory.fuzzy.FuzzyChoice` (see :issue:`184`).
    - Support non-default databases at the factory level (see :issue:`171`)
    - Make :class:`factory.django.FileField` and :class:`factory.django.ImageField` non-post_generation, i.e normal fields also available in ``save()`` (see :issue:`141`).

*Bugfix:*

    - Avoid issues when using :meth:`factory.django.mute_signals` on a base factory class (see :issue:`183`).
    - Fix limitations of :class:`factory.StubFactory`, that can now use :class:`factory.SubFactory` and co (see :issue:`131`).


*Deprecation:*

    - Remove deprecated features from :ref:`v2.4.0`
    - Remove the auto-magical sequence setup (based on the latest primary key value in the database) for Django and SQLAlchemy;
      this relates to issues :issue:`170`, :issue:`153`, :issue:`111`, :issue:`103`, :issue:`92`, :issue:`78`. See https://github.com/FactoryBoy/factory_boy/commit/13d310f for technical details.

.. warning:: Version 2.5.0 removes the 'auto-magical sequence setup' bug-and-feature.
             This could trigger some bugs when tests expected a non-zero sequence reference.

Upgrading
"""""""""

.. warning:: Version 2.5.0 removes features that were marked as deprecated in :ref:`v2.4.0 <v2.4.0>`.

All ``FACTORY_*``-style attributes are now declared in a ``class Meta:`` section:

.. code-block:: python

    # Old-style, deprecated
    class MyFactory(factory.Factory):
        FACTORY_FOR = models.MyModel
        FACTORY_HIDDEN_ARGS = ['a', 'b', 'c']

    # New-style
    class MyFactory(factory.Factory):
        class Meta:
            model = models.MyModel
            exclude = ['a', 'b', 'c']

A simple shell command to upgrade the code would be:

.. code-block:: sh

    # sed -i: inplace update
    # grep -l: only file names, not matching lines
    sed -i 's/FACTORY_FOR =/class Meta:\n        model =/' $(grep -l FACTORY_FOR $(find . -name '*.py'))

This takes care of all ``FACTORY_FOR`` occurences; the files containing other attributes to rename can be found with ``grep -R  FACTORY .``


.. _v2.4.1:

2.4.1 (2014-06-23)
------------------

*Bugfix:*

    - Fix overriding deeply inherited attributes (set in one factory, overridden in a subclass, used in a sub-sub-class).

.. _v2.4.0:

2.4.0 (2014-06-21)
------------------

*New:*

    - Add support for :attr:`factory.fuzzy.FuzzyInteger.step`, thanks to `ilya-pirogov <https://github.com/ilya-pirogov>`_ (:issue:`120`)
    - Add :meth:`~factory.django.mute_signals` decorator to temporarily disable some signals, thanks to `ilya-pirogov <https://github.com/ilya-pirogov>`_ (:issue:`122`)
    - Add :class:`~factory.fuzzy.FuzzyFloat` (:issue:`124`)
    - Declare target model and other non-declaration fields in a ``class Meta`` section.

*Deprecation:*

    - Use of ``FACTORY_FOR`` and other ``FACTORY`` class-level attributes is deprecated and will be removed in 2.5.
      Those attributes should now declared within the :class:`class Meta <factory.FactoryOptions>` attribute:

      For :class:`factory.Factory`:

      * Rename :attr:`~factory.Factory.FACTORY_FOR` to :attr:`~factory.FactoryOptions.model`
      * Rename :attr:`~factory.Factory.ABSTRACT_FACTORY` to :attr:`~factory.FactoryOptions.abstract`
      * Rename :attr:`~factory.Factory.FACTORY_STRATEGY` to :attr:`~factory.FactoryOptions.strategy`
      * Rename :attr:`~factory.Factory.FACTORY_ARG_PARAMETERS` to :attr:`~factory.FactoryOptions.inline_args`
      * Rename :attr:`~factory.Factory.FACTORY_HIDDEN_ARGS` to :attr:`~factory.FactoryOptions.exclude`

      For :class:`factory.django.DjangoModelFactory`:

      * Rename :attr:`~factory.django.DjangoModelFactory.FACTORY_DJANGO_GET_OR_CREATE` to :attr:`~factory.django.DjangoOptions.django_get_or_create`

      For :class:`factory.alchemy.SQLAlchemyModelFactory`:

      * Rename :attr:`~factory.alchemy.SQLAlchemyModelFactory.FACTORY_SESSION` to :attr:`~factory.alchemy.SQLAlchemyOptions.sqlalchemy_session`

.. _v2.3.1:

2.3.1 (2014-01-22)
------------------

*Bugfix:*

    - Fix badly written assert containing state-changing code, spotted by `chsigi <https://github.com/chsigi>`_ (:issue:`126`)
    - Don't crash when handling objects whose __repr__ is non-pure-ascii bytes on Py2,
      discovered by `mbertheau <https://github.com/mbertheau>`_ (:issue:`123`) and `strycore <https://github.com/strycore>`_ (:issue:`127`)

.. _v2.3.0:

2.3.0 (2013-12-25)
------------------

*New:*

    - Add :class:`~factory.fuzzy.FuzzyText`, thanks to `jdufresne <https://github.com/jdufresne>`_ (:issue:`97`)
    - Add :class:`~factory.fuzzy.FuzzyDecimal`, thanks to `thedrow <https://github.com/thedrow>`_ (:issue:`94`)
    - Add support for :class:`~mongoengine.EmbeddedDocument`, thanks to `imiric <https://github.com/imiric>`_ (:issue:`100`)

.. _v2.2.1:

2.2.1 (2013-09-24)
------------------

*Bugfix:*

    - Fixed sequence counter for :class:`~factory.django.DjangoModelFactory` when a factory
      inherits from another factory relating to an abstract model.

.. _v2.2.0:

2.2.0 (2013-09-24)
------------------

*Bugfix:*

    - Removed duplicated :class:`~factory.alchemy.SQLAlchemyModelFactory` lurking in :mod:`factory`
      (:issue:`83`)
    - Properly handle sequences within object inheritance chains.
      If FactoryA inherits from FactoryB, and their associated classes share the same link,
      sequence counters will be shared (:issue:`93`)
    - Properly handle nested :class:`~factory.SubFactory` overrides

*New:*

    - The :class:`~factory.django.DjangoModelFactory` now supports the ``FACTORY_FOR = 'myapp.MyModel'``
      syntax, making it easier to shove all factories in a single module (:issue:`66`).
    - Add :meth:`factory.debug()` helper for easier backtrace analysis
    - Adding factory support for mongoengine with :class:`~factory.mongoengine.MongoEngineFactory`.

.. _v2.1.2:

2.1.2 (2013-08-14)
------------------

*New:*

    - The :class:`~factory.Factory.ABSTRACT_FACTORY` keyword is now optional, and automatically set
      to ``True`` if neither the :class:`~factory.Factory` subclass nor its parent declare the
      :class:`~factory.Factory.FACTORY_FOR` attribute (:issue:`74`)


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
    - Add a :attr:`~factory.builder.Resolver.factory_parent` attribute to the
      :class:`~factory.builder.Resolver` passed to :class:`~factory.LazyAttribute`, in order to access
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
