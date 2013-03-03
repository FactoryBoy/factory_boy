Reference
=========

.. currentmodule:: factory

This section offers an in-depth description of factory_boy features.

For internals and customization points, please refer to the :doc:`internals` section.


The :class:`Factory` class
--------------------------

.. class:: Factory

    The :class:`Factory` class is the base of factory_boy features.

    It accepts a few specific attributes (must be specified on class declaration):

    .. attribute:: FACTORY_FOR

        This required attribute describes the class of objects to generate.
        It may only be absent if the factory has been marked abstract through
        :attr:`ABSTRACT_FACTORY`.

    .. attribute:: ABSTRACT_FACTORY

        This attribute indicates that the :class:`Factory` subclass should not
        be used to generate objects, but instead provides some extra defaults.

    .. attribute:: FACTORY_ARG_PARAMETERS

        Some factories require non-keyword arguments to their :meth:`~object.__init__`.
        They should be listed, in order, in the :attr:`FACTORY_ARG_PARAMETERS`
        attribute:

        .. code-block:: python

            class UserFactory(factory.Factory):
                FACTORY_FOR = User
                FACTORY_ARG_PARAMETERS = ('login', 'email')

                login = 'john'
                email = factory.LazyAttribute(lambda o: '%s@example.com' % o.login)
                firstname = "John"

        .. code-block:: pycon

            >>> UserFactory()
            <User: john>
            >>> User('john', 'john@example.com', firstname="John")  # actual call

    **Base functions:**

    The :class:`Factory` class provides a few methods for getting objects;
    the usual way being to simply call the class:

    .. code-block:: pycon

        >>> UserFactory()               # Calls UserFactory.create()
        >>> UserFactory(login='john')   # Calls UserFactory.create(login='john')

    Under the hood, factory_boy will define the :class:`Factory`
    :meth:`~object.__new__` method to call the default :ref:`strategy <strategies>`
    of the :class:`Factory`.


    A specific strategy for getting instance can be selected by calling the
    adequate method:

    .. classmethod:: build(cls, **kwargs)

        Provides a new object, using the 'build' strategy.

    .. classmethod:: build_batch(cls, size, **kwargs)

        Provides a list of :obj:`size` instances from the :class:`Factory`,
        through the 'build' strategy.


    .. classmethod:: create(cls, **kwargs)

        Provides a new object, using the 'create' strategy.

    .. classmethod:: create_batch(cls, size, **kwargs)

        Provides a list of :obj:`size` instances from the :class:`Factory`,
        through the 'create' strategy.


    .. classmethod:: stub(cls, **kwargs)

        Provides a new stub

    .. classmethod:: stub_batch(cls, size, **kwargs)

        Provides a list of :obj:`size` stubs from the :class:`Factory`.


    .. classmethod:: generate(cls, strategy, **kwargs)

        Provide a new instance, with the provided :obj:`strategy`.

    .. classmethod:: generate_batch(cls, strategy, size, **kwargs)

        Provides a list of :obj:`size` instances using the specified strategy.


    .. classmethod:: simple_generate(cls, create, **kwargs)

        Provide a new instance, either built (``create=False``) or created (``create=True``).

    .. classmethod:: simple_generate_batch(cls, create, size, **kwargs)

        Provides a list of :obj:`size` instances, either built or created
        according to :obj:`create`.


    **Extension points:**

    A :class:`Factory` subclass may override a couple of class methods to adapt
    its behaviour:

    .. classmethod:: _adjust_kwargs(cls, **kwargs)

        .. OHAI_VIM**

        The :meth:`_adjust_kwargs` extension point allows for late fields tuning.

        It is called once keyword arguments have been resolved and post-generation
        items removed, but before the :attr:`FACTORY_ARG_PARAMETERS` extraction
        phase.

        .. code-block:: python

            class UserFactory(factory.Factory):

                @classmethod
                def _adjust_kwargs(cls, **kwargs):
                    # Ensure ``lastname`` is upper-case.
                    kwargs['lastname'] = kwargs['lastname'].upper()
                    return kwargs

        .. OHAI_VIM**


    .. classmethod:: _setup_next_sequence(cls)

        This method will compute the first value to use for the sequence counter
        of this factory.

        It is called when the first instance of the factory (or one of its subclasses)
        is created.

        Subclasses may fetch the next free ID from the database, for instance.


    .. classmethod:: _build(cls, target_class, *args, **kwargs)

        .. OHAI_VIM*

        This class method is called whenever a new instance needs to be built.
        It receives the target class (provided to :attr:`FACTORY_FOR`), and
        the positional and keyword arguments to use for the class once all has
        been computed.

        Subclasses may override this for custom APIs.


    .. classmethod:: _create(cls, target_class, *args, **kwargs)

        .. OHAI_VIM*

        The :meth:`_create` method is called whenever an instance needs to be
        created.
        It receives the same arguments as :meth:`_build`.

        Subclasses may override this for specific persistence backends:

        .. code-block:: python

            class BaseBackendFactory(factory.Factory):
                ABSTRACT_FACTORY = True

                def _create(cls, target_class, *args, **kwargs):
                    obj = target_class(*args, **kwargs)
                    obj.save()
                    return obj

        .. OHAI_VIM*


