Internals
=========

.. currentmodule:: factory

Behind the scenes: steps performed when parsing a factory declaration, and when calling it.


This section will be based on the following factory declaration:

.. literalinclude:: ../tests/test_docs_internals.py
    :pyobject: UserFactory


Parsing, Step 1: Metaclass and type declaration
-----------------------------------------------

1. Python parses the declaration and calls (thanks to the metaclass declaration):

   .. code-block:: python

        factory.base.BaseFactory.__new__(
            'UserFactory',
            (factory.Factory,),
            attributes,
        )

2. That metaclass removes :attr:`~Factory.Meta` and :attr:`~Factory.Params` from the class attributes,
   then generate the actual factory class (according to standard Python rules)
3. It initializes a :class:`FactoryOptions` object, and links it to the class


Parsing, Step 2: adapting the class definition
-----------------------------------------------

1. The :class:`FactoryOptions` reads the options from the :attr:`class Meta <Factory.Meta>` declaration
2. It finds a few specific pointer (loading the model class, finding the reference
   factory for the sequence counter, etc.)
3. It copies declarations and parameters from parent classes
4. It scans current class attributes (from ``vars()``) to detect pre/post declarations
5. Declarations are split among pre-declarations and post-declarations
   (a raw value shadowing a post-declaration is seen as a post-declaration)


.. note:: A declaration for ``foo__bar`` will be converted into parameter ``bar``
          for declaration ``foo``.


Instantiating, Step 1: Converging entry points
----------------------------------------------

First, decide the strategy:

- If the entry point is specific to a strategy (:meth:`~Factory.build`,
  :meth:`~Factory.create_batch`, ...), use it
- If it is generic (:meth:`~Factory.generate`, :meth:`Factory.__call__`),
  use the strategy defined at the :attr:`class Meta <Factory.Meta>` level


Then, we'll pass the strategy and passed-in overrides to the ``Factory._generate`` method.

.. note:: According to the project road map, a future version will use a ``Factory._generate_batch`` at its core instead.

A factory's ``Factory._generate`` function actually delegates to a ``StepBuilder()`` object.
This object will carry the overall "build an object" context (strategy, depth, and possibly other).


Instantiating, Step 2: Preparing values
---------------------------------------

1. The ``StepBuilder`` merges overrides with the class-level declarations
2. The sequence counter for this instance is initialized
3. A ``Resolver`` is set up with all those declarations, and parses them in order;
   it will call each value's ``evaluate()`` method, including extra parameters.
4. If needed, the ``Resolver`` might recurse (through the ``StepBuilder``, e.g when
   encountering a :class:`SubFactory`.


Instantiating, Step 3: Building the object
------------------------------------------

1. The ``StepBuilder`` fetches the attributes computed by the ``Resolver``.
2. It applies renaming/adjustment rules
3. It passes them to the ``FactoryOptions.instantiate`` method, which
   forwards to the proper methods.
4. Post-declaration are applied (in declaration order)


.. note:: This document discusses implementation details; there is no guarantee that the
          described methods names and signatures will be kept as is.
