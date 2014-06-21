factory_boy
===========

.. image:: https://secure.travis-ci.org/rbarrois/factory_boy.png?branch=master
    :target: http://travis-ci.org/rbarrois/factory_boy/

factory_boy is a fixtures replacement based on thoughtbot's `factory_girl <http://github.com/thoughtbot/factory_girl>`_.

As a fixtures replacement tool, it aims to replace static, hard to maintain fixtures
with easy-to-use factories for complex object.

Instead of building an exhaustive test setup with every possible combination of corner cases,
``factory_boy`` allows you to use objects customized for the current test,
while only declaring the test-specific fields:

.. code-block:: python

    class FooTests(unittest.TestCase):

        def test_with_factory_boy(self):
            # We need a 200€, paid order, shipping to australia, for a VIP customer
            order = OrderFactory(
                amount=200,
                status='PAID',
                customer__is_vip=True,
                address__country='AU',
            )
            # Run the tests here

        def test_without_factory_boy(self):
            address = Address(
                street="42 fubar street",
                zipcode="42Z42",
                city="Sydney",
                country="AU",
            )
            customer = Customer(
                first_name="John",
                last_name="Doe",
                phone="+1234",
                email="john.doe@example.org",
                active=True,
                is_vip=True,
                address=address,
            )
            # etc.

factory_boy is designed to work well with various ORMs (Django, Mogo, SQLAlchemy),
and can easily be extended for other libraries.

Its main features include:

- Straightforward declarative syntax
- Chaining factory calls while retaining the global context
- Support for multiple build strategies (saved/unsaved instances, attribute dicts, stubbed objects)
- Multiple factories per class support, including inheritance


Links
-----

* Documentation: http://factoryboy.readthedocs.org/
* Repository: https://github.com/rbarrois/factory_boy
* Package: https://pypi.python.org/pypi/factory_boy/

factory_boy supports Python 2.6, 2.7, 3.2 and 3.3, as well as PyPy; it requires only the standard Python library.


Download
--------

PyPI: https://pypi.python.org/pypi/factory_boy/

.. code-block:: sh

    $ pip install factory_boy

Source: https://github.com/rbarrois/factory_boy/

.. code-block:: sh

    $ git clone git://github.com/rbarrois/factory_boy/
    $ python setup.py install


Usage
-----


.. note:: This section provides a quick summary of factory_boy features.
          A more detailed listing is available in the full documentation.


Defining factories
""""""""""""""""""

Factories declare a set of attributes used to instantiate an object.
The class of the object must be defined in the ``model`` field of a ``class Meta:`` attribute:

.. code-block:: python

    import factory
    from . import models

    class UserFactory(factory.Factory):
        class Meta:
            model = models.User

        first_name = 'John'
        last_name = 'Doe'
        admin = False

    # Another, different, factory for the same object
    class AdminFactory(factory.Factory):
        class Meta:
            model = models.User

        first_name = 'Admin'
        last_name = 'User'
        admin = True


Using factories
"""""""""""""""

factory_boy supports several different build strategies: build, create, attributes and stub:

.. code-block:: python

    # Returns a User instance that's not saved
    user = UserFactory.build()

    # Returns a saved User instance
    user = UserFactory.create()

    # Returns a dict of attributes that can be used to build a User instance
    attributes = UserFactory.attributes()


You can use the Factory class as a shortcut for the default build strategy:

.. code-block:: python

    # Same as UserFactory.create()
    user = UserFactory()


No matter which strategy is used, it's possible to override the defined attributes by passing keyword arguments:

.. code-block:: pycon

    # Build a User instance and override first_name
    >>> user = UserFactory.build(first_name='Joe')
    >>> user.first_name
    "Joe"


It is also possible to create a bunch of objects in a single call:

.. code-block:: pycon

    >>> users = UserFactory.build(10, first_name="Joe")
    >>> len(users)
    10
    >>> [user.first_name for user in users]
    ["Joe", "Joe", "Joe", "Joe", "Joe", "Joe", "Joe", "Joe", "Joe", "Joe"]

Lazy Attributes
"""""""""""""""

Most factory attributes can be added using static values that are evaluated when the factory is defined,
but some attributes (such as fields whose value is computed from other elements)
will need values assigned each time an instance is generated.

These "lazy" attributes can be added as follows:

.. code-block:: python

    class UserFactory(factory.Factory):
        class Meta:
            model = models.User

        first_name = 'Joe'
        last_name = 'Blow'
        email = factory.LazyAttribute(lambda a: '{0}.{1}@example.com'.format(a.first_name, a.last_name).lower())

.. code-block:: pycon

    >>> UserFactory().email
    "joe.blow@example.com"


Sequences
"""""""""

Unique values in a specific format (for example, e-mail addresses) can be generated using sequences. Sequences are defined by using ``Sequence`` or the decorator ``sequence``:

.. code-block:: python

    class UserFactory(factory.Factory):
        class Meta:
            model = models.User

        email = factory.Sequence(lambda n: 'person{0}@example.com'.format(n))

    >>> UserFactory().email
    'person0@example.com'
    >>> UserFactory().email
    'person1@example.com'


Associations
""""""""""""

Some objects have a complex field, that should itself be defined from a dedicated factories.
This is handled by the ``SubFactory`` helper:

.. code-block:: python

    class PostFactory(factory.Factory):
        class Meta:
            model = models.Post

        author = factory.SubFactory(UserFactory)


The associated object's strategy will be used:


.. code-block:: python

    # Builds and saves a User and a Post
    >>> post = PostFactory()
    >>> post.id is None  # Post has been 'saved'
    False
    >>> post.author.id is None  # post.author has been saved
    False

    # Builds but does not save a User, and then builds but does not save a Post
    >>> post = PostFactory.build()
    >>> post.id is None
    True
    >>> post.author.id is None
    True


Debugging factory_boy
"""""""""""""""""""""

Debugging factory_boy can be rather complex due to the long chains of calls.
Detailed logging is available through the ``factory`` logger.

A helper, :meth:`factory.debug()`, is available to ease debugging:

.. code-block:: python

    with factory.debug():
        obj = TestModel2Factory()


    import logging
    logger = logging.getLogger('factory')
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)

This will yield messages similar to those (artificial indentation):

.. code-block:: ini

    BaseFactory: Preparing tests.test_using.TestModel2Factory(extra={})
      LazyStub: Computing values for tests.test_using.TestModel2Factory(two=<OrderedDeclarationWrapper for <factory.declarations.SubFactory object at 0x1e15610>>)
        SubFactory: Instantiating tests.test_using.TestModelFactory(__containers=(<LazyStub for tests.test_using.TestModel2Factory>,), one=4), create=True
        BaseFactory: Preparing tests.test_using.TestModelFactory(extra={'__containers': (<LazyStub for tests.test_using.TestModel2Factory>,), 'one': 4})
          LazyStub: Computing values for tests.test_using.TestModelFactory(one=4)
          LazyStub: Computed values, got tests.test_using.TestModelFactory(one=4)
        BaseFactory: Generating tests.test_using.TestModelFactory(one=4)
      LazyStub: Computed values, got tests.test_using.TestModel2Factory(two=<tests.test_using.TestModel object at 0x1e15410>)
    BaseFactory: Generating tests.test_using.TestModel2Factory(two=<tests.test_using.TestModel object at 0x1e15410>)


ORM Support
"""""""""""

factory_boy has specific support for a few ORMs, through specific :class:`~factory.Factory` subclasses:

* Django, with :class:`~factory.django.DjangoModelFactory`
* Mogo, with :class:`~factory.mogo.MogoFactory`
* MongoEngine, with :class:`~factory.mongoengine.MongoEngineFactory`
* SQLAlchemy, with :class:`~factory.alchemy.SQLAlchemyModelFactory`

Contributing
------------

factory_boy is distributed under the MIT License.

Issues should be opened through `GitHub Issues <http://github.com/rbarrois/factory_boy/issues/>`_; whenever possible, a pull request should be included.

All pull request should pass the test suite, which can be launched simply with:

.. code-block:: sh

    $ python setup.py test


.. note::

    Running test requires the unittest2 (standard in Python 2.7+) and mock libraries.


In order to test coverage, please use:

.. code-block:: sh

    $ pip install coverage
    $ coverage erase; coverage run --branch setup.py test; coverage report


Contents, indices and tables
----------------------------

.. toctree::
    :maxdepth: 2

    introduction
    reference
    orms
    recipes
    fuzzy
    examples
    internals
    changelog
    ideas

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