.. _strategies:

Strategies
""""""""""

factory_boy supports two main strategies for generating instances, plus stubs.


.. data:: BUILD_STRATEGY

    The 'build' strategy is used when an instance should be created,
    but not persisted to any datastore.

    It is usually a simple call to the :meth:`~object.__init__` method of the
    :attr:`~Factory.FACTORY_FOR` class.


.. data:: CREATE_STRATEGY

    The 'create' strategy builds and saves an instance into its appropriate datastore.

    This is the default strategy of factory_boy; it would typically instantiate an
    object, then save it:

    .. code-block:: pycon
    
        >>> obj = self._associated_class(*args, **kwargs)
        >>> obj.save()
        >>> return obj

    .. OHAI_VIM*


.. function:: use_strategy(strategy)

    *Decorator*

    Change the default strategy of the decorated :class:`Factory` to the chosen :obj:`strategy`:

    .. code-block:: python

        @use_strategy(factory.BUILD_STRATEGY)
        class UserBuildingFactory(UserFactory):
            pass


.. data:: STUB_STRATEGY

    The 'stub' strategy is an exception in the factory_boy world: it doesn't return
    an instance of the :attr:`~Factory.FACTORY_FOR` class, and actually doesn't
    require one to be present.

    Instead, it returns an instance of :class:`StubObject` whose attributes have been
    set according to the declarations.


.. class:: StubObject(object)

    A plain, stupid object. No method, no helpers, simply a bunch of attributes.

    It is typically instantiated, then has its attributes set:

    .. code-block:: pycon

        >>> obj = StubObject()
        >>> obj.x = 1
        >>> obj.y = 2


.. class:: StubFactory(Factory)

    An :attr:`abstract <Factory.ABSTRACT_FACTORY>` :class:`Factory`,
    with a default strategy set to :data:`STUB_STRATEGY`.


.. _declarations:

Declarations
------------

LazyAttribute
"""""""""""""

.. class:: LazyAttribute(method_to_call)

The :class:`LazyAttribute` is a simple yet extremely powerful building brick
for extending a :class:`Factory`.

It takes as argument a method to call (usually a lambda); that method should
accept the object being built as sole argument, and return a value.

.. code-block:: python

    class UserFactory(factory.Factory):
        FACTORY_FOR = User

        username = 'john'
        email = factory.LazyAttribute(lambda o: '%s@example.com' % o.username)

.. code-block:: pycon

    >>> u = UserFactory()
    >>> u.email
    'john@example.com'

    >>> u = UserFactory(username='leo')
    >>> u.email
    'leo@example.com'


Decorator
~~~~~~~~~

.. function:: lazy_attribute

If a simple lambda isn't enough, you may use the :meth:`lazy_attribute` decorator instead.

This decorates an instance method that should take a single argument, ``self``;
the name of the method will be used as the name of the attribute to fill with the
return value of the method:

.. code-block:: python

    class UserFactory(factory.Factory)
        FACTORY_FOR = User

        name = u"Jean"

        @factory.lazy_attribute
        def email(self):
            # Convert to plain ascii text
            clean_name = (unicodedata.normalize('NFKD', self.name)
                            .encode('ascii', 'ignore')
                            .decode('utf8'))
            return u'%s@example.com' % clean_name

.. code-block:: pycon

    >>> joel = UserFactory(name=u"Joël")
    >>> joel.email
    u'joel@example.com'


Sequence
""""""""

.. class:: Sequence(lambda, type=int)

If a field should be unique, and thus different for all built instances,
use a :class:`Sequence`.

This declaration takes a single argument, a function accepting a single parameter
- the current sequence counter - and returning the related value.


.. note:: An extra kwarg argument, ``type``, may be provided.
          This feature is deprecated in 1.3.0 and will be removed in 2.0.0.


.. code-block:: python

    class UserFactory(factory.Factory)
        FACTORY_FOR = User

        phone = factory.Sequence(lambda n: '123-555-%04d' % n)

.. code-block:: pycon

    >>> UserFactory().phone
    '123-555-0001'
    >>> UserFactory().phone
    '123-555-0002'


Decorator
~~~~~~~~~

.. function:: sequence

As with :meth:`lazy_attribute`, a decorator is available for complex situations.

:meth:`sequence` decorates an instance method, whose ``self`` method will actually
be the sequence counter - this might be confusing:

.. code-block:: python

    class UserFactory(factory.Factory)
        FACTORY_FOR = User

        @factory.sequence
        def phone(n):
            a = n // 10000
            b = n % 10000
            return '%03d-555-%04d' % (a, b)

.. code-block:: pycon

    >>> UserFactory().phone
    '000-555-9999'
    >>> UserFactory().phone
    '001-555-0000'


Sharing
~~~~~~~

The sequence counter is shared across all :class:`Sequence` attributes of the
:class:`Factory`:

.. code-block:: python

    class UserFactory(factory.Factory):
        FACTORY_FOR = User

        phone = factory.Sequence(lambda n: '%04d' % n)
        office = factory.Sequence(lambda n: 'A23-B%03d' % n)

.. code-block:: pycon

    >>> u = UserFactory()
    >>> u.phone, u.office
    '0041', 'A23-B041'
    >>> u2 = UserFactory()
    >>> u2.phone, u2.office
    '0042', 'A23-B042'


Inheritance
~~~~~~~~~~~

When a :class:`Factory` inherits from another :class:`Factory`, their
sequence counter is shared:

.. code-block:: python

    class UserFactory(factory.Factory):
        FACTORY_FOR = User

        phone = factory.Sequence(lambda n: '123-555-%04d' % n)


    class EmployeeFactory(UserFactory):
        office_phone = factory.Sequence(lambda n: '%04d' % n)

.. code-block:: pycon

    >>> u = UserFactory()
    >>> u.phone
    '123-555-0001'

    >>> e = EmployeeFactory()
    >>> e.phone, e.office_phone
    '123-555-0002', '0002'

    >>> u2 = UserFactory()
    >>> u2.phone
    '123-555-0003'


LazyAttributeSequence
"""""""""""""""""""""

