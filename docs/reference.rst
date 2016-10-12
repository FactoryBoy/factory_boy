Reference
=========

.. currentmodule:: factory

This section offers an in-depth description of factory_boy features.

For internals and customization points, please refer to the :doc:`internals` section.


The :class:`Factory` class
--------------------------

Meta options
""""""""""""

.. class:: FactoryOptions

    .. versionadded:: 2.4.0

    A :class:`Factory`'s behaviour can be tuned through a few settings.

    For convenience, they are declared in a single ``class Meta`` attribute:

    .. code-block:: python

        class MyFactory(factory.Factory):
            class Meta:
                model = MyObject
                abstract = False

    .. attribute:: model

        This optional attribute describes the class of objects to generate.

        If unset, it will be inherited from parent :class:`Factory` subclasses.

        .. versionadded:: 2.4.0

    .. attribute:: abstract

        This attribute indicates that the :class:`Factory` subclass should not
        be used to generate objects, but instead provides some extra defaults.

        It will be automatically set to ``True`` if neither the :class:`Factory`
        subclass nor its parents define the :attr:`~FactoryOptions.model` attribute.

        .. warning:: This flag is reset to ``False`` when a :class:`Factory` subclasses
                     another one if a :attr:`~FactoryOptions.model` is set.

        .. versionadded:: 2.4.0

    .. attribute:: inline_args

        Some factories require non-keyword arguments to their :meth:`~object.__init__`.
        They should be listed, in order, in the :attr:`inline_args`
        attribute:

        .. code-block:: python

            class UserFactory(factory.Factory):
                class Meta:
                    model = User
                    inline_args = ('login', 'email')

                login = 'john'
                email = factory.LazyAttribute(lambda o: '%s@example.com' % o.login)
                firstname = "John"

        .. code-block:: pycon

            >>> UserFactory()
            <User: john>
            >>> User('john', 'john@example.com', firstname="John")  # actual call

        .. versionadded:: 2.4.0

    .. attribute:: exclude

        While writing a :class:`Factory` for some object, it may be useful to
        have general fields helping defining others, but that should not be
        passed to the model class; for instance, a field named 'now' that would
        hold a reference time used by other objects.

        Factory fields whose name are listed in :attr:`exclude` will
        be removed from the set of args/kwargs passed to the underlying class;
        they can be any valid factory_boy declaration:

        .. code-block:: python

            class OrderFactory(factory.Factory):
                class Meta:
                    model = Order
                    exclude = ('now',)

                now = factory.LazyFunction(datetime.datetime.utcnow)
                started_at = factory.LazyAttribute(lambda o: o.now - datetime.timedelta(hours=1))
                paid_at = factory.LazyAttribute(lambda o: o.now - datetime.timedelta(minutes=50))

        .. code-block:: pycon

            >>> OrderFactory()    # The value of 'now' isn't passed to Order()
            <Order: started 2013-04-01 12:00:00, paid 2013-04-01 12:10:00>

            >>> # An alternate value may be passed for 'now'
            >>> OrderFactory(now=datetime.datetime(2013, 4, 1, 10))
            <Order: started 2013-04-01 09:00:00, paid 2013-04-01 09:10:00>

        .. versionadded:: 2.4.0


    .. attribute:: rename

        Sometimes, a model expects a field with a name already used by one
        of :class:`Factory`'s methods.

        In this case, the :attr:`rename` attributes allows to define renaming
        rules: the keys of the :attr:`rename` dict are those used in the
        :class:`Factory` declarations, and their values the new name:

        .. code-block:: python

            class ImageFactory(factory.Factory):
                # The model expects "attributes"
                form_attributes = ['thumbnail', 'black-and-white']

                class Meta:
                    model = Image
                    rename = {'form_attributes': 'attributes'}

        .. versionadded: 2.6.0


    .. attribute:: strategy

        Use this attribute to change the strategy used by a :class:`Factory`.
        The default is :data:`CREATE_STRATEGY`.



