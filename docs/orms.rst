.. _orm:

Using factory_boy with ORMs
===========================

.. currentmodule:: factory


factory_boy provides custom :class:`Factory` subclasses for various ORMs,
adding dedicated features.


Django
------

.. module:: factory.django


The first versions of factory_boy were designed specifically for Django,
but the library has now evolved to be framework-independent.

Most features should thus feel quite familiar to Django users.

The :class:`DjangoModelFactory` subclass
"""""""""""""""""""""""""""""""""""""""""

All factories for a Django :class:`~django.db.models.Model` should use the
:class:`DjangoModelFactory` base class.


.. class:: DjangoModelFactory(factory.Factory)

    Dedicated class for Django :class:`~django.db.models.Model` factories.

    This class provides the following features:

    * The :attr:`~factory.FactoryOptions.model` attribute also supports the ``'app.Model'``
      syntax
    * :func:`~factory.Factory.create()` uses :meth:`Model.objects.create() <django.db.models.query.QuerySet.create>`
    * When using :class:`~factory.RelatedFactory` or :class:`~factory.PostGeneration`
      attributes, the base object will be :meth:`saved <django.db.models.Model.save>`
      once all post-generation hooks have run.


.. class:: DjangoOptions(factory.base.FactoryOptions)

    The ``class Meta`` on a :class:`~DjangoModelFactory` supports extra parameters:

    .. attribute:: database

        .. versionadded:: 2.5.0

        All queries to the related model will be routed to the given database.
        It defaults to ``'default'``.

    .. attribute:: django_get_or_create

        .. versionadded:: 2.4.0

        Fields whose name are passed in this list will be used to perform a
        :meth:`Model.objects.get_or_create() <django.db.models.query.QuerySet.get_or_create>`
        instead of the usual :meth:`Model.objects.create() <django.db.models.query.QuerySet.create>`:

        .. code-block:: python

            class UserFactory(factory.django.DjangoModelFactory):
                class Meta:
                    model = 'myapp.User'  # Equivalent to ``model = myapp.models.User``
                    django_get_or_create = ('username',)

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

        .. warning:: When ``django_get_or_create`` is used, be aware that any new
            values passed to the Factory are **not** used to update an existing model.

            .. code-block:: pycon

                >>> john = UserFactory(username="john")   # Fetches the existing user
                <User: john>

                >>> john.email
                "john@example.com"

                >>> john = UserFactory(                   # Fetches the existing user
                >>>     username="john",                  # and provides a new email value
                >>>     email="a_new_email@example.com"
                >>> )
                <User: john>

                >>> john.email                            # The email value was not updated
                "john@example.com"

    .. attribute:: skip_postgeneration_save

        Transitional option to prevent :class:`~factory.django.DjangoModelFactory`'s
        ``_after_postgeneration`` from issuing a duplicate call to
        :meth:`~django.db.models.Model.save` on the created instance when
        :class:`factory.PostGeneration` hooks return a value.


Extra fields
""""""""""""

.. class:: Password

    Applies :func:`~django.contrib.auth.hashers.make_password` to the
    clear-text argument before to generate the object.

    .. method:: __init__(self, password)

        :param str or None password: Default password.

    .. note:: When the ``password`` argument is ``None``, the resulting password is
              unusable as if ``set_unusable_password()`` were used. This is distinct
              from setting the password to an empty string.

    .. code-block:: python

        class UserFactory(factory.django.DjangoModelFactory):
            class Meta:
                model = models.User

            password = factory.django.Password('pw')

    .. code-block:: pycon

        >>> from django.contrib.auth.hashers import check_password
        >>> # Create user with the default password from the factory.
        >>> user = UserFactory.create()
        >>> check_password('pw', user.password)
        True
        >>> # Override user password at call time.
        >>> other_user = UserFactory.create(password='other_pw')
        >>> check_password('other_pw', other_user.password)
        True
        >>> # Set unusable password
        >>> no_password_user = UserFactory.create(password=None)
        >>> no_password_user.has_usable_password()
        False


.. class:: FileField

    Custom declarations for :class:`django.db.models.FileField`

    .. method:: __init__(self, from_path='', from_file='', from_func='', data=b'', filename='example.dat')

        :param str from_path: Use data from the file located at ``from_path``,
                              and keep its filename
        :param io.BytesIO from_file: Use the contents of the provided file object; use its filename
                               if available, unless ``filename`` is also provided.
        :param Callable from_func: Use function that returns a file object
        :param bytes data: Use the provided bytes as file contents
        :param str filename: The filename for the FileField

.. note:: If the value ``None`` was passed for the :class:`FileField` field, this will
          disable field generation:

.. code-block:: python

    class MyFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = models.MyModel

        the_file = factory.django.FileField(filename='the_file.dat')

.. code-block:: pycon

    >>> MyFactory(the_file__data=b'uhuh').the_file.read()
    b'uhuh'
    >>> MyFactory(the_file=None).the_file
    None


.. class:: ImageField

    Custom declarations for :class:`django.db.models.ImageField`

    .. method:: __init__(self, from_path='', from_file='', from_func='', filename='example.jpg', width=100, height=100, color='green', format='JPEG')

        :param str from_path: Use data from the file located at ``from_path``,
                              and keep its filename
        :param io.BytesIO from_file: Use the contents of the provided file object; use its filename
                               if available
        :param Callable from_func: Use function that returns a file object
        :param str filename: The filename for the ImageField
        :param int width: The width of the generated image (default: ``100``)
        :param int height: The height of the generated image (default: ``100``)
        :param str color: The color of the generated image (default: ``'green'``)
        :param str format: The image format (as supported by PIL) (default: ``'JPEG'``)
        :param str palette: The image palette (as supported by PIL) (default: ``'RGB'``)

.. note:: If the value ``None`` was passed for the :class:`ImageField` field, this will
          disable field generation:

.. note:: Just as Django's :class:`django.db.models.ImageField` requires the
          Python Imaging Library, this :class:`ImageField` requires it too.

.. code-block:: python

    class MyFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = models.MyModel

        the_image = factory.django.ImageField(color='blue')

.. code-block:: pycon

    >>> MyFactory(the_image__width=42).the_image.width
    42
    >>> MyFactory(the_image=None).the_image
    None


Disabling signals
"""""""""""""""""

