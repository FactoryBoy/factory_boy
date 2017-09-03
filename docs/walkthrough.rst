Guide
=====

.. currentmodule:: guide

factory_boy holds a wide array of features, which can be combined into complex descriptions and definitions.
This section will build a set of factories increasingly powerful, built onto those features.

We'll run our examples around an imagined library management system: books, readers, etc.

Step 1: factories for a single model
------------------------------------

Let's start with authors; our data model could be the following:

.. literalinclude:: ../examples/guide.py
    :pyobject: Author


A first factory
"""""""""""""""

In order to have realistic random data, we'll start with the following factory:

.. literalinclude:: ../examples/guide.py
    :pyobject: BasicAuthorFactory


Let's walk through the definitions:

* ``death = None``: each author will be considered alive.
* ``main_language = 'en'``: Use the ``'en'`` language code for each other; simpler to begin with.
* `fullname = factory.Faker('name') <factory.Faker>`_ will use a randomly yet human-looking name for every author
* `birthdate = factory.FuzzyDate(...) <factory.fuzzy.FuzzyDate>`_: For every author,
  use a random date between 1 AD and 20 years ago (we'll assume
  that most authors are older than 20 years old; and Python's built-in ``date`` type won't handle date before 1 AD).


If we create a few objects with this:


.. code-block:: pycon

    >>> BasicAuthorFactory()
    Vincent Foster (1000-10-12 - ) [en]

    >>> BasicAuthorFactory()
    Christian Cole (1751-09-14 - ) [en]

    # We want more!
    >>> BasicAuthorFactory.create_batch(10)
    [
     <Author: Sabrina Hicks (0996-05-21 - ) [en]>,
     <Author: Jennifer Guzman (0004-09-05 - ) [en]>,
     <Author: Renee Wiley (1436-07-26 - ) [en]>,
     <Author: Paul Morton (0777-12-08 - ) [en]>,
     <Author: Brianna Williams (0458-03-30 - ) [en]>,
     <Author: Carla Smith (1322-03-04 - ) [en]>,
     <Author: Darrell House (0940-12-27 - ) [en]>,
     <Author: Cody Collier (0762-09-08 - ) [en]>,
     <Author: James Bishop MD (0329-12-24 - ) [en]>,
     <Author: George Moore (0551-03-29 - ) [en]>,
    ]


This looks good! However, there are a few issues:

* Some authors are rather old
* Everyone has the same languege


Improving the ``AuthorFactory`` (lazy_attribute)
""""""""""""""""""""""""""""""""""""""""""""""""

Let's start with preventing immortality: we'll decide that no author should live more than 100 years.

.. literalinclude:: ../examples/guide.py
    :pyobject: MortalAuthorFactory

Here, we use a :meth:`factory.lazy_attribute`-decorated function to compute our custom death date.

.. note:: Note how we :ref:`inherit <intro-inheritance>` from the :class:`BasicAuthorFactory` class
          for increased readability; this is a simple yet powerful technique when designing factories.

Let's see this in action:

.. code-block:: pycon

    >>> MortalAuthorFactory()
    <Author: Daniel Kelley (1724-02-17 - 1824-01-24) [en]>
    >>> MortalAuthorFactory()
    <Author: Laura Howard (0098-01-18 - 0197-12-25) [en]>

    >>> MortalAuthorFactory()
    <Author: William Nelson (1964-11-07 - ) [en]>


Better!
However, we'll quickly notice that all our authors die around age 100; this is quite unrealistic...

We could alter our ``death()`` function to use a random age;
however, our library has a special "They Died too Young" section, which we'll need to test.

Using :class:`class Params <parameters>` for easier tuning
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

We'd like to be able to write the following test:

.. code-block:: python

    young = AuthorFactory(death_age=24)
    old = AuthorFactory(death_age=40)
    self.assertEqual([young], died_too_young_authors())


Let's get to work:

.. literalinclude:: ../examples/guide.py
    :pyobject: UnluckyAuthorFactory

Note the ``class Params`` section: this section of the factory can hold any valid declarations;
they will be available to each other declarations as if they were part of the main class body.

However, they will be removed from the kwargs passed to the instance creation function.

Our database has more variety:

.. code-block:: pycon

    >>> UnluckyAuthorFactory()
    <Author: Hailey Lee (1386-03-15 - 1442-04-27) [en]>
    >>> UnluckyAuthorFactory()
    <Author: Linda Bullock (1986-01-11 - ) [en]>,


We can even force an author's death age:

.. code-block:: pycon

    >>> UnluckyAuthorFactory(death_age=42)
    <Author: Amy Roberts (1003-08-02 - 1045-09-02) [en]>


.. note:: Within our ``death()`` function, we can read ``self.death_age`` even if this field
          will never be defined on the final object; within most factory-decorated functions,
          ``self`` refers to a fake stub (neither an instance of the factory class nor from the target model),
          where all fields from the factory declaration can be freely accesses.


Step 2: Handling connected models
---------------------------------

We now have the tools to build simple objects; but most projects will require more complex,
inter-connected models.

For instance, a library without books would be quite useless; let's fill it.

Linking models: :class:`~factory.SubFactory`
""""""""""""""""""""""""""""""""""""""""""""

Our model is rather simple: a title and summary, an author, publication date, and language:

.. literalinclude:: ../examples/guide.py
    :pyobject: Book


For the title and summary, :class:`~factory.Faker` provides great helpers.

Handling ``Author`` is more complex: we need to provide a proper object.
We'll reuse our ``UnluckyAuthorFactory`` with a :class:`~factory.SubFactory`:

.. literalinclude:: ../examples/guide.py
    :pyobject: BasicBookFactory


Now, whenever we create a ``Book`` with a ``BasicBookFactory``, factory_boy will first
use the ``UnluckyAuthorFactory`` to create an author; and pass it as ``author=`` to our
``Book`` constructor:

.. code-block:: pycon

    >>> BasicBookFactory()
    <Book: "Versatile reciprocal core" by Brett Dean (pub. 1983-04-29)>
    >>> BasicBookFactory()
    <Book: "Secured methodical superstructure" by Nancy Bryan (pub. 1843-02-18)>

    >>> _.author
    <Author: Nancy Bryan (1272-04-03 - 1340-05-25) [en]>


Improving inter-model consistency
"""""""""""""""""""""""""""""""""

