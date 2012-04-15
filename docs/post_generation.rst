PostGenerationHook
==================


Some objects expect additional method calls or complex processing for proper definition.
For instance, a ``User`` may need to have a related ``Profile``, where the ``Profile`` is built from the ``User`` object.

To support this pattern, factory_boy provides the following tools:
  - :py:class:`factory.PostGeneration`: this class allows calling a given function with the generated object as argument
  - :py:func:`factory.post_generation`: decorator performing the same functions as :py:class:`~factory.PostGeneration`
  - :py:class:`factory.RelatedFactory`: this builds or creates a given factory *after* building/creating the first Factory.


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