Signals are often used to plug some custom code into external components code;
for instance to create ``Profile`` objects on-the-fly when a new ``User`` object is saved.

This may interfere with finely tuned :class:`factories <DjangoModelFactory>`, which would
create both using :class:`~factory.RelatedFactory`.

To work around this problem, use the :meth:`mute_signals()` decorator/context manager:

.. method:: mute_signals(signal1, ...)

    Disable the list of selected signals when calling the factory, and reactivate them upon leaving.

.. code-block:: python

    # foo/factories.py

    import factory

    from . import models
    from . import signals

    @factory.django.mute_signals(signals.pre_save, signals.post_save)
    class FooFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = models.Foo

        # ...

    def make_chain():
        with factory.django.mute_signals(signals.pre_save, signals.post_save):
            # pre_save/post_save won't be called here.
            return SomeFactory(), SomeOtherFactory()


Mogo
----

.. module:: factory.mogo

factory_boy supports `Mogo`_-style models, through the :class:`MogoFactory` class.

`Mogo`_ is a wrapper around the ``pymongo`` library for MongoDB.

.. _Mogo: https://github.com/joshmarshall/mogo

.. class:: MogoFactory(factory.Factory)

    Dedicated class for `Mogo`_ models.

    This class provides the following features:

    * :func:`~factory.Factory.build()` calls a model's ``new()`` method
    * :func:`~factory.Factory.create()` builds an instance through ``new()`` then
      saves it.


MongoEngine
-----------

.. module:: factory.mongoengine

factory_boy supports `MongoEngine`_-style models, through the :class:`MongoEngineFactory` class.

`mongoengine`_ is a wrapper around the ``pymongo`` library for MongoDB.

.. _mongoengine: http://mongoengine.org/