Those books have a slight issue: most publication dates fall outside the author's life - so many fakes!

Let's make sure they were written when the author was alive, and at least 15.
For this, we'll need to force the publication date to happen between "birthdate + 15 years" and "deathdate or today":

.. literalinclude:: ../examples/guide.py
    :pyobject: AuthenticBookFactory

The two parameters ``min_publication_date`` and ``max_publication_date`` make our
intent clearer, and allow users of this factory to choose more precisely their target publication date.

The actual publication_date is computed from those two fields, through a :class:`~factory.LazyResolver`:
this declaration can be seen as:

.. code-block:: python

    # Note: this is pseudo-code for the actual factory resolution algorithm.

    # First, resolve min_publication_date / max_publication_date:
    min_date = min_publication_date.evaluate(**context)
    max_date = max_publication_date.evaluate(**context)

    # Then, use them to prepare and compute the publication_date declaration:
    pub_date_declaration = factory.fuzzy.FuzzyDate(start_date=min_date, end_date=max_date)
    pub_date = pub_date_declaration.evaluate(**context)

    # Finally, product the actual object
    Book.objects.create(publication_date=pub_date)


.. note:: 

    * :class:`~factory.SelfAttribute` will simply copy the value of another field
      within the factory, following a dotted path (use multiple dots to read fields
      from ancestors in a :class:`~factory.SubFactory` chain)
    * Within a :class:`~factory.LazyResolver` or a :class:`~factory.SubFactory`,
      a :class:`~factory.SelfAttribute` will be anchored to the *inside* of that
      declaration; go "up" a level to read fields from the containing factory.

We now have books written when the author was alive, and not too young:

.. code-block:: pycon

    >>> AuthenticBookFactory()
    <Book: "Business-focused even-keeled productivity" by Lauren Ball (pub. 1201-07-30)>
    >>> _.author
    <Author: Lauren Ball (1129-12-20 - 1227-03-03) [en]>


If we assemble the features of both models, all data is kept coherent; for instance,
forcing the death age at 18 will generate a book written when the author was aged 15 to 18.

.. code-block:: pycon

    >>> AuthenticBookFactory(author__death_age=18)
    <Book: "Synergistic multi-tasking hierarchy" by Scott Elliott (pub. 1074-08-25)>
    >>> _.author
    <Author: Scott Elliott (1056-09-12 - 1074-09-26) [en]>


Step 3: Related objects
-----------------------

We can now build our library's catalog; let's fill its inventory with various
copies of our books:

.. literalinclude:: ../examples/guide.py
    :pyobject: Copy

Its associated factory holds nothing fancy; we'll use a :class:`~factory.Sequence` declaration
to provide a different, unique ``material_number`` to each copy.

.. literalinclude:: ../examples/guide.py
    :pyobject: CopyFactory


.. note:: As shown here, a :class:`~factory.fuzzy.FuzzyChoice` declaration can
          be used to choose an arbitrary value among a set of options.


