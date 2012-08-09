SubFactory
==========

Some objects may use other complex objects as parameters; in order to simplify this setup, factory_boy
provides the :py:class:`factory.SubFactory` class.

This should be used when defining a :py:class:`~factory.Factory` attribute that will hold the other complex object::

    import factory

    # A standard factory
    class UserFactory(factory.Factory):
        FACTORY_FOR = User

        # Various fields
        first_name = 'John'
        last_name = factory.Sequence(lambda n: 'D%se' % ('o' * n))  # De, Doe, Dooe, Doooe, ...
        email = factory.LazyAttribute(lambda o: '%s.%s@example.org' % (o.first_name.lower(), o.last_name.lower()))

    # A factory for an object with a 'User' field
    class CompanyFactory(factory.Factory):
        FACTORY_FOR = Company

        name = factory.Sequence(lambda n: 'FactoryBoyz' + z * n)

        # Let's use our UserFactory to create that user, and override its first name.
        owner = factory.SubFactory(UserFactory, first_name='Jack')

Instantiating the external factory will in turn instantiate an object of the internal factory::

    >>> c = CompanyFactory()
    >>> c
    <Company: FactoryBoyz>

    # Notice that the first_name was overridden
    >>> c.owner
    <User: Jack De>
    >>> c.owner.email
    jack.de@example.org

Fields of the SubFactory can also be overridden when instantiating the external factory::

    >>> c = CompanyFactory(owner__first_name='Henry')
    >>> c.owner
    <User: Henry Doe>

    # Notice that the updated first_name was propagated to the email LazyAttribute.
    >>> c.owner.email
    henry.doe@example.org
    
    # It is also possible to override other fields of the SubFactory
    >>> c = CompanyFactory(owner__last_name='Jones')
    >>> c.owner
    <User: Henry Jones>
    >>> c.owner.email
    henry.jones@example.org


Circular dependencies
---------------------

In order to solve circular dependency issues, Factory Boy provides the :class:`~factory.CircularSubFactory` class.

This class expects a module name and a factory name to import from that module; the given module will be imported
(as an absolute import) when the factory is first accessed::

    # foo/factories.py
    import factory

    from bar import factories

    class FooFactory(factory.Factory):
        bar = factory.SubFactory(factories.BarFactory)


    # bar/factories.py
    import factory

    class BarFactory(factory.Factory):
        # Avoid circular import
        foo = factory.CircularSubFactory('foo.factories', 'FooFactory', bar=None)