.. class:: LazyAttributeSequence(method_to_call)

The :class:`LazyAttributeSequence` declaration merges features of :class:`Sequence`
and :class:`LazyAttribute`.

It takes a single argument, a function whose two parameters are, in order:

* The object being built
* The sequence counter

.. code-block:: python

    class UserFactory(factory.Factory):
        FACTORY_FOR = User

        login = 'john'
        email = factory.LazyAttributeSequence(lambda o, n: '%s@s%d.example.com' % (o.login, n))

.. code-block:: pycon

    >>> UserFactory().email
    'john@s1.example.com'
    >>> UserFactory(login='jack').email
    'jack@s2.example.com'


Decorator
~~~~~~~~~

.. function:: lazy_attribute_sequence(method_to_call)

As for :meth:`lazy_attribute` and :meth:`sequence`, the :meth:`lazy_attribute_sequence`
handles more complex cases:

.. code-block:: python

    class UserFactory(factory.Factory):
        FACTORY_FOR = User

        login = 'john'

        @lazy_attribute_sequence
        def email(self, n):
            bucket = n % 10
            return '%s@s%d.example.com' % (self.login, bucket)


SubFactory
""""""""""

.. class:: SubFactory(sub_factory, **kwargs)

    .. OHAI_VIM**

This attribute declaration calls another :class:`Factory` subclass,
selecting the same build strategy and collecting extra kwargs in the process.

The :class:`SubFactory` attribute should be called with:

* A :class:`Factory` subclass as first argument, or the fully qualified import
  path to that :class:`Factory` (see :ref:`Circular imports <subfactory-circular>`)
* An optional set of keyword arguments that should be passed when calling that
  factory


Definition
~~~~~~~~~~

.. code-block:: python


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

        name = factory.Sequence(lambda n: 'FactoryBoyz' + 'z' * n)

        # Let's use our UserFactory to create that user, and override its first name.
        owner = factory.SubFactory(UserFactory, first_name='Jack')


Calling
~~~~~~~

The wrapping factory will call of the inner factory:

.. code-block:: pycon

    >>> c = CompanyFactory()
    >>> c
    <Company: FactoryBoyz>

    # Notice that the first_name was overridden
    >>> c.owner
    <User: Jack De>
    >>> c.owner.email
    jack.de@example.org


Fields of the :class:`~factory.SubFactory` may be overridden from the external factory:

.. code-block:: pycon

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


Strategies
~~~~~~~~~~

The strategy chosen for the external factory will be propagated to all subfactories:

.. code-block:: pycon

    >>> c = CompanyFactory()
    >>> c.pk            # Saved to the database
    3
    >>> c.owner.pk      # Saved to the database
    8

    >>> c = CompanyFactory.build()
    >>> c.pk            # Not saved
    None
    >>> c.owner.pk      # Not saved either
    None


.. _subfactory-circular:

Circular imports
~~~~~~~~~~~~~~~~

Some factories may rely on each other in a circular manner.
This issue can be handled by passing the absolute import path to the target
:class:`Factory` to the :class:`SubFactory`.

.. versionadded:: 1.3.0

.. code-block:: python

    class UserFactory(factory.Factory):
        FACTORY_FOR = User

        username = 'john'
        main_group = factory.SubFactory('users.factories.GroupFactory')

    class GroupFactory(factory.Factory):
        FACTORY_FOR = Group

        name = "MyGroup"
        owner = factory.SubFactory(UserFactory)


Obviously, such circular relationships require careful handling of loops:

.. code-block:: pycon

    >>> owner = UserFactory(main_group=None)
    >>> UserFactory(main_group__owner=owner)
    <john (group: MyGroup)>


.. class:: CircularSubFactory(module_name, symbol_name, **kwargs)

    .. OHAI_VIM**

    Lazily imports ``module_name.symbol_name`` at the first call.

.. deprecated:: 1.3.0
    Merged into :class:`SubFactory`; will be removed in 2.0.0.

    Replace ``factory.CircularSubFactory('some.module', 'Symbol', **kwargs)``
    with ``factory.SubFactory('some.module.Symbol', **kwargs)``


SelfAttribute
"""""""""""""

.. class:: SelfAttribute(dotted_path_to_attribute)

Some fields should reference another field of the object being constructed, or an attribute thereof.

This is performed by the :class:`~factory.SelfAttribute` declaration.
That declaration takes a single argument, a dot-delimited path to the attribute to fetch:

.. code-block:: python

    class UserFactory(factory.Factory)
        FACTORY_FOR = User

        birthdate = factory.Sequence(lambda n: datetime.date(2000, 1, 1) + datetime.timedelta(days=n))
        birthmonth = factory.SelfAttribute('birthdate.month')

.. code-block:: pycon

    >>> u = UserFactory()
    >>> u.birthdate
    date(2000, 3, 15)
    >>> u.birthmonth
    3


Parents
~~~~~~~

When used in conjunction with :class:`~factory.SubFactory`, the :class:`~factory.SelfAttribute`
gains an "upward" semantic through the double-dot notation, as used in Python imports.

``factory.SelfAttribute('..country.language')`` means
"Select the ``language`` of the ``country`` of the :class:`~factory.Factory` calling me".

.. code-block:: python

    class UserFactory(factory.Factory):
        FACTORY_FOR = User

        language = 'en'


    class CompanyFactory(factory.Factory):
        FACTORY_FOR = Company

        country = factory.SubFactory(CountryFactory)
        owner = factory.SubFactory(UserFactory, language=factory.SelfAttribute('..country.language'))

.. code-block:: pycon

    >>> company = CompanyFactory()
    >>> company.country.language
    'fr'
    >>> company.owner.language
    'fr'

Obviously, this "follow parents" hability also handles overriding some attributes on call:

.. code-block:: pycon

    >>> company = CompanyFactory(country=china)
    >>> company.owner.language
    'cn'


Iterator
""""""""

.. class:: Iterator(iterable, cycle=True, getter=None)

    The :class:`Iterator` declaration takes succesive values from the given
    iterable. When it is exhausted, it starts again from zero (unless ``cycle=False``).

    .. attribute:: cycle

        The ``cycle`` argument is only useful for advanced cases, where the provided
        iterable has no end (as wishing to cycle it means storing values in memory...).

        .. versionadded:: 1.3.0
            The ``cycle`` argument is available as of v1.3.0; previous versions
            had a behaviour equivalent to ``cycle=False``.

    .. attribute:: getter

        A custom function called on each value returned by the iterable.
        See the :ref:`iterator-getter` section for details.

        .. versionadded:: 1.3.0

Each call to the factory will receive the next value from the iterable:

.. code-block:: python

    class UserFactory(factory.Factory)
        lang = factory.Iterator(['en', 'fr', 'es', 'it', 'de'])

.. code-block:: pycon

    >>> UserFactory().lang
    'en'
    >>> UserFactory().lang
    'fr'


When a value is passed in for the argument, the iterator will *not* be advanced:

.. code-block:: pycon

    >>> UserFactory().lang
    'en'
    >>> UserFactory(lang='cn').lang
    'cn'
    >>> UserFactory().lang
    'fr'

.. _iterator-getter:

Getter
~~~~~~

Some situations may reuse an existing iterable, using only some component.
This is handled by the :attr:`~Iterator.getter` attribute: this is a function
that accepts as sole parameter a value from the iterable, and returns an
adequate value.

.. code-block:: python

    class UserFactory(factory.Factory):
        FACTORY_FOR = User

        # CATEGORY_CHOICES is a list of (key, title) tuples
        category = factory.Iterator(User.CATEGORY_CHOICES, getter=lambda c: c[0])


Decorator
~~~~~~~~~

.. function:: iterator(func)


When generating items of the iterator gets too complex for a simple list comprehension,
use the :func:`iterator` decorator:

.. warning:: The decorated function takes **no** argument,
             notably no ``self`` parameter.

.. code-block:: python

    class UserFactory(factory.Factory):
        FACTORY_FOR = User

        @factory.iterator
        def name():
            with open('test/data/names.dat', 'r') as f:
                for line in f:
                    yield line


InfiniteIterator
~~~~~~~~~~~~~~~~

.. class:: InfiniteIterator(iterable)

    Equivalent to ``factory.Iterator(iterable)``.

.. deprecated:: 1.3.0
    Merged into :class:`Iterator`; will be removed in v2.0.0.

    Replace ``factory.InfiniteIterator(iterable)``
    with ``factory.Iterator(iterable)``.


.. function:: infinite_iterator(function)

    Equivalent to ``factory.iterator(func)``.


.. deprecated:: 1.3.0
    Merged into :func:`iterator`; will be removed in v2.0.0.

    Replace ``@factory.infinite_iterator`` with ``@factory.iterator``.



post-building hooks
"""""""""""""""""""

Some objects expect additional method calls or complex processing for proper definition.
For instance, a ``User`` may need to have a related ``Profile``, where the ``Profile`` is built from the ``User`` object.

To support this pattern, factory_boy provides the following tools:
  - :class:`PostGeneration`: this class allows calling a given function with the generated object as argument
  - :func:`post_generation`: decorator performing the same functions as :class:`PostGeneration`
  - :class:`RelatedFactory`: this builds or creates a given factory *after* building/creating the first Factory.


RelatedFactory
""""""""""""""

.. class:: RelatedFactory(some_factory, related_field, **kwargs)

    .. OHAI_VIM**

A :class:`RelatedFactory` behaves mostly like a :class:`SubFactory`,
with the main difference that it should be provided with a ``related_field`` name
as second argument.

Once the base object has been built (or created), the :class:`RelatedFactory` will
build the :class:`Factory` passed as first argument (with the same strategy),
passing in the base object as a keyword argument whose name is passed in the
``related_field`` argument:

.. code-block:: python

    class CityFactory(factory.Factory):
        FACTORY_FOR = City

        capital_of = None
        name = "Toronto"

    class CountryFactory(factory.Factory):
        FACTORY_FOR = Country

        lang = 'fr'
        capital_city = factory.RelatedFactory(CityFactory, 'capital_of', name="Paris")

.. code-block:: pycon

    >>> france = CountryFactory()
    >>> City.objects.get(capital_of=france)
    <City: Paris>

Extra kwargs may be passed to the related factory, through the usual ``ATTR__SUBATTR`` syntax:

.. code-block:: pycon

    >>> england = CountryFactory(lang='en', capital_city__name="London")
    >>> City.objects.get(capital_of=england)
    <City: London>


PostGeneration
""""""""""""""

.. class:: PostGeneration(callable)

The :class:`PostGeneration` declaration performs actions once the target object
has been generated.

Its sole argument is a callable, that will be called once the base object has
  been generated.

.. note:: Previous versions of factory_boy supported an extra ``extract_prefix``
          argument, to use an alternate argument prefix.
          This feature is deprecated in 1.3.0 and will be removed in 2.0.0.

Once the base object has been generated, the provided callable will be called
as ``callable(obj, create, extracted, **kwargs)``, where:

- ``obj`` is the base object previously generated
- ``create`` is a boolean indicating which strategy was used
- ``extracted`` is ``None`` unless a value was passed in for the
  :class:`PostGeneration` declaration at :class:`Factory` declaration time
- ``kwargs`` are any extra parameters passed as ``attr__key=value`` when calling
  the :class:`Factory`:


.. code-block:: python

    class UserFactory(factory.Factory):
        FACTORY_FOR = User

        login = 'john'
        make_mbox = factory.PostGeneration(
                lambda obj, create, extracted, **kwargs: os.makedirs(obj.login))

.. OHAI_VIM**

Decorator
~~~~~~~~~

.. function:: post_generation(extract_prefix=None)

A decorator is also provided, decorating a single method accepting the same
``obj``, ``created``, ``extracted`` and keyword arguments as :class:`PostGeneration`.


.. code-block:: python

    class UserFactory(factory.Factory):
        FACTORY_FOR = User

        login = 'john'

        @factory.post_generation
        def mbox(self, create, extracted, **kwargs):
            if not create:
                return
            path = extracted or os.path.join('/tmp/mbox/', self.login)
            os.path.makedirs(path)
            return path

.. OHAI_VIM**

.. code-block:: pycon

    >>> UserFactory.build()                  # Nothing was created
    >>> UserFactory.create()                 # Creates dir /tmp/mbox/john
    >>> UserFactory.create(login='jack')     # Creates dir /tmp/mbox/jack
    >>> UserFactory.create(mbox='/tmp/alt')  # Creates dir /tmp/alt


PostGenerationMethodCall
""""""""""""""""""""""""

.. class:: PostGenerationMethodCall(method_name, extract_prefix=None, *args, **kwargs)

.. OHAI_VIM*

The :class:`PostGenerationMethodCall` declaration will call a method on the
generated object just after it being called.

Its sole argument is the name of the method to call.
Extra arguments and keyword arguments for the target method may also be provided.

Once the object has been generated, the method will be called, with the arguments
provided in the :class:`PostGenerationMethodCall` declaration, and keyword
arguments taken from the combination of :class:`PostGenerationMethodCall`
declaration and prefix-based values:

.. code-block:: python

    class UserFactory(factory.Factory):
        FACTORY_FOR = User

        password = factory.PostGenerationMethodCall('set_password', password='')

.. code-block:: pycon

    >>> UserFactory()                           # Calls user.set_password(password='')
    >>> UserFactory(password='test')            # Calls user.set_password(password='test')
    >>> UserFactory(password__disabled=True)    # Calls user.set_password(password='', disabled=True)


Module-level functions
----------------------

Beyond the :class:`Factory` class and the various :ref:`declarations` classes
and methods, factory_boy exposes a few module-level functions, mostly useful
for lightweight factory generation.


Lightweight factory declaration
"""""""""""""""""""""""""""""""

.. function:: make_factory(klass, **kwargs)

    .. OHAI_VIM**

    The :func:`make_factory` function takes a class, declarations as keyword arguments,
    and generates a new :class:`Factory` for that class accordingly:

    .. code-block:: python

        UserFactory = make_factory(User,
            login='john',
            email=factory.LazyAttribute(lambda u: '%s@example.com' % u.login),
        )

        # This is equivalent to:

        class UserFactory(factory.Factory):
            FACTORY_FOR = User

            login = 'john'
            email = factory.LazyAttribute(lambda u: '%s@example.com' % u.login)


Instance building
"""""""""""""""""