.. class:: MongoEngineFactory(factory.Factory)

    Dedicated class for `MongoEngine`_ models.

    This class provides the following features:

    * :func:`~factory.Factory.build()` calls a model's ``__init__`` method
    * :func:`~factory.Factory.create()` builds an instance through ``__init__`` then
      saves it.

    .. note:: If the :attr:`associated class <factory.FactoryOptions.model>` is a :class:`mongoengine.EmbeddedDocument`,
              the :class:`~MongoEngineFactory`'s ``create`` function won't "save" it, since this wouldn't make sense.

              This feature makes it possible to use :class:`~factory.SubFactory` to create embedded document.

A minimalist example:

.. code-block:: python

    import mongoengine

    class Address(mongoengine.EmbeddedDocument):
        street = mongoengine.StringField()

    class Person(mongoengine.Document):
        name = mongoengine.StringField()
        address = mongoengine.EmbeddedDocumentField(Address)

    import factory

    class AddressFactory(factory.mongoengine.MongoEngineFactory):
        class Meta:
            model = Address

        street = factory.Sequence(lambda n: 'street%d' % n)

    class PersonFactory(factory.mongoengine.MongoEngineFactory):
        class Meta:
            model = Person

        name = factory.Sequence(lambda n: 'name%d' % n)
        address = factory.SubFactory(AddressFactory)


SQLAlchemy
----------

.. module:: factory.alchemy


Factory_boy also supports `SQLAlchemy`_  models through the :class:`SQLAlchemyModelFactory` class.

To work, this class needs an `SQLAlchemy`_ session object affected to the :attr:`Meta.sqlalchemy_session <SQLAlchemyOptions.sqlalchemy_session>` attribute.

.. _SQLAlchemy: https://www.sqlalchemy.org/

.. class:: SQLAlchemyModelFactory(factory.Factory)

    Dedicated class for `SQLAlchemy`_ models.

    This class provides the following features:

    * :func:`~factory.Factory.create()` uses :meth:`sqlalchemy.orm.Session.add`


.. class:: SQLAlchemyOptions(factory.base.FactoryOptions)

    In addition to the usual parameters available in :class:`class Meta <factory.FactoryOptions>`,
    a :class:`SQLAlchemyModelFactory` also supports the following settings:

    .. attribute:: sqlalchemy_session

        SQLAlchemy session to use to communicate with the database when creating
        an object through this :class:`SQLAlchemyModelFactory`.

    .. attribute:: sqlalchemy_session_factory

       .. versionadded:: 3.3.0

         :class:`~collections.abc.Callable` returning a :class:`~sqlalchemy.orm.Session` instance to use to communicate
         with the database. You can either provide the session through this attribute, or through
         :attr:`~factory.alchemy.SQLAlchemyOptions.sqlalchemy_session`, but not both at the same time.

        .. code-block:: python

            from . import common

            class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
                class Meta:
                    model = User
                    sqlalchemy_session_factory = lambda: common.Session()

                username = 'john'

    .. attribute:: sqlalchemy_session_persistence

        Control the action taken by ``sqlalchemy_session`` at the end of a create call.

        Valid values are:

        * ``None``: do nothing
        * ``'flush'``: perform a session :meth:`~sqlalchemy.orm.Session.flush`
        * ``'commit'``: perform a session :meth:`~sqlalchemy.orm.Session.commit`

        The default value is ``None``.

    .. attribute:: sqlalchemy_get_or_create

        .. versionadded:: 3.0.0

        Fields whose name are passed in this list will be used to perform a
        :meth:`Model.query.one_or_none() <sqlalchemy.orm.Query.one_or_none>`
        or the usual :meth:`Session.add() <sqlalchemy.orm.Session.add>`:

        .. code-block:: python

            class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
                class Meta:
                    model = User
                    sqlalchemy_session = session
                    sqlalchemy_get_or_create = ('username',)

                username = 'john'

        .. code-block:: pycon

            >>> User.query.all()
            []
            >>> UserFactory()                   # Creates a new user
            <User: john>
            >>> User.query.all()
            [<User: john>]

            >>> UserFactory()                   # Fetches the existing user
            <User: john>
            >>> User.query.all()                # No new user!
            [<User: john>]

            >>> UserFactory(username='jack')    # Creates another user
            <User: jack>
            >>> User.query.all()
            [<User: john>, <User: jack>]

        .. warning:: When ``sqlalchemy_get_or_create`` is used, be aware that any new
            values passed to the Factory are **not** used to update an existing model.

            .. code-block:: pycon

                >>> john = UserFactory(username="john")   # Fetches the existing user
                <User: john>

                >>> john.email
                "john@example.com"

                >>> john = UserFactory(                   # Fetches the existing user
                >>>     username="john",                  # and provides a new email value
                >>>     email="a_new_email@example.com"
                >>> )
                <User: john>

                >>> john.email                            # The email value was not updated
                "john@example.com"