Attributes and methods
""""""""""""""""""""""


.. class:: Factory


    **Class-level attributes:**

    .. attribute:: Meta
    .. attribute:: _meta

        .. versionadded:: 2.4.0

        The :class:`FactoryOptions` instance attached to a :class:`Factory` class is available
        as a :attr:`_meta` attribute.

    .. attribute:: Params

        .. versionadded:: 2.7.0

        The extra parameters attached to a :class:`Factory` are declared through a :attr:`Params`
        class.
        See :ref:`the "Parameters" section <parameters>` for more information.

    .. attribute:: _options_class

        .. versionadded:: 2.4.0

        If a :class:`Factory` subclass needs to define additional, extra options, it has to
        provide a custom :class:`FactoryOptions` subclass.

        A pointer to that custom class should be provided as :attr:`_options_class` so that
        the :class:`Factory`-building metaclass can use it instead.


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
        items removed, but before the :attr:`~FactoryOptions.inline_args` extraction
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


    .. classmethod:: _build(cls, model_class, *args, **kwargs)

        .. OHAI_VIM*

        This class method is called whenever a new instance needs to be built.
        It receives the model class (provided to :attr:`~FactoryOptions.model`), and
        the positional and keyword arguments to use for the class once all has
        been computed.

        Subclasses may override this for custom APIs.


    .. classmethod:: _create(cls, model_class, *args, **kwargs)

        .. OHAI_VIM*

        The :meth:`_create` method is called whenever an instance needs to be
        created.
        It receives the same arguments as :meth:`_build`.

        Subclasses may override this for specific persistence backends:

        .. code-block:: python

            class BaseBackendFactory(factory.Factory):
                class Meta:
                    abstract = True  # Optional

                def _create(cls, model_class, *args, **kwargs):
                    obj = model_class(*args, **kwargs)
                    obj.save()
                    return obj

        .. OHAI_VIM*

    .. classmethod:: _after_postgeneration(cls, obj, create, results=None)

        :arg object obj: The object just generated
        :arg bool create: Whether the object was 'built' or 'created'
        :arg dict results: Map of post-generation declaration name to call
                           result

        The :meth:`_after_postgeneration` is called once post-generation
        declarations have been handled.

        Its arguments allow to handle specifically some post-generation return
        values, for instance.


    **Advanced functions:**


    .. classmethod:: reset_sequence(cls, value=None, force=False)

        :arg int value: The value to reset the sequence to
        :arg bool force: Whether to force-reset the sequence

        Allows to reset the sequence counter for a :class:`~factory.Factory`.
        The new value can be passed in as the ``value`` argument:

        .. code-block:: pycon

            >>> SomeFactory.reset_sequence(4)
            >>> SomeFactory._next_sequence
            4

        Since subclasses of a non-:attr:`abstract <factory.FactoryOptions.abstract>`
        :class:`~factory.Factory` share the same sequence counter, special care needs
        to be taken when resetting the counter of such a subclass.

        By default, :meth:`reset_sequence` will raise a :exc:`ValueError` when
        called on a subclassed :class:`~factory.Factory` subclass. This can be
        avoided by passing in the ``force=True`` flag:

        .. code-block:: pycon

            >>> InheritedFactory.reset_sequence()
            Traceback (most recent call last):
              File "factory_boy/tests/test_base.py", line 179, in test_reset_sequence_subclass_parent
                SubTestObjectFactory.reset_sequence()
              File "factory_boy/factory/base.py", line 250, in reset_sequence
                "Cannot reset the sequence of a factory subclass. "
            ValueError: Cannot reset the sequence of a factory subclass. Please call reset_sequence() on the root factory, or call reset_sequence(forward=True).

            >>> InheritedFactory.reset_sequence(force=True)
            >>>

        This is equivalent to calling :meth:`reset_sequence` on the base
        factory in the chain.


.. _parameters:

Parameters
""""""""""

.. versionadded:: 2.7.0

Some models have many fields that can be summarized by a few parameters; for instance,
a train with many cars — each complete with serial number, manufacturer, ...;
or an order that can be pending/shipped/received, with a few fields to describe each step.

When building instances of such models, a couple of parameters can be enough to determine
all other fields; this is handled by the :class:`~Factory.Params` section of a :class:`Factory` declaration.


Simple parameters
~~~~~~~~~~~~~~~~~

Some factories only need little data:

.. code-block:: python

    class ConferenceFactory(factory.Factory):
        class Meta:
            model = Conference

        class Params:
            duration = 'short' # Or 'long'

        start_date = factory.fuzzy.FuzzyDate()
        end_date = factory.LazyAttribute(
            lambda o: o.start_date + datetime.timedelta(days=2 if o.duration == 'short' else 7)
        )
        sprints_start = factory.LazyAttribute(
            lambda o: o.end_date - datetime.timedelta(days=0 if o.duration == 'short' else 1)
        )

.. code-block:: pycon

    >>> Conference(duration='short')
    <Conference: DUTH 2015 (2015-11-05 - 2015-11-08, sprints 2015-11-08)>
    >>> Conference(duration='long')
    <Conference: DjangoConEU 2016 (2016-03-30 - 2016-04-03, sprints 2016-04-02)>


Any simple parameter provided to the :class:`Factory.Params` section is available to the whole factory,
but not passed to the final class (similar to the :attr:`~FactoryOptions.exclude` behavior).


Traits
~~~~~~

.. class:: Trait(**kwargs)

    .. OHAI VIM**

    .. versionadded:: 2.7.0

    A trait's parameters are the fields it should alter when enabled.


For more complex situations, it is helpful to override a few fields at once:

.. code-block:: python

    class OrderFactory(factory.Factory):
        class Meta:
            model = Order

        state = 'pending'
        shipped_on = None
        shipped_by = None

        class Params:
            shipped = factory.Trait(
                state='shipped',
                shipped_on=datetime.date.today(),
                shipped_by=factory.SubFactory(EmployeeFactory),
            )

