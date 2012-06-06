Welcome to Factory Boy's documentation!
=======================================

factory_boy provides easy replacement for fixtures, based on thoughtbot's `factory_girl <http://github.com/thoughtbot/factory_girl>`_.

It allows for an easy definition of factories, various build factories, factory inheritance, ...


Example
-------

Defining a factory
""""""""""""""""""

Simply subclass the :py:class:`~factory.Factory` class, adding various class attributes which will be used as defaults::

    import factory

    class MyUserFactory(factory.Factory):
        FACTORY_FOR = MyUser    # Define the related object

        # A simple attribute
        first_name = 'Foo'

        # A 'sequential' attribute: each instance of the factory will have a different 'n'
        last_name = factory.Sequence(lambda n: 'Bar' + n)

        # A 'lazy' attribute: computed from the values of other attributes
        email = factory.LazyAttribute(lambda o: '%s.%s@example.org' % (o.first_name.lower(), o.last_name.lower()))

Using a factory
"""""""""""""""

Once defined, a factory can be instantiated through different methods::

    # Calls MyUser(first_name='Foo', last_name='Bar0', email='foo.bar0@example.org')
    >>> user = MyUserFactory.build()

    # Calls MyUser.objects.create(first_name='Foo', last_name='Bar1', email='foo.bar1@example.org')
    >>> user = MyUserFactory.create()

    # Values can be overridden
    >>> user = MyUserFactory.build(first_name='Baz')
    >>> user.email
    'baz.bar2@example.org'

    # Additional values can be specified
    >>> user = MyUserFactory.build(some_other_var=42)
    >>> user.some_other_var
    42




Contents:

.. toctree::
    :maxdepth: 2

    examples
    subfactory
    post_generation
    internals

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