Obviously, we should have at least one copy of each book of our catalog;
we could change every call to our ``AuthenticBookFactory``:

.. code-block:: python

    def test_something(self):
        book = factories.AuthenticBookFactory()
        # <<<< Added
        factories.CopyFactory(book=book)
        # <<<< End addition

But that would be long and tedious; what we want is for our ``AuthenticBookFactory`` to
always create a ``Copy`` with the book.


Introducing :class:`~factory.RelatedFactory`
""""""""""""""""""""""""""""""""""""""""""""

The simplest way to handle this is to use a :class:`~factory.RelatedFactory`:

.. literalinclude:: ../examples/guide.py
    :pyobject: PhysicalBookFactory

A :class:`~factory.RelatedFactory` is used to build another object *after the current
one*; here, we'll create a ``Copy`` pointing to the created ``Book`` once the ``Book``
has been created.

A :class:`~factory.SubFactory` wouldn't work, since the relation is from a ``Copy``
*pointing to* a ``Book``.

Let's see it in action:

.. code-block:: pycon

    >>> PhysicalBookFactory()
    <Book: "Quality-focused eco-centric moratorium" by Mark Wade (pub. 0815-07-09)>
    >>> _.copy_set
    [<Copy: "Quality-focused eco-centric moratorium" by Mark Wade [#2, Used]>]

.. note::

    The :class:`~factory.RelatedFactory` declaration takes two positional arguments:

    * The target factory class
    * The field of that factory that should be replaced with the just-created object.

    It might also take optional keyword arguments which would override the target factory's
    declarations.


Customizing related object creation
"""""""""""""""""""""""""""""""""""

The head librarian looked at our latest demo, and was quite upset at seeing
non-pristine copies in our inventory! Our library should always have at least
one pristine copy of each book.

We could simply override our copy's condition when calling the :class:`~RelatedFactory`:

.. literalinclude:: ../examples/guide.py
    :pyobject: IndestructibleBookFactory

And get the expected result:

.. code-block:: pycon

    >>> IndestructibleBookFactory()
    <Book: "Switchable explicit algorithm" by Julie Cunningham (pub. 0285-10-11)>
    >>> _.copy_set
    [<Copy: "Switchable explicit algorithm" by Julie Cunningham [#0, Pristine]>]

.. note::

    We could also simply add an override in our factory subclass, just like we'd
    do when using a :class:`~factory.SubFactory`:

    .. literalinclude:: ../examples/guide.py
        :pyobject: UltraSolidBookFactory

    .. code-block:: pycon

        >>> UltraSolidBookFactory()
        <Book: "Public-key impactful infrastructure" by Patrick Taylor (pub. 1341-05-30)>
        >>> _.copy_set
        [<Copy: "Public-key impactful infrastructure" by Patrick Taylor [#8, Pristine]>]


However, that setup would mean that each copy is pristine (unless declared
otherwise when building it).


Advanced post-generation customization with :class:`~factory.post_generation`
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Let's improve on our ``PhysicalBook`` factory: if the randomly generated copy
wasn't pristine, we'll generate a few more and add a pristine one if needed.

We'll need some custom code for this; it should run after the ``Book`` and
its initial copy have been generated.

We will use a :func:`~factory.post_generation` hook for that task:

.. literalinclude:: ../examples/guide.py
    :pyobject: MultiConditionBookFactory

.. code-block:: pycon

    >>> MultiConditionBookFactory()
    <Book: "Devolved systematic budgetary management" by Mary Jordan (pub. 0140-12-18)>
    >>> _.copy_set
    [<Copy: "Devolved systematic budgetary management" by Mary Jordan [#0, Used]>,
     <Copy: "Devolved systematic budgetary management" by Mary Jordan [#1, Damaged]>,
     <Copy: "Devolved systematic budgetary management" by Mary Jordan [#2, Used]>,
     <Copy: "Devolved systematic budgetary management" by Mary Jordan [#3, Light wear]>,
     <Copy: "Devolved systematic budgetary management" by Mary Jordan [#4, Damaged]>,
     <Copy: "Devolved systematic budgetary management" by Mary Jordan [#5, Pristine]>]

All is fine: we get a few copies, including a ``Pristine`` one!


.. TODO Speak of a more random set of copies, at least one, etc.


.. note::

    The ``create``, ``override`` and ``extra`` arguments to
    :func:`~factory.post_generation` may be used for advanced features, which
    are outside the scope of this section.


Once our library has been filled with books, some loans would be in order.

For this, we'll use a simple data representation:

.. literalinclude:: ../examples/guide.py
    :pyobject: Patron

.. literalinclude:: ../examples/guide.py
    :pyobject: Loan


Using 