Such a :class:`Trait` is activated or disabled by a single boolean field:


.. code-block:: pycon

    >>> OrderFactory()
    <Order: pending>
    Order(state='pending')
    >>> OrderFactory(shipped=True)
    <Order: shipped by John Doe on 2016-04-02>


A :class:`Trait` can be enabled/disabled by a :class:`Factory` subclass:

.. code-block:: python

    class ShippedOrderFactory(OrderFactory):
        shipped = True


Values set in a :class:`Trait` can be overridden by call-time values:

.. code-block:: pycon

    >>> OrderFactory(shipped=True, shipped_on=last_year)
    <Order: shipped by John Doe on 2015-04-20>


:class:`Traits <Trait>` can be chained:

.. code-block:: python

    class OrderFactory(factory.Factory):
        class Meta:
            model = Order

        # Can be pending/shipping/received
        state = 'pending'
        shipped_on = None
        shipped_by = None
        received_on = None
        received_by = None

        class Params:
            shipped = factory.Trait(
                state='shipped',
                shipped_on=datetime.date.today,
                shipped_by=factory.SubFactory(EmployeeFactory),
            )
            received = factory.Trait(
                shipped=True,
                state='received',
                shipped_on=datetime.date.today - datetime.timedelta(days=4),
                received_on=datetime.date.today,
                received_by=factory.SubFactory(CustomerFactory),
            )

.. code-block:: pycon

    >>> OrderFactory(received=True)
    <Order: shipped by John Doe on 2016-03-20, received by Joan Smith on 2016-04-02>



A :class:`Trait` might be overridden in :class:`Factory` subclasses:

.. code-block:: python

    class LocalOrderFactory(OrderFactory):

        class Params:
            received = factory.Trait(
                shipped=True,
                state='received',
                shipped_on=datetime.date.today - datetime.timedelta(days=1),
                received_on=datetime.date.today,
                received_by=factory.SubFactory(CustomerFactory),
            )


.. code-block:: pycon

    >>> LocalOrderFactory(received=True)
    <Order: shipped by John Doe on 2016-04-01, received by Joan Smith on 2016-04-02>


.. note:: When overriding a :class:`Trait`, the whole declaration **MUST** be replaced.


.. _strategies:

Strategies
""""""""""

factory_boy supports two main strategies for generating instances, plus stubs.


.. data:: BUILD_STRATEGY

    The 'build' strategy is used when an instance should be created,
    but not persisted to any datastore.

    It is usually a simple call to the :meth:`~object.__init__` method of the
    :attr:`~FactoryOptions.model` class.


.. data:: CREATE_STRATEGY

    The 'create' strategy builds and saves an instance into its appropriate datastore.

    This is the default strategy of factory_boy; it would typically instantiate an
    object, then save it:

    .. code-block:: pycon

        >>> obj = self._associated_class(*args, **kwargs)
        >>> obj.save()
        >>> return obj

    .. OHAI_VIM*

    .. warning:: For backward compatibility reasons, the default behaviour of
                 factory_boy is to call ``MyClass.objects.create(*args, **kwargs)``
                 when using the ``create`` strategy.

                 That policy will be used if the
                 :attr:`associated class <FactoryOptions.model>` has an ``objects``
                 attribute *and* the :meth:`~Factory._create` classmethod of the
                 :class:`Factory` wasn't overridden.


.. function:: use_strategy(strategy)

    *Decorator*

    Change the default strategy of the decorated :class:`Factory` to the chosen :obj:`strategy`:

    .. code-block:: python

        @use_strategy(factory.BUILD_STRATEGY)
        class UserBuildingFactory(UserFactory):
            pass


.. data:: STUB_STRATEGY

    The 'stub' strategy is an exception in the factory_boy world: it doesn't return
    an instance of the :attr:`~FactoryOptions.model` class, and actually doesn't
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

    An :attr:`abstract <FactoryOptions.abstract>` :class:`Factory`,
    with a default strategy set to :data:`STUB_STRATEGY`.


.. function:: debug(logger='factory', stream=None)

    :param str logger: The name of the logger to enable debug for
    :param file stream: The stream to send debug output to, defaults to :obj:`sys.stderr`

    Context manager to help debugging factory_boy behavior.
    It will temporarily put the target logger (e.g ``'factory'``) in debug mode,
    sending all output to :obj`~sys.stderr`;
    upon leaving the context, the logging levels are reset.

    A typical use case is to understand what happens during a single factory call:

    .. code-block:: python

        with factory.debug():
            obj = TestModel2Factory()

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


.. _declarations:

Declarations
------------


Faker
"""""

.. class:: Faker(provider, locale=None, **kwargs)

    .. OHAIVIM**

    In order to easily define realistic-looking factories,
    use the :class:`Faker` attribute declaration.

    This is a wrapper around `fake-factory <https://pypi.python.org/pypi/fake-factory>`_;
    its argument is the name of a ``fake-factory`` provider:

    .. code-block:: python

        class UserFactory(factory.Factory):
            class Meta:
                model = User

            name = factory.Faker('name')

    .. code-block:: pycon

        >>> user = UserFactory()
        >>> user.name
        'Lucy Cechtelar'


    .. attribute:: locale

        If a custom locale is required for one specific field,
        use the ``locale`` parameter:

        .. code-block:: python

            class UserFactory(factory.Factory):
                class Meta:
                    model = User

                name = factory.Faker('name', locale='fr_FR')

        .. code-block:: pycon

            >>> user = UserFactory()
            >>> user.name
            'Jean Valjean'


    .. classmethod:: override_default_locale(cls, locale)

        If the locale needs to be overridden for a whole test,
        use :meth:`~factory.Faker.override_default_locale`:

        .. code-block:: pycon

            >>> with factory.Faker.override_default_locale('de_DE'):
            ...     UserFactory()
            <User: Johannes Brahms>

    .. classmethod:: add_provider(cls, locale=None)

        Some projects may need to fake fields beyond those provided by ``fake-factory``;
        in such cases, use :meth:`factory.Faker.add_provider` to declare additional providers
        for those fields:

        .. code-block:: python

            factory.Faker.add_provider(SmileyProvider)

            class FaceFactory(factory.Factory):
                class Meta:
                    model = Face

                smiley = factory.Faker('smiley')


LazyFunction
""""""""""""

.. class:: LazyFunction(method_to_call)

The :class:`LazyFunction` is the simplest case where the value of an attribute
does not depend on the object being built.

It takes as argument a method to call (function, lambda...); that method should
not take any argument, though keyword arguments are safe but unused,
and return a value.

.. code-block:: python

    class LogFactory(factory.Factory):
        class Meta:
            model = models.Log

        timestamp = factory.LazyFunction(datetime.now)

.. code-block:: pycon

    >>> LogFactory()
    <Log: log at 2016-02-12 17:02:34>

    >>> # The LazyFunction can be overriden
    >>> LogFactory(timestamp=now - timedelta(days=1))
    <Log: log at 2016-02-11 17:02:34>

Decorator
~~~~~~~~~

The class :class:`LazyFunction` does not provide a decorator.

For complex cases, use :meth:`LazyAttribute.lazy_attribute` directly.

LazyAttribute
"""""""""""""

.. class:: LazyAttribute(method_to_call)

The :class:`LazyAttribute` is a simple yet extremely powerful building brick
for extending a :class:`Factory`.

It takes as argument a method to call (usually a lambda); that method should
accept the object being built as sole argument, and return a value.

.. code-block:: python

    class UserFactory(factory.Factory):
        class Meta:
            model = User

        username = 'john'
        email = factory.LazyAttribute(lambda o: '%s@example.com' % o.username)

.. code-block:: pycon

    >>> u = UserFactory()
    >>> u.email
    'john@example.com'

    >>> u = UserFactory(username='leo')
    >>> u.email
    'leo@example.com'


The object passed to :class:`LazyAttribute` is not an instance of the target class,
but instead a :class:`~containers.LazyStub`: a temporary container that computes
the value of all declared fields.


Decorator
~~~~~~~~~

.. function:: lazy_attribute

If a simple lambda isn't enough, you may use the :meth:`lazy_attribute` decorator instead.

This decorates an instance method that should take a single argument, ``self``;
the name of the method will be used as the name of the attribute to fill with the
return value of the method:

.. code-block:: python

    class UserFactory(factory.Factory)
        class Meta:
            model = User

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
          This feature was deprecated in 1.3.0 and will be removed in 2.0.0.


.. code-block:: python

    class UserFactory(factory.Factory)
        class Meta:
            model = User

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
        class Meta:
            model = User

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
        class Meta:
            model = User

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

When a :class:`Factory` inherits from another :class:`Factory` and the `model`
of the subclass inherits from the `model` of the parent, the sequence counter
is shared across the :class:`Factory` classes:

.. code-block:: python

    class UserFactory(factory.Factory):
        class Meta:
            model = User

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


Forcing a sequence counter
~~~~~~~~~~~~~~~~~~~~~~~~~~

If a specific value of the sequence counter is required for one instance, the
``__sequence`` keyword argument should be passed to the factory method.

This will force the sequence counter during the call, without altering the
class-level value.

.. code-block:: python

    class UserFactory(factory.Factory):
        class Meta:
            model = User

        uid = factory.Sequence(int)

.. code-block:: pycon

    >>> UserFactory()
    <User: 0>
    >>> UserFactory()
    <User: 1>
    >>> UserFactory(__sequence=42)
    <User: 42>


.. warning:: The impact of setting ``__sequence=n`` on a ``_batch`` call is
             undefined. Each generated instance may share a same counter, or
             use incremental values starting from the forced value.


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
        class Meta:
            model = User

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
        class Meta:
            model = User

        login = 'john'

        @lazy_attribute_sequence
        def email(self, n):
            bucket = n % 10
            return '%s@s%d.example.com' % (self.login, bucket)


SubFactory
""""""""""

.. class:: SubFactory(factory, **kwargs)

    .. OHAI_VIM**

This attribute declaration calls another :class:`Factory` subclass,
selecting the same build strategy and collecting extra kwargs in the process.

The :class:`SubFactory` attribute should be called with:

* A :class:`Factory` subclass as first argument, or the fully qualified import
  path to that :class:`Factory` (see :ref:`Circular imports <subfactory-circular>`)
* An optional set of keyword arguments that should be passed when calling that
  factory


.. note::

          When passing an actual :class:`~factory.Factory` for the
          :attr:`~factory.SubFactory.factory` argument, make sure to pass
          the class and not instance (i.e no ``()`` after the class):

          .. code-block:: python

              class FooFactory(factory.Factory):
                  class Meta:
                      model = Foo

                  bar = factory.SubFactory(BarFactory)  # Not BarFactory()


Definition
~~~~~~~~~~

.. code-block:: python


    # A standard factory
    class UserFactory(factory.Factory):
        class Meta:
            model = User

        # Various fields
        first_name = 'John'
        last_name = factory.Sequence(lambda n: 'D%se' % ('o' * n))  # De, Doe, Dooe, Doooe, ...
        email = factory.LazyAttribute(lambda o: '%s.%s@example.org' % (o.first_name.lower(), o.last_name.lower()))

    # A factory for an object with a 'User' field
    class CompanyFactory(factory.Factory):
        class Meta:
            model = Company

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
        class Meta:
            model = User

        username = 'john'
        main_group = factory.SubFactory('users.factories.GroupFactory')

    class GroupFactory(factory.Factory):
        class Meta:
            model = Group

        name = "MyGroup"
        owner = factory.SubFactory(UserFactory)


Obviously, such circular relationships require careful handling of loops:

.. code-block:: pycon

    >>> owner = UserFactory(main_group=None)
    >>> UserFactory(main_group__owner=owner)
    <john (group: MyGroup)>


SelfAttribute
"""""""""""""

.. class:: SelfAttribute(dotted_path_to_attribute)

Some fields should reference another field of the object being constructed, or an attribute thereof.

This is performed by the :class:`~factory.SelfAttribute` declaration.
That declaration takes a single argument, a dot-delimited path to the attribute to fetch:

.. code-block:: python

    class UserFactory(factory.Factory)
        class Meta:
            model = User

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
        class Meta:
            model = User

        language = 'en'


    class CompanyFactory(factory.Factory):
        class Meta:
            model = Company

        country = factory.SubFactory(CountryFactory)
        owner = factory.SubFactory(UserFactory, language=factory.SelfAttribute('..country.language'))

.. code-block:: pycon

    >>> company = CompanyFactory()
    >>> company.country.language
    'fr'
    >>> company.owner.language
    'fr'

Obviously, this "follow parents" ability also handles overriding some attributes on call:

.. code-block:: pycon

    >>> company = CompanyFactory(country=china)
    >>> company.owner.language
    'cn'


This feature is also available to :class:`LazyAttribute` and :class:`LazyAttributeSequence`,
through the :attr:`~containers.LazyStub.factory_parent` attribute of the passed-in object:

.. code-block:: python

    class CompanyFactory(factory.Factory):
        class Meta:
            model = Company
        country = factory.SubFactory(CountryFactory)
        owner = factory.SubFactory(UserFactory,
            language=factory.LazyAttribute(lambda user: user.factory_parent.country.language),
        )


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

    .. method:: reset()

        Reset the internal iterator used by the attribute, so that the next value
        will be the first value generated by the iterator.

        May be called several times.


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
        class Meta:
            model = User

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
        class Meta:
            model = User

        @factory.iterator
        def name():
            with open('test/data/names.dat', 'r') as f:
                for line in f:
                    yield line


Resetting
~~~~~~~~~

In order to start back at the first value in an :class:`Iterator`,
simply call the :meth:`~Iterator.reset` method of that attribute
(accessing it from the bare :class:`~Factory` subclass):

.. code-block:: pycon

    >>> UserFactory().lang
    'en'
    >>> UserFactory().lang
    'fr'
    >>> UserFactory.lang.reset()
    >>> UserFactory().lang
    'en'


Dict and List
"""""""""""""

When a factory expects lists or dicts as arguments, such values can be generated
through the whole range of factory_boy declarations,
with the :class:`Dict` and :class:`List` attributes:

.. class:: Dict(params[, dict_factory=factory.DictFactory])

    The :class:`Dict` class is used for dict-like attributes.
    It receives as non-keyword argument a dictionary of fields to define, whose
    value may be any factory-enabled declarations:

    .. code-block:: python

        class UserFactory(factory.Factory):
            class Meta:
                model = User

            is_superuser = False
            roles = factory.Dict({
                'role1': True,
                'role2': False,
                'role3': factory.Iterator([True, False]),
                'admin': factory.SelfAttribute('..is_superuser'),
            })

    .. note:: Declarations used as a :class:`Dict` values are evaluated within
              that :class:`Dict`'s context; this means that you must use
              the ``..foo`` syntax to access fields defined at the factory level.

              On the other hand, the :class:`Sequence` counter is aligned on the
              containing factory's one.


    The :class:`Dict` behaviour can be tuned through the following parameters:

    .. attribute:: dict_factory

        The actual factory to use for generating the dict can be set as a keyword
        argument, if an exotic dictionary-like object (SortedDict, ...) is required.


.. class:: List(items[, list_factory=factory.ListFactory])

    The :class:`List` can be used for list-like attributes.

    Internally, the fields are converted into a ``index=value`` dict, which
    makes it possible to override some values at use time:

    .. code-block:: python

        class UserFactory(factory.Factory):
            class Meta:
                model = User

            flags = factory.List([
                'user',
                'active',
                'admin',
            ])

    .. code-block:: pycon

        >>> u = UserFactory(flags__2='superadmin')
        >>> u.flags
        ['user', 'active', 'superadmin']


    The :class:`List` behaviour can be tuned through the following parameters:

    .. attribute:: list_factory

        The actual factory to use for generating the list can be set as a keyword
        argument, if another type (tuple, set, ...) is required.



Post-generation hooks
"""""""""""""""""""""

Some objects expect additional method calls or complex processing for proper definition.
For instance, a ``User`` may need to have a related ``Profile``, where the ``Profile`` is built from the ``User`` object.

To support this pattern, factory_boy provides the following tools:
  - :class:`PostGenerationMethodCall`: allows you to hook a particular attribute to a function call
  - :class:`PostGeneration`: this class allows calling a given function with the generated object as argument
  - :func:`post_generation`: decorator performing the same functions as :class:`PostGeneration`
  - :class:`RelatedFactory`: this builds or creates a given factory *after* building/creating the first Factory.

Post-generation hooks are called in the same order they are declared in the factory class, so that
functions can rely on the side effects applied by the previous post-generation hook.


Extracting parameters
"""""""""""""""""""""

All post-building hooks share a common base for picking parameters from the
set of attributes passed to the :class:`Factory`.

For instance, a :class:`PostGeneration` hook is declared as ``post``:

.. code-block:: python

    class SomeFactory(factory.Factory):
        class Meta:
            model = SomeObject

        @post_generation
        def post(obj, create, extracted, **kwargs):
            obj.set_origin(create)

.. OHAI_VIM**


When calling the factory, some arguments will be extracted for this method:

- If a ``post`` argument is passed, it will be passed as the ``extracted`` field
- Any argument starting with ``post__XYZ`` will be extracted, its ``post__`` prefix
  removed, and added to the kwargs passed to the post-generation hook.

Extracted arguments won't be passed to the :attr:`~FactoryOptions.model` class.

Thus, in the following call:

.. code-block:: pycon

    >>> SomeFactory(
        post=1,
        post_x=2,
        post__y=3,
        post__z__t=42,
    )

The ``post`` hook will receive ``1`` as ``extracted`` and ``{'y': 3, 'z__t': 42}``
as keyword arguments; ``{'post_x': 2}`` will be passed to ``SomeFactory._meta.model``.


RelatedFactory
""""""""""""""

.. class:: RelatedFactory(factory, factory_related_name='', **kwargs)

    .. OHAI_VIM**

    A :class:`RelatedFactory` behaves mostly like a :class:`SubFactory`,
    with the main difference that the related :class:`Factory` will be generated
    *after* the base :class:`Factory`.


    .. attribute:: factory

        As for :class:`SubFactory`, the :attr:`factory` argument can be:

        - A :class:`Factory` subclass
        - Or the fully qualified path to a :class:`Factory` subclass
          (see :ref:`subfactory-circular` for details)

    .. attribute:: name

        The generated object (where the :class:`RelatedFactory` attribute will
        set) may be passed to the related factory if the :attr:`factory_related_name` parameter
        is set.

        It will be passed as a keyword argument, using the :attr:`name` value as
        keyword:


.. note::

          When passing an actual :class:`~factory.Factory` for the
          :attr:`~factory.RelatedFactory.factory` argument, make sure to pass
          the class and not instance (i.e no ``()`` after the class):

          .. code-block:: python

              class FooFactory(factory.Factory):
                  class Meta:
                      model = Foo

                  bar = factory.RelatedFactory(BarFactory)  # Not BarFactory()


.. code-block:: python

    class CityFactory(factory.Factory):
        class Meta:
            model = City

        capital_of = None
        name = "Toronto"

    class CountryFactory(factory.Factory):
        class Meta:
            model = Country

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

If a value if passed for the :class:`RelatedFactory` attribute, this disables
:class:`RelatedFactory` generation:

.. code-block:: pycon

    >>> france = CountryFactory()
    >>> paris = City.objects.get()
    >>> paris
    <City: Paris>
    >>> reunion = CountryFactory(capital_city=paris)
    >>> City.objects.count()  # No new capital_city generated
    1
    >>> guyane = CountryFactory(capital_city=paris, capital_city__name='Kourou')
    >>> City.objects.count()  # No new capital_city generated, ``name`` ignored.
    1


.. note:: The target of the :class:`RelatedFactory` is evaluated *after* the initial factory has been instantiated.
          This means that calls to :class:`factory.SelfAttribute` cannot go higher than this :class:`RelatedFactory`:

          .. code-block:: python

              class CountryFactory(factory.Factory):
                  class Meta:
                      model = Country

                  lang = 'fr'
                  capital_city = factory.RelatedFactory(CityFactory, 'capital_of',
                      # factory.SelfAttribute('..lang') will crash, since the context of
                      # ``CountryFactory`` has already been evaluated.
                      main_lang=factory.SelfAttribute('capital_of.lang'),
                  )


PostGeneration
""""""""""""""

.. class:: PostGeneration(callable)

The :class:`PostGeneration` declaration performs actions once the model object
has been generated.

Its sole argument is a callable, that will be called once the base object has
  been generated.

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
        class Meta:
            model = User

        login = 'john'
        make_mbox = factory.PostGeneration(
                lambda obj, create, extracted, **kwargs: os.makedirs(obj.login))

.. OHAI_VIM**

Decorator
~~~~~~~~~

.. function:: post_generation

A decorator is also provided, decorating a single method accepting the same
``obj``, ``created``, ``extracted`` and keyword arguments as :class:`PostGeneration`.


.. code-block:: python

    class UserFactory(factory.Factory):
        class Meta:
            model = User

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

.. class:: PostGenerationMethodCall(method_name, *args, **kwargs)

    .. OHAI_VIM*

    The :class:`PostGenerationMethodCall` declaration will call a method on
    the generated object just after instantiation. This declaration class
    provides a friendly means of generating attributes of a factory instance
    during initialization. The declaration is created using the following arguments:

    .. attribute:: method_name

        The name of the method to call on the :attr:`~FactoryOptions.model` object

    .. attribute:: args

        The default set of unnamed arguments to pass to the method given in
        :attr:`method_name`

    .. attribute:: kwargs

        The default set of keyword arguments to pass to the method given in
        :attr:`method_name`

Once the factory instance has been generated, the method specified in
:attr:`~PostGenerationMethodCall.method_name` will be called on the generated object
with any arguments specified in the :class:`PostGenerationMethodCall` declaration, by
default.

For example, to set a default password on a generated User instance
during instantiation, we could make a declaration for a ``password``
attribute like below:

.. code-block:: python

    class UserFactory(factory.Factory):
        class Meta:
            model = User

        username = 'user'
        password = factory.PostGenerationMethodCall('set_password',
                                                    'defaultpassword')

When we instantiate a user from the ``UserFactory``, the factory
will create a password attribute by calling ``User.set_password('defaultpassword')``.
Thus, by default, our users will have a password set to ``'defaultpassword'``.

.. code-block:: pycon

    >>> u = UserFactory()                             # Calls user.set_password('defaultpassword')
    >>> u.check_password('defaultpassword')
    True

If the :class:`PostGenerationMethodCall` declaration contained no
arguments or one argument, an overriding value can be passed
directly to the method through a keyword argument matching the attribute name.
For example we can override the default password specified in the declaration
above by simply passing in the desired password as a keyword argument to the
factory during instantiation.

.. code-block:: pycon

    >>> other_u = UserFactory(password='different')   # Calls user.set_password('different')
    >>> other_u.check_password('defaultpassword')
    False
    >>> other_u.check_password('different')
    True

.. note::

    For Django models, unless the object method called by
    :class:`PostGenerationMethodCall` saves the object back to the
    database, we will have to explicitly remember to save the object back
    if we performed a ``create()``.

    .. code-block:: pycon

        >>> u = UserFactory.create()  # u.password has not been saved back to the database
        >>> u.save()                  # we must remember to do it ourselves


    We can avoid this by subclassing from :class:`DjangoModelFactory`,
    instead, e.g.,

    .. code-block:: python

        class UserFactory(factory.django.DjangoModelFactory):
            class Meta:
                model = User

            username = 'user'
            password = factory.PostGenerationMethodCall('set_password',
                                                        'defaultpassword')


If instead the :class:`PostGenerationMethodCall` declaration uses two or
more positional arguments, the overriding value must be an iterable. For
example, if we declared the ``password`` attribute like the following,

.. code-block:: python

    class UserFactory(factory.Factory):
        class Meta:
            model = User

        username = 'user'
        password = factory.PostGenerationMethodCall('set_password', '', 'sha1')

then we must be cautious to pass in an iterable for the ``password``
keyword argument when creating an instance from the factory:

.. code-block:: pycon

    >>> UserFactory()                           # Calls user.set_password('', 'sha1')
    >>> UserFactory(password=('test', 'md5'))   # Calls user.set_password('test', 'md5')

    >>> # Always pass in a good iterable:
    >>> UserFactory(password=('test',))         # Calls user.set_password('test')
    >>> UserFactory(password='test')            # Calls user.set_password('t', 'e', 's', 't')


.. note:: While this setup provides sane and intuitive defaults for most users,
          it prevents passing more than one argument when the declaration used
          zero or one.

          In such cases, users are advised to either resort to the more powerful
          :class:`PostGeneration` or to add the second expected argument default
          value to the :class:`PostGenerationMethodCall` declaration
          (``PostGenerationMethodCall('method', 'x', 'y_that_is_the_default')``)

Keywords extracted from the factory arguments are merged into the
defaults present in the :class:`PostGenerationMethodCall` declaration.

.. code-block:: pycon

    >>> UserFactory(password__disabled=True)    # Calls user.set_password('', 'sha1', disabled=True)


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
            class Meta:
                model = User

            login = 'john'
            email = factory.LazyAttribute(lambda u: '%s@example.com' % u.login)

    An alternate base class to :class:`Factory` can be specified in the
    ``FACTORY_CLASS`` argument:

    .. code-block:: python

        UserFactory = make_factory(models.User,
            login='john',
            email=factory.LazyAttribute(lambda u: '%s@example.com' % u.login),
            FACTORY_CLASS=factory.django.DjangoModelFactory,
        )

        # This is equivalent to:

        class UserFactory(factory.django.DjangoModelFactory):
            class Meta:
                model = models.User

            login = 'john'
            email = factory.LazyAttribute(lambda u: '%s@example.com' % u.login)

    .. versionadded:: 2.0.0
        The ``FACTORY_CLASS`` kwarg was added in 2.0.0.


Instance building
"""""""""""""""""

The :mod:`factory` module provides a bunch of shortcuts for creating a factory and
extracting instances from them:

.. function:: build(klass, FACTORY_CLASS=None, **kwargs)
.. function:: build_batch(klass, size, FACTORY_CLASS=None, **kwargs)

    Create a factory for :obj:`klass` using declarations passed in kwargs;
    return an instance built from that factory,
    or a list of :obj:`size` instances (for :func:`build_batch`).

    :param class klass: Class of the instance to build
    :param int size: Number of instances to build
    :param kwargs: Declarations to use for the generated factory
    :param FACTORY_CLASS: Alternate base class (instead of :class:`Factory`)



.. function:: create(klass, FACTORY_CLASS=None, **kwargs)
.. function:: create_batch(klass, size, FACTORY_CLASS=None, **kwargs)

    Create a factory for :obj:`klass` using declarations passed in kwargs;
    return an instance created from that factory,
    or a list of :obj:`size` instances (for :func:`create_batch`).

    :param class klass: Class of the instance to create
    :param int size: Number of instances to create
    :param kwargs: Declarations to use for the generated factory
    :param FACTORY_CLASS: Alternate base class (instead of :class:`Factory`)



.. function:: stub(klass, FACTORY_CLASS=None, **kwargs)
.. function:: stub_batch(klass, size, FACTORY_CLASS=None, **kwargs)

    Create a factory for :obj:`klass` using declarations passed in kwargs;
    return an instance stubbed from that factory,
    or a list of :obj:`size` instances (for :func:`stub_batch`).

    :param class klass: Class of the instance to stub
    :param int size: Number of instances to stub
    :param kwargs: Declarations to use for the generated factory
    :param FACTORY_CLASS: Alternate base class (instead of :class:`Factory`)