A (very) simple example:

.. code-block:: python

    from sqlalchemy import Column, Integer, Unicode, create_engine
    from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

    engine = create_engine('sqlite://')
    session = scoped_session(sessionmaker(bind=engine))
    Base = declarative_base()


    class User(Base):
        """ A SQLAlchemy simple model class who represents a user """
        __tablename__ = 'UserTable'

        id = Column(Integer(), primary_key=True)
        name = Column(Unicode(20))

    Base.metadata.create_all(engine)

    import factory

    class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = User
            sqlalchemy_session = session   # the SQLAlchemy session object

        id = factory.Sequence(lambda n: n)
        name = factory.Sequence(lambda n: 'User %d' % n)

.. code-block:: pycon

    >>> session.query(User).all()
    []
    >>> UserFactory()
    <User: User 0>
    >>> session.query(User).all()
    [<User: User 0>]


Managing sessions
"""""""""""""""""

Since `SQLAlchemy`_ is a general purpose library,
there is no "global" session management system.

The most common pattern when working with unit tests and ``factory_boy``
is to use `SQLAlchemy`_'s :class:`sqlalchemy.orm.scoping.scoped_session`:

* The test runner configures some project-wide :class:`~sqlalchemy.orm.scoped_session`
* Each :class:`~SQLAlchemyModelFactory` subclass uses this
  :class:`~sqlalchemy.orm.scoped_session` as its :attr:`~SQLAlchemyOptions.sqlalchemy_session`
* The :meth:`~unittest.TestCase.tearDown` method of tests calls
  :meth:`Session.remove <sqlalchemy.orm.scoped_session.remove>`
  to reset the session.

.. note:: See the excellent :ref:`SQLAlchemy guide on scoped_session <sqlalchemy:unitofwork_contextual>`
          for details of :class:`~sqlalchemy.orm.scoped_session`'s usage.

          The basic idea is that declarative parts of the code (including factories)
          need a simple way to access the "current session",
          but that session will only be created and configured at a later point.

          The :class:`~sqlalchemy.orm.scoping.scoped_session` handles this,
          by virtue of only creating the session when a query is sent to the database.


Here is an example layout:

- A global (test-only?) file holds the :class:`~sqlalchemy.orm.scoped_session`:

.. code-block:: python

    # myproject/test/common.py

    from sqlalchemy import orm
    Session = orm.scoped_session(orm.sessionmaker())


- All factory access it:

.. code-block:: python

    # myproject/factories.py

    import factory

    from . import models
    from .test import common

    class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = models.User

            # Use the not-so-global scoped_session
            # Warning: DO NOT USE common.Session()!
            sqlalchemy_session = common.Session

        name = factory.Sequence(lambda n: "User %d" % n)


- The test runner configures the :class:`~sqlalchemy.orm.scoped_session` when it starts:

.. code-block:: python

    # myproject/test/runtests.py

    import sqlalchemy

    from . import common

    def runtests():
        engine = sqlalchemy.create_engine('sqlite://')

        # It's a scoped_session, and now is the time to configure it.
        common.Session.configure(bind=engine)

        run_the_tests


- :class:`test cases <unittest.TestCase>` use this ``scoped_session``,
  and clear it after each test (for isolation):

.. code-block:: python

    # myproject/test/test_stuff.py

    import unittest

    from . import common

    class MyTest(unittest.TestCase):

        def setUp(self):
            # Prepare a new, clean session
            self.session = common.Session()

        def test_something(self):
            u = factories.UserFactory()
            self.assertEqual([u], self.session.query(User).all())

        def tearDown(self):
            # Rollback the session => no changes to the database
            self.session.rollback()
            # Remove it, so that the next test gets a new Session()
            common.Session.remove()
