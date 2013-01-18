ChangeLog
=========

2.0.0 (future)
--------------

.. note:: This section lists features planned for v2 of factory_boy. Changes announced here may not have been committed to the repository.

*New:*

    - Add support for Python3
    - Clean up documentation
    - Document extension points
    - Add support for ``get_or_create`` in :class:`~factory.DjangoModelFactory`

*Deprecation:*

    - Remove associated class discovery
    - Stop defaulting to Django's ``Foo.objects.create()`` when "creating" instances
    - Remove STRATEGY_*
    - Remove :meth:`~factory.Factory.set_building_function` / :meth:`~factory.Factory.set_creation_function`


1.3.0 (current)
---------------

*New:*

    - Add :class:`~factory.CircularSubFactory` to solve circular dependencies between factories
    - Better creation/building customization hooks at :meth:`factory.Factory._build` and :meth:`factory.Factory.create`
    - Add support for passing non-kwarg parameters to a :class:`~factory.Factory` wrapped class
    - Enhance :class:`~factory.SelfAttribute` to handle "container" attribute fetching
    - Keep the :attr:`~factory.Factory.FACTORY_FOR` attribute in :class:`~factory.Factory` classes
    - Provide a dedicated :class:`~factory.MogoFactory` subclass of :class:`~factory.Factory`
    - Allows overriding default arguments in
      :class:`~factory.PostGenerationMethodCall` when creating a new
      instance of a factory.
    - Add :class:`~factory.DjangoPostGenerationMethodCall` that
      automatically saves the object to the database after calling the
      specified object's method during post-generation.

*Pending deprecation:*

The following features have been deprecated and will be removed in an upcoming release.

    - Usage of :meth:`~factory.Factory.set_creation_function` and :meth:`~factory.Factory.set_building_function`
      are now deprecated
    - The :attr:`~factory.Factory.ABSTRACT_FACTORY` attribute has been renamed to
      :attr:`~factory.Factory.FACTORY_ABSTRACT`.
    - Implicit associated class discovery is no longer supported, you must set the :attr:`~factory.Factory.FACTORY_FOR`
      attribute on all :class:`~factory.Factory` subclasses

1.2.0 (09/08/2012)
------------------

*New:*

    - Add :class:`~factory.CircularSubFactory` to solve circular dependencies between factories

1.1.5 (09/07/2012)
------------------

*Bugfix:*

    - Fix :class:`~factory.PostGenerationDeclaration` and derived classes.

1.1.4 (19/06/2012)
------------------

*New:*

    - Add :meth:`~factory.use_strategy` decorator to override a
      :class:`~factory.Factory`'s default strategy
    - Improve test running (tox, python2.6/2.7)
    - Introduce :class:`~factory.PostGeneration` and
      :class:`~factory.RelatedFactory`

1.1.3 (9/03/2012)
-----------------

*Bugfix:*

  - Fix packaging rules

1.1.2 (25/02/2012)
------------------

*New:*

  - Add :class:`~factory.Iterator` and :class:`~factory.InfiniteIterator` for :class:`~factory.Factory` attribute declarations.
  - Provide :func:`~factory.Factory.generate` and :func:`~factory.Factory.simple_generate`, that allow specifying the instantiation strategy directly.
    Also provides :func:`~factory.Factory.generate_batch` and :func:`~factory.Factory.simple_generate_batch`.

1.1.1 (24/02/2012)
------------------

*New:*

  - Add :func:`~factory.Factory.build_batch`, :func:`~factory.Factory.create_batch` and :func:`~factory.Factory.stub_batch`, to instantiate factories in batch

1.1.0 (24/02/2012)
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

1.0.4 (21/12/2011)
------------------

*New:*

  - Improve the algorithm for populating a :class:`~factory.Factory` attributes dict
  - Add ``python setup.py test`` command to run the test suite
  - Allow custom build functions
  - Introduce :data:`~factory.MOGO_BUILD` build function
  - Add support for inheriting from multiple :class:`~factory.Factory`
  - Base :class:`~factory.Factory` classes can now be declared :attr:`abstract <factory.Factory.ABSTRACT_FACTORY>`.
  - Provide :class:`~factory.DjangoModelFactory`, whose :class:`~factory.Sequence` counter starts at the next free database id
  - Introduce :class:`~factory.SelfAttribute`, a shortcut for ``factory.LazyAttribute(lambda o: o.foo.bar.baz``.

*Bugfix:*

  - Handle nested :class:`~factory.SubFactory`
  - Share sequence counter between parent and subclasses
  - Fix :class:`~factory.SubFactory` / :class:`~factory.Sequence` interferences

1.0.2 (16/05/2011)
------------------

*New:*

  - Introduce :class:`~factory.SubFactory`

1.0.1 (13/05/2011)
------------------

*New:*

  - Allow :class:`~factory.Factory` inheritance
  - Improve handling of custom build/create functions

*Bugfix:*

  - Fix concurrency between :class:`~factory.LazyAttribute` and :class:`~factory.Sequence`

1.0.0 (22/08/2010)
------------------

*New:*

  - First version of factory_boy


.. vim:et:ts=4:sw=4:tw=119:ft=rst:
