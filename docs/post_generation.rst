PostGenerationHook
==================


Some objects expect additional method calls or complex processing for proper definition.
For instance, a ``User`` may need to have a related ``Profile``, where the ``Profile`` is built from the ``User`` object.

To support this pattern, factory_boy provides the following tools:
  - :py:class:`factory.PostGenerationMethodCall`: and
    :py:class:`factory.DjangoPostGenerationMethodCall` allow you to hook
    a particular attribute to a function call; see
    `the example below`_
  - :py:class:`factory.PostGeneration`: this class allows calling a given function with the generated object as argument
  - :py:func:`factory.post_generation`: decorator performing the same functions as :py:class:`~factory.PostGeneration`
  - :py:class:`factory.RelatedFactory`: this builds or creates a given factory *after* building/creating the first Factory.


.. _the example below: `PostGenerationMethodCall and DjangoPostGenerationMethodCall`_


Passing arguments to a post-generation hook
-------------------------------------------

A post-generation hook will be defined with a given attribute name.
When calling the ``Factory``, some arguments will be passed to the post-generation hook instead of being available for ``Factory`` building:

  - An argument with the same name as the post-generation hook attribute will be passed to the hook
  - All arguments beginning with that name and ``__`` will be passed to the hook, after removing the prefix.

Example::

    class MyFactory(factory.Factory):
        blah = factory.PostGeneration(lambda obj, create, extracted, **kwargs: 42)

    MyFactory(
        blah=42,  # Passed in the 'extracted' argument of the lambda
        blah__foo=1,  # Passed in kwargs as 'foo': 1
        blah__baz=2,  # Passed in kwargs as 'baz': 2
        blah_bar=3,  # Not passed
    )

The prefix used for extraction can be changed by setting the ``extract_prefix`` argument of the hook::

    class MyFactory(factory.Factory):
        @factory.post_generation(extract_prefix='bar')
        def foo(self, create, extracted, **kwargs):
            self.foo = extracted

    MyFactory(
        bar=42,  # Will be passed to 'extracted'
        bar__baz=13,  # Will be passed as 'baz': 13 in kwargs
        foo=2,  # Won't be passed to the post-generation hook
    )


PostGeneration and @post_generation
-----------------------------------

Both declarations wrap a function, which will be called with the following arguments:
  - ``obj``: the generated factory
  - ``create``: whether the factory was "built" or "created"
  - ``extracted``: if the :py:class:`~factory.PostGeneration` was declared as attribute ``foo``,
    and another value was given for ``foo`` when calling the ``Factory``,
    that value will be available in the ``extracted`` parameter.
  - other keyword args are extracted from those passed to the ``Factory`` with the same prefix as the name of the :py:class:`~factory.PostGeneration` attribute


PostGenerationMethodCall and DjangoPostGenerationMethodCall
-----------------------------------------------------------

These two classes provide a friendly means of generating attributes of a
factory during instantiation by calling a method belonging to the
``FACTORY_FOR`` class. The attribute is declared with the following
arguments:

  - ``method_name``: the name of the method to call on the
    ``FACTORY_FOR`` object
  - ``extract_prefix``: if a string, the keyword argument prefix by
    which the field will get its overriding arguments, otherwise if
    ``None``, defaults to the name of the attribute
  - ``*args``: the default set of unnamed arguments to pass to the
    method given in ``method_name``
  - ``**kwargs``: the default set of keyword arguments to pass to the
    method gien in ``method_name``

To see an example of the usefulness of these
fields, let's take again the ``UserFactory`` model and the need to
generate a password: ::

    class UserFactory(factory.Factory):
        FACTORY_FOR = User

        username = 'user'
        password = factory.PostGenerationMethodCall(
                'set_password', None, 'defaultpassword')

Now when we instantiate a user from the ``UserFactory``, the factory
will set the password attribute by calling the ``User.set_password``
method, passing in ``'defaultpassword'`` as the argument to
``User.set_password``. Thus, by default, our users will have a password
set to ``'defaultpassword'``. ::

    >>> from factories import UserFactory
    >>> u = UserFactory.build()
    >>> u.check_password('defaultpassword')
    True

If we need to override that password, we can simply pass in the desired
password to use as a keyword argument to the factory during
instantiation. ::

    >>> other_u = UserFactory.build(password='different')
    >>> other_u.check_password('defaultpassword')
    False
    >>> other_u.check_password('different')
    True

Unless the object method called by :py:class:`PostGenerationMethodCall` saves the object back to the database, we will have to explicitly remember to save the object back if we performed a ``create()``. ::

    >>> u = UserFactory.create()  # u.password has not been saved back to the database
    >>> u.save()                  # we must remember to do it ourselves

:py:class:`DjangoPostGenerationMethodCall` provides a shortcut to solve
this problem. Using :py:class:`DjangoPostGenerationMethodCall`, when a factory is instantiated with ``create()``,
:py:class:`DjangoPostGenerationMethodCall` will call the instance's
``save()`` method after making the call to the object method passed in
as an argument to :py:class:`DjangoPostGenerationMethodCall`. ::

    class PasswordSavingUserFactory(factory.Factory):
        FACTORY_FOR = User

        username = 'user'
        password = factory.DjangoPostGenerationMethodCall(
                'set_password', None, 'defaultpassword')

With this new ``PasswordSavingUserFactory`` class, we don't have to
remember to save back to the database during ``create()``. ::

    >>> u = PasswordSavingUserFactory.build()   # nothing will be saved to the database as usual
    >>> other_u = PasswordSavingUserFactory.create()  # no need to call other_u.save() after; the password has already been committed to the DB

RelatedFactory
--------------

This is declared with the following arguments:
  - ``factory``: the :py:class:`~factory.Factory` to call
  - ``name``: the keyword to use when passing this object to the related :py:class:`~factory.Factory`; if empty, the object won't be passed to the related :py:class:`~factory.Factory`
  - Extra keyword args which will be passed to the factory

When the object is built, the keyword arguments passed to the related :py:class:`~factory.Factory` are:
  - ``name: obj`` if ``name`` was passed when defining the :py:class:`~factory.RelatedFactory`
  - extra keyword args defined in the :py:class:`~factory.RelatedFactory` definition, overridden by any prefixed arguments passed to the object definition


Example::

    class RelatedObjectFactory(factory.Factory):
        FACTORY_FOR = RelatedObject
        one = 1
        two = 2
        related = None

    class ObjectWithRelatedFactory(factory.Factory):
        FACTORY_FOR = SomeObject
        foo = factory.RelatedFactory(RelatedObjectFactory, 'related', one=2)

    ObjectWithRelatedFactory(foo__two=3)

The ``RelatedObject`` will be called with:
  - ``one=2``
  - ``two=3``
  - ``related=<SomeObject>``