.. function:: generate(klass, strategy, FACTORY_CLASS=None, **kwargs)
.. function:: generate_batch(klass, strategy, size, FACTORY_CLASS=None, **kwargs)

    Create a factory for :obj:`klass` using declarations passed in kwargs;
    return an instance generated from that factory with the :obj:`strategy` strategy,
    or a list of :obj:`size` instances (for :func:`generate_batch`).

    :param class klass: Class of the instance to generate
    :param str strategy: The strategy to use
    :param int size: Number of instances to generate
    :param kwargs: Declarations to use for the generated factory
    :param FACTORY_CLASS: Alternate base class (instead of :class:`Factory`)



.. function:: simple_generate(klass, create, FACTORY_CLASS=None, **kwargs)
.. function:: simple_generate_batch(klass, create, size, FACTORY_CLASS=None, **kwargs)

    Create a factory for :obj:`klass` using declarations passed in kwargs;
    return an instance generated from that factory according to the :obj:`create` flag,
    or a list of :obj:`size` instances (for :func:`simple_generate_batch`).

    :param class klass: Class of the instance to generate
    :param bool create: Whether to build (``False``) or create (``True``) instances
    :param int size: Number of instances to generate
    :param kwargs: Declarations to use for the generated factory
    :param FACTORY_CLASS: Alternate base class (instead of :class:`Factory`)


