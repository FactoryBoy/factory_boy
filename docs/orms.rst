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

    * The :attr:`~factory.Factory.FACTORY_FOR` attribute also supports the ``'app.Model'``
      syntax
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
                FACTORY_FOR = 'myapp.User'  # Equivalent to ``FACTORY_FOR = myapp.models.User``
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


.. note:: If a :class:`DjangoModelFactory` relates to an :obj:`~django.db.models.Options.abstract`
          model, be sure to declare the :class:`DjangoModelFactory` as abstract:

          .. code-block:: python

              class MyAbstractModelFactory(factory.django.DjangoModelFactory):
                  FACTORY_FOR = models.MyAbstractModel
                  ABSTRACT_FACTORY = True

              class MyConcreteModelFactory(MyAbstractModelFactory):
                  FACTORY_FOR = models.MyConcreteModel

          Otherwise, factory_boy will try to get the 'next PK' counter from the abstract model.


.. class:: FileField

    Custom declarations for :class:`django.db.models.FileField`

    .. method:: __init__(self, from_path='', from_file='', data=b'', filename='example.dat')

        :param str from_path: Use data from the file located at ``from_path``,
                              and keep its filename
        :param file from_file: Use the contents of the provided file object; use its filename
                               if available
        :param bytes data: Use the provided bytes as file contents
        :param str filename: The filename for the FileField

.. note:: If the value ``None`` was passed for the :class:`FileField` field, this will
          disable field generation:

.. code-block:: python

    class MyFactory(factory.django.DjangoModelFactory):
        FACTORY_FOR = models.MyModel

        the_file = factory.django.FileField(filename='the_file.dat')

.. code-block:: pycon

    >>> MyFactory(the_file__data=b'uhuh').the_file.read()
    b'uhuh'
    >>> MyFactory(the_file=None).the_file
    None


.. class:: ImageField

    Custom declarations for :class:`django.db.models.ImageField`

    .. method:: __init__(self, from_path='', from_file='', filename='example.jpg', width=100, height=100, color='green', format='JPEG')

        :param str from_path: Use data from the file located at ``from_path``,
                              and keep its filename
        :param file from_file: Use the contents of the provided file object; use its filename
                               if available
        :param str filename: The filename for the ImageField
        :param int width: The width of the generated image (default: ``100``)
        :param int height: The height of the generated image (default: ``100``)
        :param str color: The color of the generated image (default: ``'green'``)
        :param str format: The image format (as supported by PIL) (default: ``'JPEG'``)

.. note:: If the value ``None`` was passed for the :class:`FileField` field, this will
          disable field generation:

.. note:: Just as Django's :class:`django.db.models.ImageField` requires the
          Python Imaging Library, this :class:`ImageField` requires it too.

.. code-block:: python

    class MyFactory(factory.django.DjangoModelFactory):
        FACTORY_FOR = models.MyModel

        the_image = factory.django.ImageField(color='blue')

.. code-block:: pycon

    >>> MyFactory(the_image__width=42).the_image.width
    42
    >>> MyFactory(the_image=None).the_image
    None


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


MongoEngine
-----------

.. currentmodule:: factory.mongoengine

factory_boy supports `MongoEngine`_-style models, through the :class:`MongoEngineFactory` class.

`mongoengine`_ is a wrapper around the ``pymongo`` library for MongoDB.

.. _mongoengine: http://mongoengine.org/

.. class:: MongoEngineFactory(factory.Factory)

    Dedicated class for `MongoEngine`_ models.

    This class provides the following features:

    * :func:`~factory.Factory.build()` calls a model's ``__init__`` method
    * :func:`~factory.Factory.create()` builds an instance through ``__init__`` then
      saves it.

    .. note:: If the :attr:`associated class <factory.Factory.FACTORY_FOR>` is a :class:`mongoengine.EmbeddedDocument`,
              the :meth:`~MongoEngineFactory.create` function won't "save" it, since this wouldn't make sense.

              This feature makes it possible to use :class:`~factory.SubFactory` to create embedded document.


SQLAlchemy
----------

.. currentmodule:: factory.alchemy


Factoy_boy also supports `SQLAlchemy`_  models through the :class:`SQLAlchemyModelFactory` class.

To work, this class needs an `SQLAlchemy`_ session object affected to "FACTORY_SESSION" class attribute.

.. _SQLAlchemy: http://www.sqlalchemy.org/

.. class:: SQLAlchemyModelFactory(factory.Factory)

    Dedicated class for `SQLAlchemy`_ models.

    This class provides the following features:

    * :func:`~factory.Factory.create()` uses :meth:`sqlalchemy.orm.session.Session.add`
    * :func:`~factory.Factory._setup_next_sequence()` selects the next unused primary key value

    .. attribute:: FACTORY_SESSION

        Fields whose SQLAlchemy session object are passed will be used to communicate with the database

A (very) simple exemple:

.. code-block:: python

    from sqlalchemy import Column, Integer, Unicode, create_engine
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import scoped_session, sessionmaker

    session = scoped_session(sessionmaker())
    engine = create_engine('sqlite://')
    session.configure(bind=engine)
    Base = declarative_base()


    class User(Base):
        """ A SQLAlchemy simple model class who represents a user """
        __tablename__ = 'UserTable'

        id = Column(Integer(), primary_key=True)
        name = Column(Unicode(20))

    Base.metadata.create_all(engine)


    class UserFactory(SQLAlchemyModelFactory):
        FACTORY_FOR = User
        FACTORY_SESSION = session   # the SQLAlchemy session object

        id = factory.Sequence(lambda n: n)
        name = factory.Sequence(lambda n: u'User %d' % n)

.. code-block:: pycon

    >>> session.query(User).all()
    []
    >>> UserFactory()
    <User: User 1>
    >>> session.query(User).all()
    [<User: User 1>]