The :mod:`factory` module provides a bunch of shortcuts for creating a factory and
extracting instances from them:

.. function:: build(klass, **kwargs)
.. function:: build_batch(klass, size, **kwargs)

    Create a factory for :obj:`klass` using declarations passed in kwargs;
    return an instance built from that factory,
    or a list of :obj:`size` instances (for :func:`build_batch`).

    :param class klass: Class of the instance to build
    :param int size: Number of instances to build
    :param kwargs: Declarations to use for the generated factory



.. function:: create(klass, **kwargs)
.. function:: create_batch(klass, size, **kwargs)

    Create a factory for :obj:`klass` using declarations passed in kwargs;
    return an instance created from that factory,
    or a list of :obj:`size` instances (for :func:`create_batch`).

    :param class klass: Class of the instance to create
    :param int size: Number of instances to create
    :param kwargs: Declarations to use for the generated factory



.. function:: stub(klass, **kwargs)
.. function:: stub_batch(klass, size, **kwargs)

    Create a factory for :obj:`klass` using declarations passed in kwargs;
    return an instance stubbed from that factory,
    or a list of :obj:`size` instances (for :func:`stub_batch`).

    :param class klass: Class of the instance to stub
    :param int size: Number of instances to stub
    :param kwargs: Declarations to use for the generated factory



.. function:: generate(klass, strategy, **kwargs)
.. function:: generate_batch(klass, strategy, size, **kwargs)

    Create a factory for :obj:`klass` using declarations passed in kwargs;
    return an instance generated from that factory with the :obj:`strategy` strategy,
    or a list of :obj:`size` instances (for :func:`generate_batch`).

    :param class klass: Class of the instance to generate
    :param str strategy: The strategy to use
    :param int size: Number of instances to generate
    :param kwargs: Declarations to use for the generated factory



.. function:: simple_generate(klass, create, **kwargs)
.. function:: simple_generate_batch(klass, create, size, **kwargs)

    Create a factory for :obj:`klass` using declarations passed in kwargs;
    return an instance generated from that factory according to the :obj:`create` flag,
    or a list of :obj:`size` instances (for :func:`simple_generate_batch`).

    :param class klass: Class of the instance to generate
    :param bool create: Whether to build (``False``) or create (``True``) instances
    :param int size: Number of instances to generate
    :param kwargs: Declarations to use for the generated factory


